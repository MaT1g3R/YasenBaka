from functools import partial

from music.abstract_source import AbstractSource
from music.music_util import file_detail, get_file_info


class FileSource(AbstractSource):
    """
    An audio source from a file.
    """

    __slots__ = ('file_path', 'title')

    def __init__(self, file_path: str):
        """
        :param file_path: the file path.
        """
        self.title, genre, artist, album, length = get_file_info(file_path)
        self.file_path = file_path
        super().__init__(
            partial(file_detail, self.title, genre, artist, album, length)
        )

    def __str__(self):
        return self.title

    def clean_up(self):
        del self.title
        del self.file_path

    async def true_name(self) -> str:
        """
        See `AbstractSource.true_name`
        """
        return self.file_path
