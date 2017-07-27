from time import time

from discord import Embed, File
from discord.ext import commands
from discord.ext.commands import Context
from wowspy import Region

import world_of_warships.war_gaming as wg
from bot import Yasen
from data_manager.data_utils import get_prefix
from world_of_warships.shell_handler import ConvertRegion, get_clan_id, \
    get_player_id


class WorldOfWarships:
    __slots__ = ('bot',)

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
        async with ctx.typing():
            region = region or Region.NA
            clan_id = await get_clan_id(ctx, name, region)
            embed, players = await self.bot.wows_manager.process_clan(
                region, clan_id)
        if isinstance(embed, Embed):
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed)
        if players:
            await self.bot.wows_manager.cache_players(region, players)

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
        if ctx.invoked_subcommand:
            return
        prefix = get_prefix(self.bot, ctx.message)
        empty_msg = (f'Your guild does not have a shamelist. '
                     f'Use `{prefix}shamelist add` '
                     f'to add yourself to the shamelist.')
        guild = ctx.guild
        shame_list = self.bot.data_manager.get_shame_list(
            guild.members, str(guild.id)
        )
        if not shame_list:
            await ctx.send(empty_msg)
            return
        embed = Embed(
            colour=self.bot.config.colour,
            title=f'Shamelist for {guild}'
        )
        for key, val in shame_list.items():
            if val:
                embed.add_field(
                    name=key, value=f'`{", ".join(val)}`', inline=False
                )
        await ctx.send(embed=embed)

    @shamelist.command()
    @commands.guild_only()
    async def add(self, ctx, name=None, region: ConvertRegion() = None):
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
        if not name:
            await ctx.send('Please enter a World of Warships player name.')
            return
        region = region or Region.NA
        player_id = await wg.get_player_id(
            region, self.bot.wows_api, self.bot.logger, name
        )
        if not player_id:
            await ctx.send(f'Player **{name}** not found!')
        else:
            self.bot.data_manager.set_shame(
                str(ctx.guild.id), str(ctx.author.id),
                region.name, str(player_id)
            )
            await ctx.send(
                f'You have set your player for {region} region to {name}'
            )

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
        region = region.upper() if region else None
        if region not in ('ALL', 'NA', 'EU', 'AS', 'RU'):
            await ctx.send('Please enter a region in `all, NA, EU, RU, AS`')
            return
        self.bot.data_manager.delete_shame(
            str(ctx.guild.id), str(ctx.author.id), region
        )
        noun = 'regions' if region == 'ALL' else 'region'
        await ctx.send(
            f'You deleted yourself from the shamelist in {region} {noun}'
        )
