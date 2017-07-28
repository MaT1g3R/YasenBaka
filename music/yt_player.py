from discord import VoiceChannel

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

    async def enqueue(self, ctx, query: str = None):
        """
        Search and enqueue one `Entry` from youtube-dl.
        Does not enqueue if the search result is empty.

        :param ctx: the `discord.Context` object.

        :param query: the search query.
        """
        entry = await Entry.from_yt(ctx, query)
        if not entry:
            await ctx.send(f'Search query {query} not found.')
            return
        self.entry_queue.append(entry)
        await ctx.send(f'Enqueued:{entry.detail}')
