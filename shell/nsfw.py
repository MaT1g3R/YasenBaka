"""
Cog for NSFW commands
"""
from discord.ext import commands
from core.nsfw_core import is_nsfw, danbooru


class Nsfw:
    """
    You horny mother fuckers
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(is_nsfw)
    async def danbooru(self, *query: str):
        await self.bot.say(danbooru(query, self.bot.data.danbooru))

