from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen
from core.nsfw_core import get_lewd
from scripts.checks import is_nsfw


class Nsfw:
    """
    Class of Nsfw commands.
    """
    __slots__ = ('bot',)

    def __init__(self, bot: Yasen):
        """
        Init the instance of this class.
        :param bot: the Yasen bot instance.
        """
        self.bot = bot

    def __local_check(self, ctx: Context):
        return is_nsfw(ctx)

    async def __process_lewd(self, ctx: Context, site: str, query: tuple):
        """
        Process a search request.
        :param ctx: the discord context.
        :param site: the site name.
        :param query: the search queries in a tuple.
        """
        if site == 'danbooru' and len(query) > 2:
            return ('Sorry, you can only enter up to two '
                    'Danbooru tags at the same time')
        msg, url, tags = await get_lewd(
            self.bot.session_manager, site, query,
            self.bot.data_manager, *self.bot.config.danbooru
        )
        if msg:
            await ctx.send(msg)
        if url:
            await ctx.send(url)
        if tags:
            self.bot.data_manager.set_nsfw_tags(site, tags)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def danbooru(self, ctx: Context, *query):
        """
        Description: Search danbooru for lewds.
        Usage: "`{prefix}danbooru up_to two_tags` if no tags given this will
        search for a random image."
        Restrictions: |
            Can only be used in DM or a channel with a name that is equal to or
            starts with `nsfw` (case insensitive)

            Only accepts up to 2 tags.
        Cooldown: Once every 5 seconds per user.
        """
        await self.__process_lewd(ctx, 'danbooru', query)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def gelbooru(self, ctx: Context, *query):
        """
        Description: Search gelbooru for lewds.
        Usage: "`{prefix}gelbooru your tags` if no tags given this will
        search for a random image."
        Restrictions: "Can only be used in DM or a channel with a name that is
        equal to or starts with `nsfw` (case insensitive)"
        Cooldown: Once every 5 seconds per user.
        """
        await self.__process_lewd(ctx, 'gelbooru', query)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def konachan(self, ctx: Context, *query):
        """
        Description: Search konachan for lewds.
        Usage: "`{prefix}konachan your tags` if no tags given this will
        search for a random image."
        Restrictions: "Can only be used in DM or a channel with a name that is
        equal to or starts with `nsfw` (case insensitive)"
        Cooldown: Once every 5 seconds per user.
        """
        await self.__process_lewd(ctx, 'konachan', query)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def yandere(self, ctx: Context, *query):
        """
        Description: Search yandere for lewds.
        Usage: "`{prefix}yandere your tags` if no tags given this will
        search for a random image."
        Restrictions: "Can only be used in DM or a channel with a name that is
        equal to or starts with `nsfw` (case insensitive)"
        Cooldown: Once every 5 seconds per user.
        """
        await self.__process_lewd(ctx, 'yandere', query)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def e621(self, ctx: Context, *query):
        """
        Description: Search e621 for lewds.
        Usage: "`{prefix}e621 your tags` if no tags given this will
        search for a random image."
        Restrictions: "Can only be used in DM or a channel with a name that is
        equal to or starts with `nsfw` (case insensitive)"
        Cooldown: Once every 5 seconds per user.
        """
        await self.__process_lewd(ctx, 'e621', query)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def rule34(self, ctx: Context, *query):
        """
        Description: Search rule34 for lewds.
        Usage: "`{prefix}rule34 your tags` if no tags given this will
        search for a random image."
        Restrictions: "Can only be used in DM or a channel with a name that is
        equal to or starts with `nsfw` (case insensitive)"
        Cooldown: Once every 5 seconds per user.
        """
        await self.__process_lewd(ctx, 'rule34', query)
