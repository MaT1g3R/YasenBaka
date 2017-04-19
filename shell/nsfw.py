"""
Cog for NSFW commands
"""
from discord.ext import commands
from core.nsfw_core import is_nsfw, danbooru, gelbooru, k_or_y


class Nsfw:
    """
    You horny motherfuckers
    """
    def __init__(self, bot):
        self.bot = bot
        self.random = 'You didn\'t specify a search term, here\'s a ' \
                      'random result.'

    @commands.command()
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def danbooru(self, *query: str):
        if len(query) == 0:
            await self.bot.say(self.random)
        await self.bot.say(danbooru(query, self.bot.data.danbooru))

    @commands.command()
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def konachan(self, *query: str):
        if len(query) == 0:
            await self.bot.say(self.random)
        await self.bot.say(k_or_y(query, 'Konachan'))

    @commands.command()
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def yandere(self, *query: str):
        if len(query) == 0:
            await self.bot.say(self.random)
        await self.bot.say(k_or_y(query, 'Yandere'))

    @commands.command()
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def gelbooru(self, *query: str):
        if len(query) == 0:
            await self.bot.say(self.random)
        await self.bot.say(gelbooru(query))
