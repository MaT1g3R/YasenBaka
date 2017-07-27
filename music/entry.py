from asyncio import sleep
from typing import NewType, Union

from discord import FFmpegPCMAudio, Member
from discord.ext.commands import Context
from youtube_dl import YoutubeDL

from music.abstract_source import AbstractSource
from music.file_source import FileSource
from music.music_util import fetch_ytdl_info, get_ytdl_format
from music.ytdl_source import YTDLSource

_SourceType = Union[
    NewType('FileSource', AbstractSource),
    NewType('YTDLSource', AbstractSource)
]


class Entry:
    """
    An object that represents a song entry.
    """
    __slots__ = ('requester', 'source', 'skip_members')

    def __init__(self, requester: Member, source: _SourceType):
        """
        Init the instance.
        :param requester: the song requester.
        :param source: An audio source.
            This should be a subclass of `AbstractSource`
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
        return cls(ctx.author, FileSource(file))

    @classmethod
    async def from_yt(cls, ctx: Context, query: str):
        """
        Get an `Entry` instace from a youtube-dl search query or url.
        :param ctx: discord `Context` object
        :param query: the search query.
        :return: `Entry` instance from a search query or url.
        """
        with YoutubeDL(get_ytdl_format(None)) as ydl:
            data = await fetch_ytdl_info(ydl, query)
            if 'entries' in data:
                data = data['entries'][0]
            webpage_url = data.get('webpage_url')
            duration = data.get('duration')
            if not webpage_url or not isinstance(duration, (int, float)):
                return
            need_download = duration <= 1800
            delete_after = duration > 600
            yt = YTDLSource(
                data, str(ctx.author), need_download,
                delete_after, ctx.bot.logger
            )
            return cls(ctx.author, yt)

    async def play(self, ctx):
        """
        Start playing music in the Context.
        :param ctx: discord `Context` object
        """
        vc = ctx.voice_client
        if not vc:
            return
        name = await self.source.true_name()
        src = FFmpegPCMAudio(name, before_options='-nostdin', options='-vn')
        vc.play(
            src,
            after=lambda e: ctx.bot.logger.warn(str(e)) if e else None
        )
        while True:
            if not vc.is_playing():
                return
            await sleep(5)

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
