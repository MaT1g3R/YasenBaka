from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen
from core.bot_info_core import get_info_embed


class BotInfo:
    def __init__(self, bot: Yasen):
        self.bot = bot

    @commands.command()
    async def info(self, ctx: Context):
        """
        Description: "Displays information about the bot."
        Usage: "{prefix}info"
        """
        await ctx.send(embed=get_info_embed(self.bot))
