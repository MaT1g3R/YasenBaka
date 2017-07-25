from asyncio import sleep

from discord import FFmpegPCMAudio, PCMVolumeTransformer, VoiceClient
from discord.ext.commands import Context

from music.abstract_source import AbstractSource
from music.music_util import get_file_info


class FileSource(AbstractSource):
    """
    A audio source from a file.
    """
    __slots__ = ('__source', 'title', 'genre', 'artist', 'album', 'length')

    def __init__(self, file_path: str):
        """
        :param file_path: the file path.
        """
        self.__source = PCMVolumeTransformer(FFmpegPCMAudio(file_path))
        finfo = get_file_info(file_path)
        self.title, self.genre, self.artist, self.album, self.length = finfo

    def __str__(self):
        return self.title

    def __del__(self):
        del self.__source

    def detail(self) -> str:
        """
        See `AbstractSource.detail`
        """
        artist = f'\nArtist:\n`{self.artist}`' if self.artist else ''
        album = f'\nAlbum:\n`{self.album}\n`' if self.album else ''
        genre = f'\nGenre:\n`{self.genre}`' if self.genre else ''
        length = f' [{self.length}]' if self.length else ''
        return f'\t{self.title}{length}\n{artist}\n{album}\n{genre}'

    async def play(self, ctx: Context):
        """
        See `AbstractSource.play`
        """
        vc: VoiceClient = ctx.voice_client
        vc.play(
            self.__source,
            after=lambda e: ctx.bot.logger.warn(str(e))
        )
        while True:
            await sleep(5)
            if not vc.is_playing():
                return
