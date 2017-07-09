from random import choice

from discord import File
from discord.ext import commands
from discord.ext.commands import BucketType, Context

from bot import HTTPStatusError, Yasen
from core.fun_core import generate_dice_rolls, parse_repeat, random_kanna
from core.nsfw_core import get_lewd
from data import data_path


class Fun:
    """
    Class to hold `Fun` commands.
    """

    def __init__(self, bot: Yasen):
        """
        Initialize the instance of this class.
        :param bot: the bot instance.
        """
        self.bot = bot

    @commands.command()
    async def kanna(self, ctx: Context):
        """
        Description: "Display a random Kanna image."
        Usage: "{}kanna"
        """
        res = await random_kanna(
            self.bot.kanna, self.bot.session_manager, self.bot.data_manager)
        await ctx.send(file=res)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def repeat(self, ctx: Context, n=None, *, msg=None):
        """
        Description: "Repeat a message x number of times, where 1 <= x <= 5."
        Usage: "{}repeat 3 my message"
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
    async def umi(self, ctx: Context):
        """
        Description: "Display a random Umi image."
        Usage: "{}umi"
        """
        msg, url, _ = await get_lewd(
            self.bot.session_manager, 'safebooru',
            ('sonoda_umi',), self.bot.data_manager
        )
        if not url:
            await ctx.send(msg)
            return
        try:
            bytes_io = await self.bot.session_manager.bytes_io(url)
        except HTTPStatusError as e:
            await ctx.send(f'Something went wrong with the Safebooru API\n{e}')
        else:
            await ctx.send(file=File(bytes_io))

    @commands.command()
    async def ayaya(self, ctx: Context):
        """
        Description: "Ayaya!"
        Usage: "{}ayaya"
        """
        await ctx.send(file=File(str(data_path.joinpath('ayaya.png'))))

    @commands.command()
    async def lewd(self, ctx: Context):
        """
        Description: "Onii chan no baka, echhi, hentai!"
        Usage: "{}lewd"
        """
        img = await self.bot.api_consumer.wolke_image('lewd')
        if isinstance(img, File):
            await ctx.send(file=img)
        else:
            await ctx.send(img)

    @commands.command()
    async def roll(self, ctx, dice: str = ''):
        """
        Description: "Rolls dice in NdN format."
        Usage: "**{}roll 5d6** This rolls a D6 5 times."
        """
        await ctx.send(generate_dice_rolls(dice.lower()))

    @commands.command()
    async def choose(self, ctx, *choices: str):
        """Description: Chooses between multiple choices."""
        if not choices:
            await ctx.send('Please enter some choices for me to choose from.')
        else:
            await ctx.send(choice(choices))
