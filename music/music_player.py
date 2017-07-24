from asyncio import Queue
from enum import Enum
from pathlib import Path
from random import shuffle

from discord.ext.commands import Context

from music.entry import Entry


class PlayingStatus(Enum):
    NO = 0
    FILE = 1
    WEB = 2


class MusicPlayer:
    def __init__(self, default_path: Path = None):
        self.default_path = default_path
        self.default_files = None
        self.default_queue = Queue()
        self.guild_queue = Queue()
        self.playing_status = PlayingStatus.NO
        self.current = None

    def __del__(self):
        del self.guild_queue
        del self.default_queue
        del self.current
        del self.default_files

    async def play_list_str(self) -> str:
        raise NotImplementedError

    def get_files(self):
        if not self.default_path or not self.default_path.is_dir():
            return None
        lst = list(
            str(Path(f).resolve().absolute())
            for f in self.default_path.iterdir()
        )
        shuffle(lst)
        return lst

    async def put_default_entries(self):
        if not self.default_files:
            self.default_files = self.get_files()
        for _ in range(10):
            if not self.default_files:
                return
            file = self.default_files.pop()
            entry = Entry(file)
            await self.default_queue.put(entry)

    async def __play_current(self):
        await self.current.play()
        del self.current
        self.current = None

    async def skip(self, ctx: Context, force: bool):
        self.playing_status = PlayingStatus.NO
        if not self.current:
            return
        if force:
            ctx.voice_client.stop()
        else:
            self.current.skip()
        del self.current
        self.current = None

    async def queue(self, ctx, query):
        entry = Entry(ctx, query, False)
        await self.guild_queue.put(entry)

    async def play_default(self, ctx):
        if not self.default_path or not self.default_path.is_dir():
            return
        if not self.default_files:
            self.default_files = self.get_files()
        while True:
            if self.default_queue.empty():
                await self.put_default_entries()
            self.playing_status = PlayingStatus.FILE
            self.current = await self.default_queue.get()
            await self.__play_current()
            if self.playing_status != PlayingStatus.FILE:
                return

    async def play(self, ctx):
        while True:
            if self.playing_status == PlayingStatus.FILE:
                await self.skip(ctx, True)
            self.playing_status = PlayingStatus.WEB
            self.current = await self.guild_queue.get()
            await self.__play_current()
