"""Utility commands"""
import discord
from discord.ext import commands
from google import search
import html2text
from os.path import join
import stackexchange
from helpers import read_json, generate_latex_online, try_say, get_server_id, \
    is_admin, convert_currency, fopen_generic, get_distro
import time
import subprocess
import resource
import math
import sys
from discord.errors import Forbidden


class Util:
    """Utility commands"""
    def __init__(self, bot, stack_api):
        self.start_time = time.time()
        self.bot = bot
        self.so = stackexchange.Site(stackexchange.StackOverflow, stack_api,
                                     impose_throttling=True)
        self.help_message = read_json(fopen_generic(join('data', 'help.json')))

    def get_uptime(self):
        time_elapsed = int(time.time() - self.start_time)
        hours = math.floor(time_elapsed/(60*60))  # How the fuck do i math
        time_elapsed -= hours*3600
        minutes = math.floor(time_elapsed/60)
        time_elapsed -= minutes*60
        minutes_str = str(minutes) if minutes >= 10 else '0' + str(minutes)
        seconds_str = str(time_elapsed) if time_elapsed >= 10 \
            else '0' + str(time_elapsed)
        return '{}:{}:{}'.format(str(hours), minutes_str, seconds_str)

    @commands.command()
    async def help(self, input_: str = 'Default'):
        """Help messages"""
        music = ', '.join(sorted(self.help_message['music']))
        fun = ', '.join(sorted(self.help_message['fun']))
        util = ', '.join(sorted(self.help_message['util']))
        wows = ', '.join(sorted(self.help_message['wows']))
        sheet = ', '.join(self.help_message['ssheet'])

        if input_ == 'Default':
            await self.bot.say('Command List:\nUtility:```{}```Fun:```{}'
                               '```Music:```{}```'
                               'World of Warships:```{}'
                               '```WoWs match spreadsheet:```{}```'.
                               format(util, fun, music, wows, sheet)
                               + '?help [command] for more info'
                                 ' on that command, such as `?help play`')
        elif input_ in self.help_message:
            await self.bot.say(self.help_message[input_])

    @commands.command(pass_context=True)
    async def pmall(self, ctx, *args):
        server_id = get_server_id(ctx)
        if server_id is None or not is_admin(ctx, ctx.message.author.id):
            await self.bot.say("Cannot use this command, not admin")
        else:
            message = []
            lazy_bums = []
            for s in args:
                if s.startswith('<@!') and s.endswith('>'):
                    lazy_bums.append(s[3:-1])
                elif s.startswith('<@') and s.endswith('>'):
                    lazy_bums.append(s[2:-1])
                else:
                    message.append(s)
            members = [member for member in ctx.message.server.members
                       if member.id in lazy_bums]
            ex_list = []
            for member in members:
                try:
                    await self.bot.send_message(member, ' '.join(message))
                except Forbidden:
                    ex_list.append(member.name)
            if ex_list:
                await self.bot.say(
                    'The pm could not be sent to the following users:'
                    ' {}'.format(', '.join(ex_list)))
            await self.bot.say("Mass pm success!")

    @commands.command(pass_context=True)
    async def latex(self, ctx, *input_: str):
        """Renders the input LaTeX equation"""
        if len(input_) <= 0:
            await self.bot.say("Please enter a valid input.")
            return
        l = " ".join(input_)
        fn = generate_latex_online(l)
        await self.bot.send_file(ctx.message.channel, fn)

    @commands.command(pass_context=True)
    async def joined(self, ctx, member: discord.Member):
        """Says when a member joined."""
        if ctx.message.channel.name is not None:
            res = ('{0.name} joined in {0.joined_at}'.format(member))
            res = res.split(' ')
            res.pop()
            res = ' '.join(res)
            await self.bot.say(res)

    @commands.command()
    async def anime(self, *input_: str):
        """
        search MAL for anime
        """
        name = '+'.join(input_) + ' site:https://myanimelist.net'
        for url in search(name, stop=20):
            if 'https://myanimelist.net/anime' in url:
                await self.bot.say(url)
                break

    @commands.command(pass_context=True)
    async def avatar(self, ctx, member: discord.Member):
        """ get user avatar """
        if ctx.message.channel.name is not None:
            await self.bot.say('{0.avatar_url}'.format(member))

    @commands.command()
    async def stackoverflow(self, *question: str):
        """I do not take responsibility for damage caused"""
        self.so.be_inclusive()

        q = '+'.join(question) + ' site:stackoverflow.com'
        q_url = ''
        for url in search(q, stop=2):
            if 'stackoverflow.com/questions/' in url:
                q_url = url
                break
        if q_url == '':
            await self.bot.say('Cannot find answer')
            return

        start_index = q_url.find('questions') + 10
        finish_index = q_url[start_index:].find('/') + start_index
        question_id = int(q_url[start_index:finish_index])

        question = self.so.question(question_id)
        answer = html2text.html2text(question.answers[0].body)
        await try_say(self.bot, answer)

    @commands.command()
    async def currency(self, base: str, target: str, amount: str):
        """converts currency"""
        try:
            amount_str = amount
            amount = float(amount)
            base = base.upper()
            target = target.upper()
        except ValueError:
            await self.bot.say('Please enter a valid amount')
            return

        try:
            money = convert_currency(base, amount, target)
            await self.bot.say(amount_str + base + ' = ' + money + target)
        except KeyError:
            await self.bot.say('Please enter valid currency codes!')

    @commands.command(pass_context=True)
    async def info(self, ctx):
        server_count = 0
        user_count = 0
        text_channel_count = 0
        voice_count = 0
        for _ in self.bot.servers:
            server_count += 1
        for _ in self.bot.get_all_members():
            user_count += 1
        for channel in self.bot.get_all_channels():
            if channel.type == discord.ChannelType.text:
                text_channel_count += 1
        for _ in self.bot.voice_clients:
            voice_count += 1
        res = discord.Embed(colour=0x4286f4)
        res.set_author(name=self.bot.user.name,
                       icon_url='{0.avatar_url}'.format(self.bot.user))
        ram = "{0:.2f}".format(
            float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024))
        res.add_field(name='RAM used', value=str(ram) + 'MB')
        res.add_field(name='Uptime', value=self.get_uptime())
        res.add_field(name='Python version', value=sys.version[:5])
        lib_ver = discord.version_info
        res.add_field(name='Library', value='Discord.py v{}.{}.{}'
                      .format(lib_ver.major, lib_ver.minor, lib_ver.micro))
        res.add_field(name='System', value=' '
                      .join([str.title(str(x)) for x in get_distro()]))
        res.add_field(name='Developers',
                      value='ラブアローシュート#6728\nNaomi#3264')
        res.add_field(name='Servers', value=str(server_count))
        res.add_field(name='Users', value=str(user_count))
        res.add_field(name='Text channels', value=str(text_channel_count))
        res.add_field(name='Voice channels', value=str(voice_count))
        res.add_field(name='Source code and invite link',
                      value='https://github.com/MaT1g3R/YasenBaka',
                      inline=False)
        res.add_field(name='Support server', value='https://discord.gg/BnPbz6q')
        res.set_footer(text='Requested by {}'.format(
            ctx.message.author.display_name + '#' +
            ctx.message.author.discriminator))
        await self.bot.send_message(ctx.message.channel, embed=res)

    @commands.command()
    async def ping(self):
        start_time = int(round(time.time() * 1000))
        msg = await self.bot.say('Pong! :hourglass:')
        end_time = int(round(time.time() * 1000))
        await self.bot.edit_message(
            msg, 'Pong! | :timer: {}ms'.format(end_time - start_time))

    @commands.command(pass_context=True)
    async def bash(self, ctx, *args):
        if str(ctx.message.author.id) \
                in ["99271746347110400", "145735970342305792"]:
            try:
                output = subprocess.check_output(args, stderr=subprocess.STDOUT)
                res_str = output.decode()
                await self.bot.say(
                    ":white_check_mark: Command success!\nOutput:\n"
                    "```{}```".format(res_str))
            except subprocess.CalledProcessError as ex:
                res_str = ex.output.decode()
                await self.bot.say(
                    ":no_entry_sign: Command failed!\nOutput:"
                    "\n```{}```".format(res_str))
        else:
            await self.bot.say('Only my owner can use this command!')

    @commands.command(pass_context=True)
    async def update(self, ctx):
        if str(ctx.message.author.id) \
                in ["99271746347110400", "145735970342305792"]:
            try:
                output = subprocess.check_output(['git', 'pull'],
                                                 stderr=subprocess.STDOUT)
                res_str = output.decode()
                await self.bot.say("```{}```".format(res_str))
                subprocess.call(['pm2', 'restart', '16'])
            except subprocess.CalledProcessError as ex:
                res_str = ex.output.decode()
                await self.bot.say(
                    ":no_entry_sign: Update failed!\n"
                    "Output:\n```{}```".format(res_str))
        else:
            await self.bot.say('Only my owner can use this command!')
