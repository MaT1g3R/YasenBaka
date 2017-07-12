from pathlib import Path
from random import choice
from typing import List

from discord import File
from discord.ext import commands
from discord.ext.commands import BucketType, Context

from bot import Yasen
from core.fun_core import generate_dice_rolls, parse_repeat, parse_salt, \
    random_picture
from core.nsfw_core import get_lewd
from data import data_path


class Fun:
    """
    Class to hold `Fun` commands.
    """

    def __init__(self, bot: Yasen,
                 kanna_files: List[Path], karen_files: List[Path]):
        """
        Initialize the instance of this class.
        :param bot: the bot instance.
        """
        self.bot = bot
        self.kanna_files = kanna_files
        self.karen_files = karen_files

    async def __random_img(self, ctx, files, tags):
        res = await random_picture(
            files, tags,
            self.bot.session_manager, self.bot.data_manager
        )
        if isinstance(res, File):
            await ctx.send(file=res)
        else:
            await ctx.send(res)

    @commands.command()
    async def kanna(self, ctx: Context):
        """
        Description: "Display a random Kanna image."
        Usage: "`{prefix}kanna`"
        """
        await self.__random_img(ctx, self.kanna_files, ('kanna_kamui',))

    @commands.command()
    async def karen(self, ctx: Context):
        """
        Description: "Display a random Karen image."
        Usage: "`{prefix}karen`"
        """
        await self.__random_img(ctx, self.karen_files, ('kujou_karen',))

    @commands.command()
    async def umi(self, ctx: Context):
        """
        Description: "Display a random Umi image."
        Usage: "`{prefix}umi`"
        """
        msg, url, _ = await get_lewd(
            self.bot.session_manager, 'safebooru',
            ('sonoda_umi',), self.bot.data_manager
        )
        if not url:
            await ctx.send(msg)
            return
        await ctx.send(url)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def repeat(self, ctx: Context, n=None, *, msg=None):
        """
        Description: "Repeat a message x number of times, where 1 <= x <= 5."
        Usage: "`{prefix}repeat 3 my message`"
        Cooldown: "Once every 5 seconds per user."
        """
        try:
            _n, _msg = parse_repeat(n, msg)
        except ValueError as e:
            await ctx.send(str(e))
        else:
            for _ in range(_n):
                await ctx.send(_msg)

    @commands.command()
    async def ayaya(self, ctx: Context):
        """
        Description: "Ayaya!"
        Usage: "`{prefix}ayaya`"
        """
        await ctx.send(file=File(str(data_path.joinpath('ayaya.png'))))

    @commands.command()
    async def lewd(self, ctx: Context):
        """
        Description: "Onii chan no baka, echhi, hentai!"
        Usage: "`{prefix}lewd`"
        """
        img = await self.bot.api_consumer.wolke_image('lewd')
        await ctx.send(img)

    @commands.command()
    async def roll(self, ctx: Context, dice: str = ''):
        """
        Description: "Rolls dice in NdN format."
        Usage: "`{prefix}roll 5d6` This rolls a D6 5 times."
        """
        await ctx.send(generate_dice_rolls(dice.lower()))

    @commands.command()
    async def choose(self, ctx: Context, *choices: str):
        """
        Description: "Chooses between multiple choices. Choices are separated
        by spaces."
        Usage: "`{prefix}choose 0 1 2 3`"
        """
        if not choices:
            await ctx.send('Please enter some choices for me to choose from.')
        else:
            await ctx.send(choice(choices))

    @commands.command()
    async def salt(self, ctx: Context, num: str = None, prob: str = None):
        """
        Description: "Chance of an event happening given number of trials and
        the probability of the event."
        Usage: "`{prefix}salt 10 0.03` this is the same as
        `{prefix}salt 10 3%`"
        """
        n, p = parse_salt(num, prob)
        if n is None or p is None:
            await ctx.send('Please enter a vaild number of trials and a '
                           'vaild probability (in decimal or percentage)')
        else:
            res = round((1 - (1 - p) ** n), 4)
            await ctx.send(f'{res*100}% chance of happeneing')

    @commands.command()
    async def chensaw(self, ctx: Context):
        """
        Description: "Display a chensaw gif."
        Usage: "`{prefix}chensaw`"
        """
        await ctx.send(file=File(str(data_path.joinpath('chensaw.gif'))))
