from asyncio import Queue, wait_for
from pathlib import Path
from random import shuffle
from typing import List, Optional

from discord.ext.commands import Context

from music.entry import Entry
from music.playing_status import PlayingStatus


class MusicPlayer:
    """
    A music player object for a single guild.

    === Attributes ===
    :type default_path: Optional[Path]
        Path that points to the directory containing the default playlist.
    :type default_files: Optional[List[str]]
        A list of file paths in the default playlist directory.
    :type default_queue: asyncio.Queue:
        A queue of `Entry` for music on the local file system.
    :type guild_queue: asyncio.Queue
        A queue of `Entry` for music on the local file system.
    :type playing_status: PlayingStatus
        A value that represents the current playing status.
    :type current: Optional[Entry]
        An `Entry` object that is currently playing.
    """
    __slots__ = ('default_path', 'default_files', 'default_queue',
                 'guild_queue', 'playing_status', 'current', 'logger')

    def __init__(self, logger, default_path: Optional[Path] = None):
        """
        Init the instance.
        :param default_path:
            Path that points to the default playlist dir, optional.
        """
        self.logger = logger
        self.default_path = default_path
        self.default_files = None
        self.default_queue = Queue()
        self.guild_queue = Queue()
        self.playing_status = PlayingStatus.NO
        self.current = None

    def __del__(self):
        self.__del_q(self.default_queue)
        self.__del_q(self.guild_queue)
        del self.guild_queue
        del self.default_queue
        del self.current
        del self.default_files

    def __log_del(self, entry: Entry):
        """
        Log the deletion of an entry.
        :param entry: the entry deleted.
        """
        self.logger.info(f'Deleting entry: {entry}')

    def __del_q(self, q: Queue):
        """
        Delete all entries from a Queue
        :param q: the `Queue` instance.
        """
        while True:
            if q.empty():
                return
            entry = q.get_nowait()
            self.__log_del(entry)
            del entry

    async def play_list_str(self) -> str:
        """
        Get the playlist for the guild as string.
        :return: a string representation of the platlist queued for the guild.
        """
        if self.playing_status == PlayingStatus.FILE:
            q = self.default_queue._queue
        elif self.playing_status == PlayingStatus.WEB:
            q = self.guild_queue._queue
        else:
            return 'Playlist is empty'
        lst_str = '\n'.join((str(entry) for entry in q))
        return f'```\n{lst_str}\n```' if lst_str else 'Playlist is empty'

    def get_files(self) -> Optional[List[str]]:
        """
        Get a list of file paths.
        :return: A list of file paths under `self.default_path` if any.
        """
        if not self.default_path or not self.default_path.is_dir():
            return None
        lst = [str(f) for f in self.default_path.iterdir()]
        shuffle(lst)
        return lst

    async def put_default_entries(self, ctx: Context):
        """
        Put max of 10 file entries into `self.default_queue`
        :param ctx: discord `Context` object
        """
        if not self.default_files:
            self.default_files = self.get_files()
        for _ in range(5):
            if not self.default_files:
                return
            file = self.default_files.pop()
            entry = Entry.from_file(ctx, file)
            await self.default_queue.put(entry)

    async def __play_current(self, ctx):
        """
        Play the current entry.
        :param ctx: discord `Context` object
        """
        await ctx.send(f'Now playing:{self.current.detail()}')
        await self.current.play(ctx)
        if self.current:
            self.__log_del(self.current)
            del self.current
            self.current = None

    async def skip(self, ctx: Context, force: bool):
        """
        Skip the current song.
        :param ctx: discord `Context` object
        :param force: True to force skip.
        """
        if not self.current:
            await ctx.send('There is nothing playing.')
            return
        if force:
            skipped = True
        else:
            skipped = await self.current.skip(ctx)
        if skipped:
            if ctx.author == self.current.requester and not force:
                await ctx.send('Song skipped by requester.')
            elif not force:
                await ctx.send('Song has been voted to be skipped.')
            ctx.voice_client.stop()
            self.__log_del(self.current)
            del self.current
            self.current = None

    async def queue(self, ctx: Context, query: str):
        """
        Enqueue a song from youtube-dl into the guild queue.
        :param ctx: discord `Context` object
        :param query: a search query or url.
        """
        entry = Entry.from_yt(ctx, query)
        await self.guild_queue.put(entry)

    async def play_default(self, ctx: Context):
        """
        Play the default playlist.
        :param ctx: discord `Context` object
        """
        if self.playing_status == PlayingStatus.FILE:
            return
        if not self.default_files:
            self.default_files = self.get_files()
        while True:
            if self.default_queue.qsize() <= 1:
                await self.put_default_entries(ctx)
            self.playing_status = PlayingStatus.FILE
            self.current = await self.default_queue.get()
            await self.__play_current(ctx)
            if self.playing_status != PlayingStatus.FILE:
                if ctx.voice_client:
                    await ctx.voice_client.disconnect()
                return

    async def play(self, ctx: Context):
        """
        Play the guild playlist.

        If the default playlist is playing, this will stop it and clear it.

        Will dissconnect from the voice channel after 10 minutes if nothing is
        playing.

        :param ctx: discord `Context` object
        """
        if self.playing_status == PlayingStatus.WEB:
            return
        while True:
            if self.playing_status == PlayingStatus.FILE:
                self.playing_status = PlayingStatus.WEB
                del self.default_queue
                self.default_queue = Queue()
                await self.skip(ctx, True)
            self.playing_status = PlayingStatus.WEB
            try:
                self.current = await wait_for(self.guild_queue.get(), 600)
            except TimeoutError:
                self.playing_status = PlayingStatus.NO
                if ctx.voice_client:
                    await ctx.voice_client.disconnect()
                return
            await self.__play_current(ctx)
