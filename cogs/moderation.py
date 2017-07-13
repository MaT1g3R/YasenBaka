from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen


class Moderation:
    """
    Moderation commands.
    """

    def __int__(self, bot: Yasen):
        self.bot = bot

    @commands.command()
    async def pmall(self, ctx: Context, *, args: str = None):
        """

        """
        pass
