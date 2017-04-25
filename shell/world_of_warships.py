"""World of Warships commands for this bot"""
from os.path import join

from discord.ext import commands

from core.helpers import generate_image_online
from core.wows_core.shell_handler import build_shame_embed, region_converter, \
    find_player, generate_shamelist, process_add_shame, process_remove_shame
from core.wows_core.wg_core import get_all_ship_tier
from core.wows_core.wtr_core import warships_today_url, coeff_all_region


class WorldOfWarships:
    """ WoWs commands """

    def __init__(self, bot):
        self.bot = bot
        self.data = self.bot.data
        self.api = self.data.wows_api

    @commands.command()
    async def update_wows(self):
        self.data.coefficients, self.data.expected = \
            coeff_all_region()
        self.data.ship_dict = get_all_ship_tier(self.api)
        await self.bot.say('Update Success!')

    @commands.command(pass_context=True)
    async def shame(self, ctx, user_name: str, region: str = 'NA'):
        """Get shamed by a bot"""
        if region not in ['NA', 'EU', 'RU', 'AS']:
            await self.bot.say('Region must be in ' + str(
                ['NA', 'EU', 'RU', 'AS']) + ' or blank for default(NA)')
            return
        region, player_id = find_player(
            ctx, self.bot.cursor, user_name,
            region_converter(region, False), self.api)
        if player_id is None:
            await self.bot.say('Cannot find player!')
            return
        r = region.value if region.value != 'com' else 'na'
        embed = build_shame_embed(region, self.api, player_id,
                                  coefficients=self.data.coefficients[r],
                                  expected=self.data.expected[r],
                                  ship_dict=self.data.ship_dict[r])
        if embed is None:
            fn = generate_image_online(warships_today_url(r, player_id),
                                       join('data', 'dark.png'))
            await self.bot.send_file(ctx.message.channel, fn)
        else:
            await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    async def shamelist(self, ctx):
        """Get the entire shame shamelist"""
        res = generate_shamelist(ctx, self.bot.cursor)
        if res is not None:
            await self.bot.say(res)
        else:
            await self.bot.say('This server doesn\'t have a shame list!')

    @commands.command(pass_context=True, no_pm=True)
    async def addshame(self, ctx, user_name: str, region: str = 'NA'):
        """Add you to the shame shamelist"""
        if region not in ['NA', 'EU', 'RU', 'AS']:
            await self.bot.say('Region must be in ' + str(
                ['NA', 'EU', 'RU', 'AS']) + ' or blank for default(NA)')
            return
        new_entry = \
            process_add_shame(
                ctx, self.bot.cursor, self.bot.conn,
                user_name, region, self.api)
        if new_entry:
            await self.bot.say('Add success!')
        elif not new_entry:
            await self.bot.say('Edit Success!')

    @commands.command(pass_context=True, no_pm=True)
    async def removeshame(self, ctx):
        """Remove you from the shame shamelist"""
        process_remove_shame(ctx, self.bot.cursor, self.bot.conn)
        await self.bot.say('Remove success!')
