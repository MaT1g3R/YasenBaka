from pathlib import Path
from random import shuffle

from discord import VoiceChannel

from music.abstract_music_player import AbstractMusicPlayer
from music.entry import Entry


class FilePlayer(AbstractMusicPlayer):
    """
    Audio player for playing local files.
    """
    __slots__ = ('default_path',)

    def __init__(self, logger, channel: VoiceChannel, default_path: Path):
        """
        :param logger: a logger object to do logging with.
        :param channel: the `VoiceChannel` to play audio in.
        :param default_path: the path to the playlist directory.
        """
        super().__init__(logger, channel)
        self.default_path = default_path

    async def enqueue(self, ctx, query: str = None):
        """
        Bulk enqueue all files in the default play list directory into
        `self.entry_queue`

        :param ctx: the `discord.Context` object.

        :param query: This isn't used.
        """
        if self.entry_queue:
            return
        files = [str(f) for f in self.default_path.iterdir()]
        shuffle(files)
        self.entry_queue.extend(Entry.from_file(ctx, file) for file in files)
