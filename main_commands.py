"""Main commands for this bot"""
import discord
from discord.ext import commands
import random
from google import search
import html2text
import textwrap
import stackexchange
from os import listdir
from os.path import isfile, join
import json


class Commands:
    """ Main commands """
    def __init__(self, bot, stack_api):
        self.kanna_files = read_kana_files()
        self.bot = bot
        self.so = stackexchange.Site(stackexchange.StackOverflow, stack_api, impose_throttling=True)
        with open('help.json', 'r') as help_:
            self.help_message = json.load(help_)

    @commands.command()
    async def help(self, input_: str = 'Default'):
        """Help messages"""
        await self.bot.say(self.help_message[input_])

    @commands.command()
    async def roll(self, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await self.bot.say('Format has to be in NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for _ in range(rolls))
        await self.bot.say(result)

    @commands.command()
    async def choose(self,  *choices: str):
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

    @commands.command()
    async def anime(self,  *input_: str):
        """
        search MAL for anime
        """

        name = '+'.join(input_) + ' site:https://myanimelist.net'
        for url in search(name, stop=20):
            if 'https://myanimelist.net/anime' in url:
                await self.bot.say(url)
                break

    @commands.command()
    async def salt(self,  percentage: str, tries: int):
        """ chance of an event happeneing """
        percentage = float(percentage.replace('%', ''))/100 if '%' in percentage else float(percentage)
        res = round((1 - (1 - percentage)**tries)*100, 2)
        await self.bot.say('about {}% of dropping'.format(res))

    @commands.command(pass_context=True)
    async def avatar(self, ctx, member: discord.Member):
        """ get user avatar """
        if ctx.message.channel.name is not None:
            await self.bot.say('{0.avatar_url}'.format(member))

    @commands.command()
    async def repeat(self, n: int, *message: str):
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
        await self.try_say(answer)

    async def try_say(self, text, i=1):
        """
        Try to say the block of text until the bot succeeds
        :param text: The block of text
        :type text: str | list
        :param i: how many sections the text needs to be split into
        :type i: int
        :return: nothing
        :rtype: None
        """
        try:
            if isinstance(text, list):
                for txt in text:
                    await self.bot.say('```markdown\n'+txt+'```')
            elif isinstance(text, str):
                    await self.bot.say('```markdown\n' + text + '```')
        except Exception:
            i += 1
            await self.try_say(self.split_text(text, i), i)

    def split_text(self, text, i):
        """
        Splits text into a shame_list
        :param text: The text to be splitted
        :type text: str | list
        :param i: the number of sections the text needs to be split into
        :type i: int
        :return: The split up text
        :rtype: list
        """
        if isinstance(text, list):
            text = ''.join(text)
        return textwrap.wrap(text, int(len(text)/i))


def read_kana_files():
    """
    Reads the kanna pictures
    :return: All path of kanna pics
    :rtype: list
    """
    return [join('kanna_is_cute_af//kanna is cute af', f) for
            f in listdir('kanna_is_cute_af//kanna is cute af') if isfile(join('kanna_is_cute_af//kanna is cute af', f))]
