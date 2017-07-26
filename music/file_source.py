from discord import FFmpegPCMAudio, PCMVolumeTransformer

from music.abstract_source import AbstractSource
from music.music_util import get_file_info


class FileSource(AbstractSource):
    """
    A audio source from a file.
    """
    __slots__ = ()

    def __init__(self, file_path: str, opts: dict):
        """
        :param file_path: the file path.
        :param opts: the ffmpeg kwargs.
        """
        title, genre, artist, album, length = get_file_info(file_path)
        super().__init__(
            PCMVolumeTransformer(FFmpegPCMAudio(file_path, **opts)),
            title,
            self.__get_detail(title, genre, artist, album, length)
        )

    @staticmethod
    def __get_detail(title, genre, artist, album, length) -> str:
        """
        See `AbstractSource.detail`
        """
        artist = f'\nArtist:\n`{artist}`' if artist else ''
        album = f'\nAlbum:\n`{album}\n`' if album else ''
        genre = f'\nGenre:\n`{genre}`' if genre else ''
        length = f' [{length}]' if length else ''
        return (f'\t{title}{length}\n{artist}'
                f'\n{album}\n{genre}')
