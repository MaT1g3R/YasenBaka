from discord import VoiceChannel
from discord.ext.commands import Context
from youtube_dl import DownloadError

from music.abstract_music_player import AbstractMusicPlayer
from music.entry import Entry


class YTPlayer(AbstractMusicPlayer):
    """
    Player to play audio from youtube-dl.
    """
    __slots__ = ()

    def __init__(self, logger, channel: VoiceChannel):
        """
        See `AbstractMusicPlayer.__init__`
        """
        super().__init__(logger, channel)

    async def enqueue(self, ctx: Context, query: str = None):
        """
        Search and enqueue one `Entry` from youtube-dl.
        Does not enqueue if the search result is empty.

        :param ctx: the `discord.Context` object.

        :param query: the search query.
        """
        async with ctx.typing():
            try:
                entry = await Entry.from_yt(ctx, query)
            except DownloadError as e:
                self.logger.warn(str(e))
                await ctx.send('Sorry, this url is not supported.')
                return
        if not entry:
            await ctx.send(f'Search query {query} not found.')
            return
        self.entry_queue.append(entry)
        await ctx.send(f'Enqueued:{entry.detail}')
