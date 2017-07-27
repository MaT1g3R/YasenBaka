from discord.ext.commands import BadArgument, Context, Converter
from wowspy import Region

from data_manager.data_utils import get_prefix
from scripts.discord_utils import leading_members
from world_of_warships.war_gaming import get_clan_id as gcid, \
    get_player_id as gpid


class ConvertRegion(Converter):
    __slots__ = ()

    async def convert(self, ctx, argument) -> Region:
        try:
            return Region[str(argument).upper()] if argument else Region.NA
        except KeyError:
            raise BadArgument('Please enter a region in `NA, EU, RU, AS`')


async def get_player_id(ctx: Context, name, region: Region):
    if not name:
        raise BadArgument('Please enter a player name.')
    bot = ctx.bot
    wows_api = bot.wows_api
    logger = bot.logger
    data_manager = bot.data_manager
    members, _ = leading_members(ctx, name)
    if not members:
        id_ = await gpid(region, wows_api, logger, name)
        if id_ is not None:
            return id_
        raise BadArgument(f'Player **{name}** not found!')
    member = members[0]
    saved = data_manager.get_shame(
        str(ctx.guild.id), str(member.id), region.name
    )
    if saved:
        return saved
    else:
        prefix = get_prefix(ctx.bot, ctx.message)
        raise BadArgument(
            f'Member {member} is not registered in the {region} region. '
            f'You can register using the `{prefix}shamelist add` command.'
        )


async def get_clan_id(ctx: Context, name, region: Region):
    if not name:
        raise BadArgument('Please enter a clan name.')
    bot = ctx.bot
    wows_api = bot.wows_api
    logger = bot.logger
    id_ = await gcid(region, wows_api, logger, name)
    if id_ is not None:
        return id_
    raise BadArgument(f'Clan **{name}** not found!')
