"""Main commands for this bot"""
import discord
from discord.ext import commands
import random
from google import search
import html2text
import stackexchange
from helpers import read_json, generate_latex_online, try_say, read_kana_files, update_command_blacklist, is_banned, \
    get_server_id, is_admin, convert_currency


class Commands:
    """ Main commands """
    def __init__(self, bot, stack_api):
        self.kanna_files = read_kana_files()
        self.bot = bot
        self.so = stackexchange.Site(stackexchange.StackOverflow, stack_api, impose_throttling=True)
        self.help_message = read_json('data//help.json')

    @commands.command(pass_context=True)
    async def help(self, ctx, input_: str = 'Default'):
        """Help messages"""
        # TODO: Finish this
        pass

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
            await self.bot.say(lazy_bums)
            members = [member for member in ctx.message.server.members if member.id in lazy_bums]
            ex_list = []
            for member in members:
                try:
                    await self.bot.send_message(member, ' '.join(message))
                except Exception:
                    ex_list.append(member.name)
            if not ex_list:
                await self.bot.say('The pm could not be sent to the following users: {}'.format(', '.join(ex_list)))
            await self.bot.say("Mass pm success!")

    @commands.command(pass_context=True)
    async def latex(self, ctx, *input_: str):
        """Renders the input LaTeX equation"""
        l = " ".join(input_)
        fn = generate_latex_online(l)
        await self.bot.send_file(ctx.message.channel, fn)

    @commands.command(pass_context=True)
    async def kyubey(self, ctx):
        """Madoka is best anime ever"""
        await self.bot.say('／人◕ ‿‿ ◕人＼')

    @commands.command(pass_context=True)
    async def roll(self, ctx, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await self.bot.say('Format has to be in NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for _ in range(rolls))
        await self.bot.say(result)

    @commands.command(pass_context=True)
    async def choose(self, ctx, *choices: str):
        """Chooses between multiple choices."""
        await self.bot.say(random.choice(choices))

    @commands.command(pass_context=True)
    async def joined(self, ctx, member: discord.Member):
        """Says when a member joined."""
        if ctx.message.channel.name is not None:
            res = ('{0.name} joined in {0.joined_at}'.format(member))
            res = res.split(' ')
            res.pop()
            res = ' '.join(res)
            await self.bot.say(res)

    @commands.command(pass_context=True)
    async def anime(self, ctx, *input_: str):
        """
        search MAL for anime
        """
        name = '+'.join(input_) + ' site:https://myanimelist.net'
        for url in search(name, stop=20):
            if 'https://myanimelist.net/anime' in url:
                await self.bot.say(url)
                break

    @commands.command(pass_context=True)
    async def salt(self, ctx, percentage: str, tries: int):
        """ chance of an event happeneing """
        percentage = float(percentage.replace('%', ''))/100 if '%' in percentage else float(percentage)
        res = round((1 - (1 - percentage)**tries)*100, 2)
        await self.bot.say('about {}% of dropping'.format(res))

    @commands.command(pass_context=True)
    async def avatar(self, ctx, member: discord.Member):
        """ get user avatar """
        if ctx.message.channel.name is not None:
            await self.bot.say('{0.avatar_url}'.format(member))

    @commands.command(pass_context=True)
    async def repeat(self, ctx, n: int, *message: str):
        """ repeat message n times, n <= 5 """
        if n > 5:
            await self.bot.say("Are you trying to break me?")
            return
        for _ in range(n):
            await self.bot.say(' '.join(message))

    @commands.command(pass_context=True)
    async def kanna(self, ctx):
        """
        Randomly display a kanna image to the channel
        :param ctx: Context
        :type ctx: ctx
        :return: nothing
        :rtype: None
        """
        fn = random.choice(self.kanna_files)
        await self.bot.send_file(ctx.message.channel, fn)

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

        start_index = q_url.find('questions')+10
        finish_index = q_url[start_index:].find('/') + start_index
        question_id = int(q_url[start_index:finish_index])

        question = self.so.question(question_id)
        answer = html2text.html2text(question.answers[0].body)
        await try_say(self.bot, answer)

    @commands.command(pass_context=True)
    async def currency(self, ctx, base: str, target: str, amount: str):
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
            await self.bot.say(amount_str + base + ' in ' + target + ' is ' + money + target)
        except KeyError:
            await self.bot.say('Please enter valid currency codes!')
