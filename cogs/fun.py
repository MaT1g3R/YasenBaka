from discord import File
from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen
from core.fun_core import random_kanna


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
        description: |
            Display a random Kanna image.
        usage: {}kanna
        """
        resp = await self.bot.api_consumer.safebooru(['kanna_kamui'])
        res, file_eh = random_kanna(self.bot.kanna, resp)
        if file_eh:
            await ctx.send(file=File(str(res)))
        else:
            await ctx.send(res)
