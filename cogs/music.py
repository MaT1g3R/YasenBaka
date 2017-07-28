from typing import NewType, Optional, Union

from discord import VoiceChannel, opus
from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen
from music.abstract_music_player import AbstractMusicPlayer
from music.guild_music_manager import GuildMusicManager
from scripts.checks import is_admin, no_pm
from scripts.helpers import parse_number

_PlayerType = Union[
    NewType('FilePlayer', AbstractMusicPlayer),
    NewType('YTPlayer', AbstractMusicPlayer),
]


class Music:
    """
    Muisc Commands.
    """
    __slots__ = ('bot', 'music_managers')

    def __init__(self, bot: Yasen):
        self.bot = bot
        self.music_managers = {}
        if not opus.is_loaded():
            raise ValueError('libopus is not loaded, please install the'
                             'library through your package manager or add'
                             'it to your PATH.')

    def __local_check(self, ctx: Context):
        return no_pm(ctx)

    async def check_conditions(self, ctx: Context) -> tuple:
        """
        Check conditions for playing music in a guild.
        :param ctx: the `discord.Context` object.
        :return: a tuple of (Can play music, channel to play music in)
        """
        guild_id = ctx.guild.id
        voice_state = ctx.author.voice
        channel = voice_state.channel if voice_state else None
        if not channel:
            await ctx.send('You must be in a voice channel'
                           ' to use music commands.')
            return False, channel
        manager = self.music_managers.get(guild_id)
        if not manager or \
                not manager.player or manager.player.channel == channel:
            return True, channel
        else:
            await ctx.send('You must be in the same voice'
                           ' channel as me to use music commands.')
            return False, channel

    async def get_player(self, ctx: Context, voice_channel: VoiceChannel,
                         is_file: bool) -> Optional[_PlayerType]:
        """
        Get a music player for the guild.
        :param ctx: the `discord.Context` object.
        :param voice_channel: the voice channel to play music in.
        :param is_file:
            True to play defualt playlist, False to play with youtube-dl.
        :return: A music player for the guild.
        """
        guild_id = ctx.guild.id
        if guild_id not in self.music_managers:
            self.music_managers[guild_id] = GuildMusicManager()
        manager: GuildMusicManager = self.music_managers[guild_id]
        if is_file:
            return await manager.get_file_player(ctx, voice_channel)
        return await manager.get_yt_player(ctx, voice_channel)

    def is_playing(self, ctx) -> tuple:
        """
        Check if music is playing in the context.
        :param ctx: the `discord.Context` object.
        :return: A tuple of (is playing music, the music player if any)
        """
        manager = self.music_managers.get(ctx.guild.id)
        if not manager or not manager.player:
            return False, None
        player = manager.player
        if not player.current:
            return False, player
        return True, player

    @commands.command()
    async def play(self, ctx: Context, *, search=None):
        """
        Description: Play music in your current voice channel.
        Restrictions: "
            Cannot be used in private message.\n
            Can only play music in one voice channel for each guild.\n
            You must be in a voice channel.\n
            If the bot is already playing music,
            you must be in the same voice channel as the bot."
        Usage: "`{prefix}play some song name or url`
        Must provide a name or url."
        Note: This will terminate the default playlist if it is current.
        """
        if not search:
            await ctx.send('Please enter a link or a search term.')
            return
        condition, channel = await self.check_conditions(ctx)
        if not condition:
            return
        player = await self.get_player(ctx, channel, False)
        await player.enqueue(ctx, search)
        await player.play(ctx)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def playdefault(self, ctx: Context):
        """
        Description: Play the default playlist in your current voice channel.
        Restrictions: |
            Cannot be used in private message.
            Can only play music in one voice channel for each guild.
            You must be in a voice channel.
        Cooldown: Once every 5 seconds per guild.
        Usage: "`{prefix}playdefault`"
        Note: "This will be terminated by the `{prefix}play` command."
        """
        path = self.bot.config.music_path
        if not path or not path.is_dir():
            await ctx.send('I do not have a default playlist.')
            return
        condition, channel = await self.check_conditions(ctx)
        if not condition:
            return
        player = await self.get_player(ctx, channel, True)
        if not player:
            return
        await player.enqueue(ctx)
        await player.play(ctx)

    @commands.command()
    async def playing(self, ctx: Context):
        """
        Description: "Check what's current."
        Restriction: Cannot be used in private message.
        Usage: "`{prefix}current`"
        """
        playing, player = self.is_playing(ctx)
        if not playing:
            await ctx.send('Not playing anything.')
        else:
            await ctx.send(f'Playing:{player.current.detail}')

    @commands.command()
    async def playlist(self, ctx: Context):
        """
        Description: Display the current playlist for this guild.
        Restriction: Cannot be used in private message.
        Usage: "`{prefix}playlist`"
        """
        pass

    @commands.command()
    async def skip(self, ctx: Context):
        """
        Description: "Vote to skip the current song.
        Song requester can skip without voting."
        Restriction: Cannot be used in private message.
        Usage: "`{prefix}skip`"
        Note: "Vote count can be set in `{prefix}setskip` default is 3."
        """
        playing, player = self.is_playing(ctx)
        if not playing:
            await ctx.send('Not playing anything.')
        else:
            await player.skip(ctx)

    @commands.command()
    @commands.check(is_admin)
    async def setskip(self, ctx: Context, count=None):
        """
        Description: Set the vote count needed to skip a song in this guild.
        Restriction: Cannot be used in private message.
        Permission Required: Administrator
        Usage: "`{prefix}setskip num`
        where `num` is a natural number between 0 and 255"
        """
        num = parse_number(count, int)
        if not isinstance(num, int) or not 0 <= num <= 255:
            await ctx.send(
                'Please enter a natural number number between 0 and 255'
            )
            return
        self.bot.data_manager.set_skip(str(ctx.guild.id), num)
        await ctx.send(
            f'The skip count for this guild has been set to **{num}**'
        )

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def stop(self, ctx: Context):
        """
        Description: "Stop whatever is current and leave the voice channel.
        This will also delete any song queued in the playlist."
        Restriction: Cannot be used in private message.
        Cooldown: Once every 5 seconds per guild.
        Usage: "`{prefix}stop`"
        """
        manager = self.music_managers.get(ctx.guild.id)
        if not manager:
            await ctx.send('Not playing anything.')
            return
        await manager.stop(ctx)
