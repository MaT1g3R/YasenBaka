from time import time

from discord import Embed, File
from discord.ext import commands
from discord.ext.commands import Context
from wowspy import Region

from bot import Yasen
from world_of_warships.shell_handler import ConvertRegion, get_player_id
from world_of_warships.war_gaming import get_clan_id


class WorldOfWarships:
    def __init__(self, bot: Yasen):
        self.bot = bot

    @commands.command()
    async def shame(self, ctx: Context, name=None,
                    region: ConvertRegion() = None):
        """
        Description: Get a World of Warships player stats.
        Regions: "`NA, EU, RU, AS`"
        Usage: "`{prefix}shame player_name region`
        region defaults to NA if not provided."
        Extra: "You can look up player by using a mention if the player is
        registered in the database via the `{prefix}shamelist add` command."
        """
        async with ctx.typing():
            region = region or Region.NA
            player_id = await get_player_id(ctx, name, region)
            res = await self.bot.wows_manager.player_embed(region, player_id)
        if isinstance(res, Embed):
            await ctx.send(embed=res)
        else:
            bytes_io = await self.bot.session_manager.bytes_img(res)
            file = File(bytes_io, f'{int(time())}_wows_sig.png')
            await ctx.send(file=file)

    @commands.command()
    async def clan(self, ctx: Context, name=None,
                   region: ConvertRegion() = None):
        """
        Description: Get a World of Warships clan stats.
        Regions: "`NA, EU, RU, AS`"
        Usage: "`{prefix}clan clan_name region`
        region defaults to NA if not provided."
        """
        if not name:
            await ctx.send('Please enter a clan name.')
            return
        region = region or Region.NA
        clan_id = await get_clan_id(region, self.bot.wows_api,
                                    self.bot.logger, name)
        if not clan_id:
            await ctx.send(f'Clan **{name}** not found.')
            return
        await self.bot.wows_manager.process_clan(ctx, region, clan_id)

    @commands.group()
    @commands.guild_only()
    async def shamelist(self, ctx: Context):
        """
        Description: "Get the list of players registered in the database in
        this guild. Note this list is not global and is only for the
        current guild."
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
    async def add(self, ctx, name, region: ConvertRegion() = None):
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
    async def remove(self, ctx, region: ConvertRegion() = None):
        """
        Description: "Remove yourself from the guild shamelist.
        Note this list is not global and is only for the current guild."
        Restriction: Cannot be used in PM.
        Regions: "`all, NA, EU, RU, AS`"
        Usage: "`{prefix}shamelist remove region` you must provide a region.
        Use `all` to remove all regions that you have registered."
        """
        raise NotImplementedError
