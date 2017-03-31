"""Utility commands"""
import discord
from discord.ext import commands
from google import search
import html2text
from os.path import join
import stackexchange
from helpers import read_json, generate_latex_online, try_say, get_server_id, is_admin, convert_currency, fopen_generic
import time


class Util:
    """Utility commands"""

    def __init__(self, bot, stack_api):
        self.bot = bot
        self.so = stackexchange.Site(stackexchange.StackOverflow, stack_api, impose_throttling=True)
        self.help_message = read_json(fopen_generic(join('data', 'help.json')))

    @commands.command()
    async def help(self, input_: str = 'Default'):
        """Help messages"""
        music = ', '.join(sorted(self.help_message['music']))
        fun = ', '.join(sorted(self.help_message['fun']))
        util = ', '.join(sorted(self.help_message['util']))
        wows = ', '.join(sorted(self.help_message['wows']))
        sheet = ', '.join(self.help_message['ssheet'])

        if input_ == 'Default':
            await self.bot.say('Command List:\nUtility:```{}```Fun:```{}```Music:```{}```'
                               'World of Warships:```{}```WoWs match spreadsheet:```{}```'.
                               format(util, fun, music, wows, sheet)
                               + '?help [command] for more info on that command, such as `?help play`')
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
            members = [member for member in ctx.message.server.members if member.id in lazy_bums]
            ex_list = []
            for member in members:
                try:
                    await self.bot.send_message(member, ' '.join(message))
                except Exception:
                    ex_list.append(member.name)
            if ex_list:
                await self.bot.say('The pm could not be sent to the following users: {}'.format(', '.join(ex_list)))
            await self.bot.say("Mass pm success!")

    @commands.command(pass_context=True)
    async def latex(self, ctx, *input_: str):
        """Renders the input LaTeX equation"""
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

    @commands.command()
    async def info(self):
        res = "Developed and maintained by <@99271746347110400> using the discord.py api. If you have any feature " \
              "requests or bug reports please pm them to me.\n" \
              "Invite the bot to your server using this link: " \
              "<https://discordapp.com/oauth2/authorize?client_id=243230010532560896&scope=bot&permissions=-1>\n" \
              "Source code: <https://github.com/MaT1g3R/YasenBaka>"

        await self.bot.say(res)

    @commands.command()
    async def ping(self):
        start_time = int(round(time.time() * 1000))
        msg = await self.bot.say('Pong! :hourglass:')
        end_time = int(round(time.time() * 1000))
        await self.bot.edit_message(msg, 'Pong! | :timer: {}ms'.format(end_time - start_time))

    @commands.command(pass_context=True)
    async def bash(self, ctx):
        if str(ctx.message.author.id) == "99271746347110400":
            await self.bot.say(ctx.message.author.id)
