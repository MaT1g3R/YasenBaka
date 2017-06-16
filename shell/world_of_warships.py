"""World of Warships commands for this bot"""
from json import JSONDecodeError
from os.path import join

from discord.ext import commands

from core.file_system import fopen_generic, write_json
from core.helpers import generate_image_online
from core.wows_core.shell_handler import build_shame_embed, find_player, \
    generate_shamelist, process_add_shame, process_clan, process_remove_shame, \
    region_converter
from core.wows_core.wg_core import get_all_ship_tier
from core.wows_core.wtr_core import coeff_all_region, warships_today_url


class WorldOfWarships:
    """ WoWs commands """

    def __init__(self, bot):
        self.bot = bot
        self.data = self.bot.data
        self.api = self.data.wows_api

    @commands.command()
    async def update_wows(self):
        try:
            self.data.coefficients, self.data.expected = \
                coeff_all_region()
            self.data.ship_dict = get_all_ship_tier(self.api)
            fp = fopen_generic(join('data', 'coefficients.json'), 'w')
            write_json(fp, self.data.coefficients)
            fp = fopen_generic(join('data', 'expected.json'), 'w')
            write_json(fp, self.data.expected)
            await self.bot.say('Update Success!')
        except JSONDecodeError:
            await self.bot.say(
                'Update Failed! Cause is probably '
                'Warships Today api being down.')

    @commands.command(pass_context=True)
    async def shame(self, ctx, user_name: str, region: str = 'NA'):
        """Get shamed by a bot"""
        if region not in ['NA', 'EU', 'RU', 'AS']:
            await self.bot.say('Region must be in ' + str(
                ['NA', 'EU', 'RU', 'AS']) + ' or blank for default(NA)')
            return
        loading = await self.bot.say('Loading...')
        region, player_id = find_player(
            ctx, self.bot.cursor, user_name,
            region_converter(region, False), self.api)
        if player_id is None:
            await self.bot.edit_message(loading, 'Cannot find player!')
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
        await self.bot.delete_message(loading)

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

    @commands.command()
    async def clan(self, query, region='NA'):
        await self.clan_helper(query, region)

    @commands.command()
    async def clanwtr(self, query, region='NA'):
        await self.clan_helper(query, region, True)

    async def clan_helper(self, query, region='NA', is_wtr=False):
        if region not in ['NA', 'EU', 'RU', 'AS']:
            await self.bot.say('Region must be in ' + str(
                ['NA', 'EU', 'RU', 'AS']) + ' or blank for default(NA)')
        else:
            msg = await self.bot.say('Loading...')
            r = region_converter(region,
                                 False).value if region != 'NA' else 'na'
            res = process_clan(self.api, region, query) if not is_wtr else \
                process_clan(self.api, region, query,
                             coefficients=self.data.coefficients[r],
                             expected=self.data.expected[r],
                             ship_dict=self.data.ship_dict[r])
            if res is None:
                await self.bot.edit_message(msg, 'Clan not found!')
            else:
                await self.bot.say(embed=res)
                await self.bot.delete_message(msg)
