from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen
from music import MusicPlayer, PlayingStatus
from scripts.checks import is_admin, no_pm
from scripts.helpers import parse_number


class Music:
    """
    Muisc Commands.
    """

    def __init__(self, bot: Yasen):
        self.bot = bot
        self.music_players = {}

    def __local_check(self, ctx: Context):
        return no_pm(ctx)

    def get_player(self, guild_id: int, create_new) -> MusicPlayer:
        player = self.music_players.get(guild_id, None)
        if not create_new:
            return player
        if not player:
            player = MusicPlayer(self.bot.config.music_path)
            self.music_players[guild_id] = player
        return player

    def check_conditions(self, ctx, music_player):
        ch = ctx.author.voice.channel
        status = music_player.playing_status
        if status == PlayingStatus.NO and not ch:
            return False, 'You must be in a voice channel to use this command.'
        if status != PlayingStatus.NO and ch not in self.bot.voice_clients:
            return False, (
                'You must be in the same voice'
                'channel as me to use this command.'
            )
        return True, None

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
        music_player = self.get_player(ctx.guild.id, True)
        condition, msg = self.check_conditions(ctx, music_player)
        if not condition:
            await ctx.send(msg)
            return
        await music_player.queue(ctx, search)
        await music_player.play(ctx)

    @commands.command()
    async def playdefault(self, ctx: Context):
        """
        Description: Play the default playlist in your current voice channel.
        Restrictions: |
            Cannot be used in private message.
            Can only play music in one voice channel for each guild.
            You must be in a voice channel.
        Usage: "`{prefix}playdefault`"
        Note: "This will be terminated by the `{prefix}play` command."
        """
        music_player = self.get_player(ctx.guild.id, True)
        condition, msg = self.check_conditions(ctx, music_player)
        if not condition:
            await ctx.send(msg)
            return
        if music_player.playing_status == PlayingStatus.WEB:
            await ctx.send('Currently playing user requested music,'
                           'please wait for the queue to be empty'
                           'to use this command.')
            return
        await music_player.play_default(ctx)

    @commands.command()
    async def playing(self, ctx: Context):
        """
        Description: "Check what's current."
        Restriction: Cannot be used in private message.
        Usage: "`{prefix}current`"
        """
        not_playing = 'Not playing anything.'
        music_player = self.get_player(ctx.guild.id, False)
        if not music_player:
            await ctx.send(not_playing)
            return
        if music_player.playing_status == PlayingStatus.NO:
            await ctx.send(not_playing)
            return
        await ctx.send(str(music_player.current))

    @commands.command()
    async def playlist(self, ctx: Context):
        """
        Description: Display the current playlist for this guild.
        Restriction: Cannot be used in private message.
        Usage: "`{prefix}playlist`"
        """
        empty = 'The playlist is empty.'
        music_player = self.get_player(ctx.guild.id, False)
        if not music_player:
            await ctx.send(empty)
            return
        await ctx.send(await music_player.play_list_str())

    @commands.command()
    async def skip(self, ctx: Context):
        """
        Description: "Vote to skip the current song.
        Song requester can skip without voting."
        Restriction: Cannot be used in private message.
        Usage: "`{prefix}skip`"
        Note: "Vote count can be set in `{prefix}setskip` default is 3."
        """
        not_playing = 'Not playing anything.'
        music_player = self.get_player(ctx.guild.id, False)
        if not music_player:
            await ctx.send(not_playing)
            return
        if music_player.playing_status == PlayingStatus.NO:
            await ctx.send(not_playing)
            return
        await music_player.skip(ctx, False)

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
    async def stop(self, ctx: Context):
        """
        Description: "Stop whatever is current and leave the voice channel.
        This will also delete any song queued in the playlist."
        Restriction: Cannot be used in private message.
        Usage: "`{prefix}stop`"
        """
        music_player = self.get_player(ctx.guild.id, False)
        if not music_player:
            return
        await ctx.voice_client.disconnect()
        del self.music_players[ctx.guild.id]
