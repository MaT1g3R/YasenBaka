from typing import Optional

from discord import VoiceChannel

from music.file_player import FilePlayer
from music.yt_player import YTPlayer


class GuildMusicManager:
    """
    Music player manager for a given guild.
    """
    __slots__ = ('player',)

    def __init__(self):
        self.player = None

    def __empty(self) -> bool:
        """
        :return: True if there's nothing playing and nothing in queue.
        """
        return not self.player or self.player.empty

    async def get_file_player(
            self, ctx, voice_channel: VoiceChannel) -> Optional[FilePlayer]:
        """
        Get a `FilePlayer`.
        If there's currently a non-empty `YTPlayer`, return None.

        :param ctx: the `discord.Context` object.

        :param voice_channel: the `VoiceChannel` to play audio in.

        :return: A `FilePlayer` instance if there's no non-empty `YTPlayer`.
        """
        if isinstance(self.player, YTPlayer) and not self.__empty():
            await ctx.send('Cannot play default playlist when there are'
                           ' user requested music.')
            return
        if not isinstance(self.player, FilePlayer):
            self.player = FilePlayer(
                ctx.bot.logger, voice_channel, ctx.bot.config.music_path
            )
        return self.player

    async def get_yt_player(
            self, ctx, voice_channel: VoiceChannel) -> YTPlayer:
        """
        Get a `YTPlayer`.
        If there's a `FilePlayer`, stop it and delete it.

        :param ctx: the `discord.Context` object.

        :param voice_channel: the `VoiceChannel` to play audio in.

        :return: A `YTPlayer` instance.
        """
        if isinstance(self.player, YTPlayer):
            return self.player
        if isinstance(self.player, FilePlayer):
            await self.player.stop(ctx, False)
            del self.player
            self.player = None
        if not self.player:
            self.player = YTPlayer(ctx.bot.logger, voice_channel)
            return self.player

    async def stop(self, ctx):
        """

        :param ctx:
        :return:
        """
        if not self.player:
            return
        await self.player.stop(ctx, True)
        del self.player
        self.player = None
