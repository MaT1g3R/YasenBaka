from pathlib import Path
from typing import List

from discord import File
from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen
from core.nsfw_core import get_lewd
from core.weeb_core import random_picture, wolke_image
from data import data_path


class Weeb:
    """
    Class to hold weeb commands.
    """
    __slots__ = ('bot', 'kanna_files', 'karen_files')

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
        Description: Display a random Kanna image.
        Usage: "`{prefix}kanna`"
        """
        await self.__random_img(ctx, self.kanna_files, ('kanna_kamui',))

    @commands.command()
    async def karen(self, ctx: Context):
        """
        Description: Display a random Karen image.
        Usage: "`{prefix}karen`"
        """
        await self.__random_img(ctx, self.karen_files, ('kujou_karen',))

    @commands.command()
    async def umi(self, ctx: Context):
        """
        Description: Display a random Umi image.
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
        res = await wolke_image(
            self.bot.session_manager, self.bot.config.wolke_api, 'lewd')
        await ctx.send(res)

    @commands.command()
    async def chensaw(self, ctx: Context):
        """
        Description: Display a chensaw gif.
        Usage: "`{prefix}chensaw`"
        """
        await ctx.send(file=File(str(data_path.joinpath('chensaw.gif'))))

    @commands.command()
    async def joke(self, ctx):
        """
        Description: Is Joke!
        Usage: "`{prefix}joke`"
        """
        await ctx.send('https://www.youtube.com/watch?v=THrCQ1ftuTU')

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def safebooru(self, ctx: Context, *query):
        """
        Description: Search safebooru for a picture.
        Usage: "`{prefix}safebooru your tags` if no tags given this will
        search for a random image."
        Cooldown: Once every 5 seconds per user.
        """
        msg, url, tags = await get_lewd(
            self.bot.session_manager, 'safebooru', query,
            self.bot.data_manager, *self.bot.config.danbooru
        )
        if msg:
            await ctx.send(msg)
        if url:
            await ctx.send(url)
        if tags:
            self.bot.data_manager.set_nsfw_tags('safebooru', tags)

    @commands.command()
    async def anime(self, ctx, *, search=None):
        """
        Description: Search for an anime.
        Usage: "`{prefix}anime Saenai Heroine no Sodatekata`"
        """
        await ctx.send('Coming soon')

    @commands.command()
    async def manga(self, ctx, *, search=None):
        """
        Description: Search for a manga.
        Usage: "`{prefix}manga Kami nomi zo Shiru Sekai`"
        """
        await ctx.send('Coming soon')

    @commands.command(name='LN')
    async def _light_novel(self, ctx, *, search=None):
        """
        Description: Search for a light novel.
        Usage: "`{prefix}LN Overlord`"
        """
        await ctx.send('Coming soon')
