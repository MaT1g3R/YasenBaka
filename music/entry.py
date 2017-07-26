from asyncio import get_event_loop
from functools import partial

import youtube_dl
from discord import FFmpegPCMAudio, Member
from discord.ext.commands import Context

from music.abstract_source import AbstractSource
from music.file_source import FileSource
from music.ytdl_source import YTDLSource

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class Entry:
    """
    An object that represents a song entry.
    """
    __slots__ = ('requester', 'source', 'skip_members')

    def __init__(self, requester: Member, source: AbstractSource):
        """
        Init the instance.
        :param requester: the song requester.
        :param source:
        """
        self.requester = requester
        self.source = source
        self.skip_members = set()

    def __str__(self):
        return str(self.source)

    def __del__(self):
        del self.source
        del self.skip_members

    @property
    def detail(self) -> str:
        """
        :return: A detailed string representation for the entry.
        """
        return self.source.detail

    @classmethod
    def from_file(cls, ctx: Context, file: str):
        """
        Get an `Entry` instace from a file path.
        :param ctx: discord `Context` object
        :param file: the file path string.
        :return: `Entry` instance from a file.
        """
        source = FileSource(file, ffmpeg_options)
        return cls(ctx.author, source)

    @classmethod
    async def from_yt(cls, ctx, query):
        """
        Get an `Entry` instace from a youtube-dl search query or url.
        :param ctx: discord `Context` object
        :param query: the search query.
        :return: `Entry` instance from a search query or url.
        """
        loop = get_event_loop()
        func = partial(ytdl.extract_info, query, download=False)
        data = await loop.run_in_executor(None, func)
        if 'entries' in data:
            data = data['entries'][0]
        download_url = data.get('url')
        if not download_url:
            return
        data['requester'] = str(ctx.author)
        filename = ytdl.prepare_filename(data)
        yt = YTDLSource(
            FFmpegPCMAudio(download_url, **ffmpeg_options), filename, data
        )
        return cls(ctx.author, yt)

    async def play(self, ctx):
        """
        Start playing music in the Context.
        :param ctx: discord `Context` object
        """
        await self.source.play(ctx)

    def __calc_skip(self, ctx) -> tuple:
        """
        Calculate the skipping count.
        :param ctx: discord `Context` object
        :return: a tuple of
            (vote count is >= than max vote count, max vote count)
        """
        max_count = ctx.bot.data_mamager.get_skip(str(ctx.guild.id))
        if not isinstance(max_count, int):
            max_count = 3
        return len(self.skip_members) >= max_count, max_count

    def __cur_skip(self, max_c) -> str:
        """
        :param max_c: max skip count.
        :return: String representation of the current skip count.
        """
        current = len(self.skip_members)
        return f'**[{current}/{max_c} Votes]**'

    async def skip(self, ctx: Context) -> bool:
        """
        Skip this entry.
        :param ctx: discord `Context` object
        :return: True if the entry should be skipped.
        """
        if ctx.author == self.requester:
            return True
        skipped, max_c = self.__calc_skip(ctx)
        self.skip_members.add(ctx.author)
        cur = self.__cur_skip(max_c)
        if ctx.author in self.skip_members:
            await ctx.send(f'You already voted to skip this song. {cur}')
        else:
            await ctx.send(f'You voted to skip this song. {cur}')
        return skipped
