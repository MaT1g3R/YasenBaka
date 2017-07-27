from asyncio import Queue
from collections import deque
from pathlib import Path
from random import shuffle
from typing import Optional

from discord import VoiceChannel
from discord.ext.commands import Context

from music.entry import Entry
from music.playing_status import PlayingStatus


class MusicPlayer:
    """
    A music player object for a single guild.

    === Attributes ===
    :type logger: Logger
        A logger object to do logging.
    :type default_path: Optional[Path]
        Path that points to the directory containing the default playlist.
    :type file_queue: deque
        A deque of file paths in the default playlist directory.
    :type query_queue: deque
        A deque of user queries cached to save RAM.
    :type entry_queue: asyncio.Queue:
        A queue of `Entry`.
    :type playing_status: PlayingStatus
        A value that represents the current playing status.
    :type current: Optional[Entry]
        An `Entry` object that is currently playing.
    :type deleting: bool:
        Boolen to signal if this instance is being deleted.
    """

    __slots__ = ('logger', 'default_path', 'file_queue', 'query_queue',
                 'entry_queue', 'playing_status', 'current', 'deleting')

    def __init__(self, logger, default_path: Optional[Path] = None):
        """
        Init the instance.
        :param logger: logger used for logging.
        :param default_path:
            Path that points to the default playlist dir, optional.
        """
        self.logger = logger
        self.default_path = default_path
        self.file_queue = deque()
        self.query_queue = deque()
        self.entry_queue = Queue()
        self.playing_status = PlayingStatus.NO
        self.current = None
        self.deleting = False

    def __del__(self):
        self.deleting = True
        self.__del_q(False)
        del self.file_queue
        del self.query_queue
        del self.playing_status

    @property
    def play_list(self) -> str:
        """
        Get the playlist for the guild as string.
        :return: a string representation of the platlist queued for the guild.
        """
        if self.playing_status == PlayingStatus.NO:
            return 'Playlist is empty.'
        q = self.entry_queue._queue
        extra_length = None
        if self.playing_status == PlayingStatus.FILE:
            extra_length = len(self.file_queue)
        elif self.playing_status == PlayingStatus.WEB:
            extra_length = len(self.query_queue)
        lst_str = '\n'.join((str(entry) for entry in q))
        if self.current:
            lst_str = f'Current ➡️ {self.current}\n{lst_str}'
        if lst_str:
            extra = f'And {extra_length} more.' if extra_length else ''
            return f'```\n{lst_str}\n```{extra}'
        else:
            return 'Playlist is empty.'

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
            if ctx.voice_client:
                ctx.voice_client.stop()
            self.__log_del(self.current)
            if ctx.author == self.current.requester and not force:
                await ctx.send('Song skipped by requester.')
            elif not force:
                await ctx.send('Song has been voted to be skipped.')

    async def stop(self, ctx: Context):
        """
        Stop playing music and clear the entry queue.
        :param ctx: discord `Context` object
        """
        self.playing_status = PlayingStatus.NO
        self.__del_q(True)
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        try:
            del self.current
        except AttributeError:
            pass

    async def enqueue(self, ctx: Context, query: str):
        """
        Enqueue a song from youtube-dl into the guild queue.
        :param ctx: discord `Context` object
        :param query: a search query or url.
        """
        if self.playing_status == PlayingStatus.FILE:
            self.__del_q(True)
        if self.entry_queue.qsize() >= 5:
            self.query_queue.append((query, ctx))
            await ctx.send(f'Enqueued query: `{query}`')
            return
        entry = await Entry.from_yt(ctx, query)
        if not entry:
            await ctx.send(f'Sorry, query: `{query}` not found.')
            return
        await self.entry_queue.put(entry)
        await ctx.send(f'Enqueued: {entry.detail}')

    async def play_default(self, ctx: Context, channel: VoiceChannel):
        """
        Play the default playlist.
        :param ctx: discord `Context` object
        :param channel: the voice channel to play music in.
        """
        if self.playing_status != PlayingStatus.NO:
            return
        if not self.file_queue:
            self.__put_files()
        self.playing_status = PlayingStatus.FILE
        await self.__play(ctx, True, channel)

    async def play(self, ctx: Context, channel: VoiceChannel):
        """
        Play the guild playlist.

        If the default playlist is playing, this will stop it and clear it.

        Will dissconnect from the voice channel after queue is empty.

        :param ctx: discord `Context` object
        :param channel: the voice channel to play music in.
        """
        if self.playing_status == PlayingStatus.WEB:
            return
        await self.__play(ctx, False, channel)

    async def __play(self, ctx: Context, is_file: bool, channel: VoiceChannel):
        """
        Helper method to play music.
        :param ctx: discord `Context` object
        :param is_file: True to play default files, False to play user quries.
        :param channel: the voice channel to play music in.
        """
        while True:
            if not is_file and self.playing_status == PlayingStatus.FILE:
                await self.skip(ctx, True)
            if not is_file:
                self.playing_status = PlayingStatus.WEB
            await self.__put_entries(is_file, ctx)
            if self.entry_queue.empty() and not self.current:
                self.playing_status = PlayingStatus.NO
                await self.stop(ctx)
                return
            await self.__play_current(ctx, channel)
            if (is_file and self.playing_status != PlayingStatus.FILE) or \
                    (not is_file and self.playing_status != PlayingStatus.WEB):
                await self.stop(ctx)
                return

    async def __play_current(self, ctx, channel: VoiceChannel):
        """
        Play the current entry.
        :param ctx: discord `Context` object
        :param channel: the voice channel to play music in.
        """
        self.current = await self.entry_queue.get()
        await ctx.send(f'Now playing:{self.current.detail}')
        await self.current.play(ctx, channel)
        try:
            if self.current:
                current_name = str(self.current)
                del self.current
                self.__log_del(current_name)
                self.current = None
        except AttributeError:
            pass

    async def __put_entries(self, is_file: bool, ctx: Context = None):
        """
        Put entries into the entry queue.
        :param is_file: True to put file entries, False to put ytdl entries.
        :param ctx: discord `Context` object
        """
        assert ctx is not None or not is_file
        if is_file:
            await self.__put_file_entries(ctx)
        else:
            await self.__put_guild_entries()

    def __log_del(self, entry_name: str):
        """
        Log the deletion of an entry.
        :param entry_name: the name of entry deleted.
        """
        self.logger.info(f'Deleted entry: {entry_name}')

    def __del_q(self, reset: bool):
        """
        Delete all entries from self.entry_queue.
        :param reset: If True, generate a new empty Queue for entry queue.
        """
        while True:
            if self.entry_queue.empty():
                break
            entry = self.entry_queue.get_nowait()
            entry_name = str(entry)
            del entry
            self.__log_del(entry_name)
        del self.entry_queue
        if reset:
            self.entry_queue = Queue()

    def __put_files(self):
        """
        Get a list of file paths.
        :return: A list of file paths under `self.default_path` if any.
        """
        if not self.default_path or not self.default_path.is_dir():
            return None
        lst = [str(f) for f in self.default_path.iterdir()]
        shuffle(lst)
        self.file_queue.extend(lst)

    async def __put_file_entries(self, ctx: Context):
        """
        Put max of 5 file entries into `self.default_queue`
        :param ctx: discord `Context` object
        """
        if len(self.file_queue) <= 1:
            self.__put_files()
        while True:
            if not self.file_queue or self.entry_queue.qsize() >= 5:
                return
            file = self.file_queue.popleft()
            entry = Entry.from_file(ctx, file)
            await self.entry_queue.put(entry)

    async def __put_guild_entries(self):
        """
        Put max of 5 entries into the guild queue from the quild query queue.
        """
        while True:
            if not self.query_queue or self.entry_queue.qsize() >= 5:
                return
            query, ctx = self.query_queue.popleft()
            entry = await Entry.from_yt(ctx, query)
            if not entry:
                await ctx.send(f'Query `{query}` enqueued by {ctx.author}'
                               f'could not be found, skipping.')
                continue
            await self.entry_queue.put(entry)
