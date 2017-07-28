from asyncio import Queue
from collections import deque

from discord import VoiceChannel
from discord.ext.commands import Context


class AbstractMusicPlayer:
    """
    An abstract class for a music player.

    === Attributes ===
    :type logger: Logger
        A logger to do logging with.
    :type channel: VoiceChannel
        The voice channel to play audio in.
    :type entry_queue: deque
        A queue of `Entry` objects to be played.
    :type current: Entry
        The currently playing `Entry`
    :type finished: Queue
        `Entry` that finished playing will be pushed into this queue and be
        deleted.
    :type playing: bool
        A bool to keep track if self is playing audio. If this is True, any
        call on `self.play` will have no effect.
    """
    __slots__ = ('logger', 'channel', 'entry_queue',
                 'current', 'finished', 'playing')

    def __init__(self, logger, channel: VoiceChannel):
        """
        :param logger: a logger object to do logging with.
        :param channel: the `VoiceChannel` to play audio in.
        """
        self.logger = logger
        self.channel = channel
        self.entry_queue = deque()
        self.current = None
        self.finished = Queue(1)
        self.playing = False

    @property
    def empty(self) -> bool:
        """
        Check if the music player is empty.
        :return: True if the music player is empty.
        """
        return self.current is None and not self.entry_queue

    def __del__(self):
        self.entry_queue.clear()
        del self.entry_queue
        del self.current
        del self.finished

    def __after(self, error):
        """
        A method used for the `after` parameter in `discord.VoiceClient.play`.

        This will serve as an observer so we can wait for audio to
        finish playing.

        :param error:
            the error raised during the playing of the audio source, if any.
        """
        if error:
            self.logger.warn(str(error))
        self.finished.put_nowait(self.current)
        self.current = None

    async def enqueue(self, ctx, query: str = None):
        """
        Enqueue `Entry` into `self.entry_queue`
        :param ctx: the `discord.Context` object.
        :param query: the search query. only needed for youtube-dl.
        """
        raise NotImplementedError

    async def skip(self, ctx):
        """
        Skip the currently playing `Entry`
        :param ctx: the `discord.Context` object.
        """
        if not self.current:
            await ctx.send('Not playing anything.')
            return
        skipped, is_requester, votes = await self.current.skip(ctx)
        if skipped and ctx.voice_client:
            ctx.voice_client.stop()
        if skipped and is_requester:
            await ctx.send('Song skipped by requester.')
        if skipped and not is_requester:
            await ctx.send(f'Song skipped. {votes}')

    async def play(self, ctx):
        """
        Public facing method to trigger playing audio.
        :param ctx: the `discord.Context` object.
        """
        if self.playing:
            return
        await self.__play(ctx)

    async def __play(self, ctx):
        """
        Method to play audio. After audio is finished playing this will call
        `self.__play_next` to check if it needs to continue playing.

        :param ctx: the `discord.Context` object.
        """
        if self.empty:
            return
        self.playing = True
        self.current = self.entry_queue.popleft()
        await self.current.play(ctx, self.channel, self.__after)
        await ctx.send(f'Now playing:{self.current.detail}')
        fin = await self.finished.get()
        del fin
        await self.__play_next(ctx)

    async def __play_next(self, ctx):
        """
        After an `Entry` is finished playing, check if there is a need to
        play the next `Entry` in `self.entry_queue`

        :param ctx: the `discord.Context` object.
        """
        if self.empty:
            self.playing = False
            await self.stop(ctx, True)
            return
        await self.__play(ctx)

    async def stop(self, ctx: Context, disconnect: bool):
        """
        Stop playing audio.

        :param ctx: the `discord.Context` object.

        :param disconnect: if True, also disconnect from the voice client.
        """
        self.current = None
        self.entry_queue.clear()
        vc = ctx.voice_client
        if vc:
            vc.stop()
        if vc and disconnect:
            await vc.disconnect()
