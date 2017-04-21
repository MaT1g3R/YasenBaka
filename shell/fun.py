"""Commands for fun"""
import random
from os.path import join

from discord.ext import commands

import core.fun_core as fun_core
from core.helpers import safebooru


class Fun:
    """Commands for fun"""

    def __init__(self, bot):
        self.bot = bot
        self.data = self.bot.data

    @commands.command()
    async def kyubey(self):
        """Madoka is best anime ever"""
        await self.bot.say('／人◕ ‿‿ ◕人＼')

    @commands.command()
    async def roll(self, dice: str):
        """Rolls a dice in NdN format."""
        await self.bot.say(fun_core.generate_dice_rolls(dice))

    @commands.command()
    async def choose(self, *choices: str):
        """Chooses between multiple choices."""
        await self.bot.say(random.choice(choices))

    @commands.command()
    async def salt(self, prob: str, tries: int):
        """ chance of an event happeneing """
        prob = fun_core.event_probability(prob, tries)
        await self.bot.say('about {}% of happeneing'.format(prob * 100))

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
        file, is_file = fun_core.random_kanna(self.data.kanna_files)
        if is_file:
            await self.bot.send_file(ctx.message.channel, file)
        else:
            await self.bot.say(file)

    @commands.command()
    async def umi(self):
        """
        Umi is love
        :return: None
        """
        await self.bot.say(random.choice(safebooru('sonoda_umi')))

    @commands.command(pass_context=True)
    async def chensaw(self, ctx):
        """Display a chensaw gif"""
        await self.bot.send_file(
            ctx.message.channel, join('data', 'chensaw.gif'))

    @commands.command(pass_context=True)
    async def ayaya(self, ctx):
        """Ayaya!"""
        await self.bot.send_file(ctx.message.channel, join('data', 'ayaya.png'))

    @commands.command()
    async def lewd(self):
        """Display lewd reaction face"""
        await self.bot.say(random.choice(self.data.lewds))

    @commands.command()
    async def steamymeme(self):
        await self.bot.say(random.choice(
            ['http://puu.sh/uvS7R/edce92064d.mp4',
             'http://puu.sh/uvSOB/7e0ec82720.mp4']))

    @commands.command()
    async def cspost(self):
        await self.bot.say(fun_core.cspost_meme())

    @commands.command()
    async def underforest(self):
        await self.bot.say("Forest is love")

    @commands.command()
    async def place(self, arg=None):
        await self.bot.say(fun_core.place_url(arg == 'clean'))

    @commands.command()
    async def joke(self):
        await self.bot.say('https://www.youtube.com/watch?v=THrCQ1ftuTU')
