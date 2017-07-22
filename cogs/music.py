from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen
from scripts.checks import is_admin, no_pm


class Music:
    """
    Muisc Commands.
    """

    def __init__(self, bot: Yasen):
        self.bot = bot

    def __local_check(self, ctx: Context):
        return no_pm(ctx)

    @commands.command()
    async def play(self, ctx: Context, *, search=None):
        """
        Description: Play music in your current voice channel.
        Restrictions: |
            Cannot be used in private message.
            Can only play music in one voice channel for each guild.
            You must be in a voice channel.
        Usage: "`{prefix}play some song name or url`
        Must provide a name or url."
        Note: This will terminate the default playlist if it is current.
        """
        raise NotImplementedError

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
        raise NotImplementedError

    @commands.command()
    async def playing(self, ctx: Context):
        """
        Description: "Check what's current."
        Restriction: Cannot be used in private message.
        Usage: "`{prefix}current`"
        """
        raise NotImplementedError

    @commands.command()
    async def playlist(self, ctx: Context):
        """
        Description: Display the current playlist for this guild.
        Restriction: Cannot be used in private message.
        Usage: "`{prefix}playlist`"
        """
        raise NotImplementedError

    @commands.command()
    async def skip(self, ctx: Context):
        """
        Description: "Vote to skip the current song.
        Song requester can skip without voting."
        Restriction: Cannot be used in private message.
        Usage: "`{prefix}skip`"
        Note: "Vote count can be set in `{prefix}setskip` default is 3."
        """
        raise NotImplementedError

    @commands.command()
    @commands.check(is_admin)
    async def setskip(self, ctx: Context, count=None):
        """
        Description: Set the vote count needed to skip a song in this guild.
        Restriction: Cannot be used in private message.
        Permission Required: Administrator
        Usage: "`{prefix}setskip num`
        where `num` is a natural number less than 256"
        """
        raise NotImplementedError

    @commands.command()
    @commands.check(is_admin)
    async def stop(self, ctx: Context):
        """
        Description: "Stop whatever is current and leave the voice channel.
        This will also delete any song queued in the playlist."
        Restriction: Cannot be used in private message.
        Permission Required: Administrator
        Usage: "`{prefix}stop`"
        """
        raise NotImplementedError
