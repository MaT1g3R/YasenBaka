from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen


class WorldOfWarships:
    def __init__(self, bot: Yasen):
        self.bot = bot

    @commands.command()
    async def shame(self, ctx: Context, *args):
        """
        Description: Get a World of Warships player stats.
        Regions: "`NA, EU, RU, AS`"
        Usage: "`{prefix}shame player_name region`
        region defaults to NA if not provided."
        Extra: "You can look up player by using a mention if the player is
        registered in the database via the `{prefix}shamelist add` command."
        """
        raise NotImplementedError

    @commands.command()
    async def clan(self, ctx: Context, *args):
        """
        Description: Get a World of Warships clan stats.
        Regions: "`NA, EU, RU, AS`"
        Usage: "`{prefix}clan clan_name region`
        region defaults to NA if not provided."
        """
        raise NotImplementedError

    @commands.group()
    @commands.guild_only()
    async def shamelist(self, ctx: Context):
        """
        Description: "Get the list of players registered in the database in
        this guild."
        Restriction: Cannot be used in PM.
        Usage: |
            `{prefix}shamelist` to get the list of players.
            `{prefix}shamelist add` to add yourself to the shamelist.
            `{prefix}shamelist remove` to remove yourself from the shamelist.
        """
        if not ctx.invoked_subcommand:
            raise NotImplementedError

    @shamelist.command()
    @commands.guild_only()
    async def add(self, ctx, *args):
        """
        Description: "Add yourself to the guild shamelist.
        Note this list is not global and is only for the current guild."
        Restrictions: |
            Cannot be used in PM.
            A member can only have 1 WoWs player registered for each region.
        Regions: "`NA, EU, RU, AS`"
        Usage: "`{prefix}shamelist add my_wows_name region` region defaults
        to NA if not provided."
        """
        raise NotImplementedError

    @shamelist.command()
    @commands.guild_only()
    async def remove(self, ctx, region=None):
        """
        Description: "Remove yourself from the guild shamelist.
        Note this list is not global and is only for the current guild."
        Restriction: Cannot be used in PM.
        Regions: "`all, NA, EU, RU, AS`"
        Usage: "`{prefix}shamelist remove region` you must provide a region.
        Use `all` to remove all regions that you have registered."
        """
        raise NotImplementedError
