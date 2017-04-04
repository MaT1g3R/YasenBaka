"""World of Warships commands for this bot"""
from discord.ext import commands
import requests
import json
from threading import Timer
from os.path import join
from helpers import format_eq, generate_image_online, read_json, write_json, get_server_id, is_admin, fopen_generic
from discord import Embed


class WorldOfWarships:
    """ WoWs commands """

    def __init__(self, bot, wows_api):
        self.bot = bot
        self.wows_api = wows_api
        self.shame_list = read_json(fopen_generic(join('data', 'shamelist.json')))
        na_ships_url = 'https://api.worldofwarships.com/wows/' \
                       'encyclopedia/ships/?application_id={}'.format(self.wows_api)
        na_ship_api_response = requests.get(na_ships_url).text
        na_ships_json_data = json.loads(na_ship_api_response)
        write_json(fopen_generic(join('data', 'na_ships.json'), 'w'), na_ships_json_data)
        self.na_ships = read_json(fopen_generic(join('data', 'na_ships.json')))['data']
        self.ssheet = read_json(fopen_generic(join('data', 'sheet.json')))
        self.days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        self.save_sheet_event = Timer(300, self.save_sheet)
        self.save_shamelist_event = Timer(300, self.save_shamelist)

    def save_sheet(self):
        """ shortcut for saving sheet """
        write_json(fopen_generic(join('data', 'sheet.json'), 'w'), self.ssheet)
        # self.ssheet = read_json(fopen_generic(join('data', 'sheet.json')))
        self.save_sheet_event = Timer(300, self.save_sheet)

    def save_shamelist(self):
        """ shortcut for saving shamelist """
        write_json(fopen_generic(join('data', 'shamelist.json'), 'w'), self.shame_list)
        # self.shame_list = read_json(fopen_generic(join('data', 'shamelist.json')))
        self.save_sheet_event = Timer(300, self.save_shamelist)

    @commands.command()
    async def ship(self, *input_: str):
        """ look for a ship on the wargaming wiki"""
        ship_dict = None
        ship_name = ' '.join(input_).title()
        if ship_name.startswith('Arp'):
            ship_name = ship_name.replace('Arp', 'ARP')
        for key, val in self.na_ships.items():
            if val['name'] == ship_name:
                ship_dict = val
                break
        if ship_dict is None:
            await self.bot.say("Ship not found!")
            return
        # Format the dictionary so it's human readable
        result = ['```']
        armour = ship_dict['default_profile']['armour']
        # --------------------------------------------------------------------------------------------------------------
        result.append(ship_dict['name'])
        # --------------------------------------------------------------------------------------------------------------
        result.append('Tier: {}'.format(ship_dict['tier']))
        # --------------------------------------------------------------------------------------------------------------
        price_val = '0'
        if ship_dict['price_gold'] != 0:
            price_val = str(ship_dict['price_gold']) + ' Doubloons'
        elif ship_dict['price_credit'] != 0:
            price_val = str(ship_dict['price_credit']) + ' Credits'
        result.append('Price: {}'.format(price_val))
        # --------------------------------------------------------------------------------------------------------------
        result.append('Hit Points: {}'.format(ship_dict['default_profile']['hull']['health']))
        # --------------------------------------------------------------------------------------------------------------
        result.append('Citadel armor: {} mm'.format(format_eq(armour['citadel']['min'], armour['citadel']['max'])))
        # --------------------------------------------------------------------------------------------------------------
        result.append('Gun Casemate Armor: {} mm'.format
                      (format_eq(armour['casemate']['min'], armour['casemate']['max'])))
        # --------------------------------------------------------------------------------------------------------------
        result.append('Armoured Deck: {} mm'.format(format_eq(armour['deck']['min'], armour['deck']['max'])))
        # --------------------------------------------------------------------------------------------------------------
        result.append('Forward and After Ends Armor: {} mm'.format
                      (format_eq(armour['extremities']['min'], armour['extremities']['max'])))
        # --------------------------------------------------------------------------------------------------------------
        result.append('```')
        await self.bot.say('\n'.join(result))

    @commands.command(pass_context=True)
    async def shame(self, ctx, user_name: str, region: str = 'NA'):
        """Get shamed by a bot"""
        if region not in ['NA', 'EU', 'RU', 'AS']:
            await self.bot.say('Region must be in ' + str(['NA', 'EU', 'RU', 'AS']) + ' or blank for default(NA)')
            return

        region_dict = {
            'NA': ['com', 'na'],
            'EU': ['eu'],
            'AS': ['asia'],
            'RU': ['ru']
        }
        in_list = False
        found = True
        warships_region = None
        player_id = None
        wows_region = region_dict[region][0]
        if ctx.message.server is not None and user_name.startswith('<@'):
            server_id = ctx.message.server.id
            if user_name.startswith('<@!'):
                user_name = user_name[3:-1]
            else:
                user_name = user_name[2:-1]
            if server_id in self.shame_list and user_name in self.shame_list[server_id]:
                warships_region = self.shame_list[server_id][user_name][0]
                player_id = self.shame_list[server_id][user_name][1]
                in_list = True
        if not in_list:
            warships_region = region_dict[region][-1]
            wows_api_url = 'https://api.worldofwarships.{}/wows/account/list/' \
                           '?application_id={}&search={}'.format(region_dict[region][0], self.wows_api, user_name)
            r = requests.get(wows_api_url).text
            warships_api_respose = json.loads(r)
            try:
                if warships_api_respose["meta"]["count"] < 1:
                    await self.bot.say("Can't find player")
                    found = False
            except KeyError:
                await self.bot.say("Can't find player")
                found = False
            player_id = warships_api_respose["data"][0]["account_id"]
        if found:
            warships_today_url = "http://{}.warshipstoday.com/signature/{}/dark.png".format(warships_region, player_id)
            fn = generate_image_online(warships_today_url, join('data', 'shame.png'))
            await self.bot.send_file(ctx.message.channel, fn)
            await self.bot.send_message(ctx.message.channel,
                                        embed=detailed_shame(self.wows_api, player_id, wows_region))

    @commands.command(pass_context=True)
    async def shamelist(self, ctx):
        """Get the entire shame shamelist"""
        server_id = get_server_id(ctx)
        if server_id in self.shame_list:
            res = [ctx.message.server.get_member(key).name for key in self.shame_list[server_id]]
            await self.bot.say('```{}```'.format(', '.join(res))) if res else \
                await self.bot.say('This server\'s shamelist is empty!')
        else:
            await self.bot.say('This server\'s shamelist is empty!')

    @commands.command(pass_context=True)
    async def addshame(self, ctx, user_name: str, region: str = 'NA'):
        """Add you to the shame shamelist"""
        if region not in ['NA', 'EU', 'RU', 'AS']:
            await self.bot.say('Region must be in ' + str(['NA', 'EU', 'RU', 'AS']) + ' or blank for default(NA)')
            return
        new_entry = False
        user_id = str(ctx.message.author.id)
        server_id = str(ctx.message.server.id)
        request_urls = {'NA': 'https://api.worldofwarships.com/wows/account/list/'
                              '?application_id={}&search={}'.format(self.wows_api, user_name),
                        'RU': 'https://api.worldofwarships.ru/wows/account/list/'
                              '?application_id={}&search={}'.format(self.wows_api, user_name),
                        'EU': 'https://api.worldofwarships.eu/wows/account/list/'
                              '?application_id={}&search={}'.format(self.wows_api, user_name),
                        'AS': 'https://api.worldofwarships.asia/wows/account/list/'
                              '?application_id={}&search={}'.format(self.wows_api, user_name)
                        }
        request_url = request_urls[region]
        r = requests.get(request_url).text
        json_data = json.loads(r)
        region_codes = {
            'NA': 'na',
            'EU': 'eu',
            'RU': 'ru',
            'AS': 'asia'
        }
        try:
            if json_data["meta"]["count"] < 1:
                await self.bot.say("Can't find player")
                return
        except KeyError:
            await self.bot.say("Can't find player")
            return
        playerid = json_data["data"][0]["account_id"]
        if ctx.message.server.id not in self.shame_list:
            self.shame_list[server_id] = {}
            new_entry = True
        if user_id not in self.shame_list[server_id]:
            self.shame_list[server_id][user_id] = None
            new_entry = True
        self.shame_list[ctx.message.server.id][user_id] = [region_codes[region], playerid]
        self.save_shamelist()
        await self.bot.say('Add success!') if new_entry else await self.bot.say('Edit Success!')

    @commands.command(pass_context=True)
    async def removeshame(self, ctx):
        """Remove you from the shame shamelist"""
        server_id = ctx.message.server.id
        if str(ctx.message.author.id) in self.shame_list[server_id]:
            self.shame_list[server_id].pop(str(ctx.message.author.id), None)
            self.save_shamelist()
            await self.bot.say('Remove success!')
        else:
            await self.bot.say('Removed failed, you were not in the shamelist to begin with.')

    @commands.command(pass_context=True)
    async def newsheet(self, ctx):
        if not is_admin(ctx, ctx.message.author.id):
            await self.bot.say('This is an admin only command!')
        else:
            self.ssheet[str(get_server_id(ctx))] = {}
            self.save_sheet()
            await self.bot.say('New spread sheet created! The old one has been removed!')

    @commands.command(pass_context=True)
    async def addmatch(self, ctx, matchname: str, *datetime):
        if not is_admin(ctx, ctx.message.author.id):
            await self.bot.say('This is an admin only command!')
        elif str(get_server_id(ctx)) not in self.ssheet:
            await self.bot.say('Your server doesn\'t seem to have a spreadsheet, please consult `?help newsheet`')
        elif not datetime or datetime[0] not in self.days:
            await self.bot.say('Please enter a valid date!')
        else:
            self.ssheet[str(get_server_id(ctx))][matchname] = {}
            datetime = list(datetime)
            datetime[0] += ','
            self.ssheet[str(get_server_id(ctx))][matchname]['time'] = datetime
            self.ssheet[str(get_server_id(ctx))][matchname]['players'] = []
            self.save_sheet()
            await self.bot.say('Match on {} added!'.format(' '.join(datetime)))

    @commands.command(pass_context=True)
    async def removematch(self, ctx, matchname):
        if not is_admin(ctx, ctx.message.author.id):
            await self.bot.say('This is an admin only command!')
        elif str(get_server_id(ctx)) not in self.ssheet:
            await self.bot.say('Your server doesn\'t seem to have a spreadsheet, please consult `?help newsheet`')
        elif matchname not in self.ssheet[str(get_server_id(ctx))]:
            await self.bot.say('There doesn\'t seem to be a with that name.')
        else:
            del self.ssheet[str(get_server_id(ctx))][matchname]
            self.save_sheet()
            await self.bot.say('Match: {} removed!'.format(matchname))

    @commands.command(pass_context=True)
    async def joinmatch(self, ctx, *matchname):
        if str(get_server_id(ctx)) not in self.ssheet:
            await self.bot.say('Your server doesn\'t seem to have a spreadsheet, please consult `?help newsheet`')
            return
        else:
            joined = []
            for name in matchname:
                try:
                    if ctx.message.author.id not in self.ssheet[str(get_server_id(ctx))][name]['players']:
                        self.ssheet[str(get_server_id(ctx))][name]['players'].append(ctx.message.author.id)
                        joined.append(name)
                except KeyError:
                    continue
            self.save_sheet()
            await self.bot.say('You have joined matches: {}'.format(', '.join(joined)))

    @commands.command(pass_context=True)
    async def quitmatch(self, ctx, *matchname):
        if str(get_server_id(ctx)) not in self.ssheet:
            await self.bot.say('Your server doesn\'t seem to have a spreadsheet, please consult `?help newsheet`')
            return
        else:
            quits = []
            for name in matchname:
                if name in self.ssheet[str(get_server_id(ctx))]:
                    try:
                        self.ssheet[str(get_server_id(ctx))][name]['players'].remove(ctx.message.author.id)
                        quits.append(name)
                    except ValueError:
                        continue
            self.save_sheet()
            await self.bot.say('You have quit the matches: {}'.format(' ,'.join(quits)))

    @commands.command(pass_context=True)
    async def sheet(self, ctx):
        if str(get_server_id(ctx)) not in self.ssheet:
            await self.bot.say('Your server doesn\'t seem to have a spreadsheet, please consult `?help newsheet`')
            return
        else:
            if self.ssheet[str(get_server_id(ctx))] == {}:
                await self.bot.say('There doesn\'t seem to be any matches in this spread sheet!')
                return
            else:
                res = [
                    '{}: {}\nPlayers: {}\nPlayer count: {}'.format(
                        ' '.join(val['time']),
                        key,
                        ', '.join([ctx.message.server.get_member(player).name for player in val['players']]),
                        len(val['players'])
                    )
                    for key, val in self.ssheet[str(get_server_id(ctx))].items()]
                res.sort(key=lambda x: self.days.index(x[0:x.find(',')]))
                await self.bot.say('```{}```'.format('\n\n'.join(res)))


def detailed_shame(api, id_, region):
    request_url = 'https://api.worldofwarships.{}/wows/account/info/' \
                  '?application_id={}&fields=statistics.pvp,nickname&account_id='.format(region, api)
    result = json.loads(requests.get(request_url + str(id_)).content)['data'][str(id_)]
    nick_name = result['nickname']
    stats = result['statistics']['pvp']
    main_hits = stats['main_battery']['hits']
    main_shots = stats['main_battery']['shots']
    second_hits = stats['second_battery']['hits']
    second_shots = stats['second_battery']['shots']
    torp_hits = stats['torpedoes']['hits']
    torp_shots = stats['torpedoes']['shots']

    battles = stats['battles']
    damage_dealt = stats['damage_dealt']
    planes_killed = stats['planes_killed']
    wins = stats['wins']
    xp = stats['xp']
    survived_battles = stats['survived_battles']
    ships_spotted = stats['ships_spotted']
    warships_killed = stats['frags']
    deaths = battles - survived_battles

    max_damage_dealt = str(stats['max_damage_dealt'])
    max_xp = str(stats['max_xp'])
    max_planes_killed = str(stats['max_planes_killed'])

    eb = Embed(colour=0x4286f4)
    eb.set_author(name=nick_name)
    if battles > 0:
        win_rate = "{0:.2f}".format((wins/battles)*100) + "%"
        avg_dmg = str(int(damage_dealt/battles))
        avg_exp = str(int(xp/battles))
        survival_rate = "{0:.2f}".format((survived_battles/battles)*100) + "%"
        avg_kills = str("{0:.2f}".format(warships_killed/battles))
        avg_plane_kills = str("{0:.2f}".format(planes_killed/battles))
        avg_spotted = str("{0:.2f}".format(ships_spotted/battles))
        kda = "{0:.2f}".format(warships_killed/deaths) if deaths > 0 else '\u221E'
        main_hitrate = "{0:.2f}".format((main_hits/main_shots)*100) + "%" if main_shots > 0 else '0%'
        second_hitrate = "{0:.2f}".format((second_hits/second_shots)*100) + "%" if second_shots > 0 else '0%'
        torp_hitrate = "{0:.2f}".format((torp_hits/torp_shots)*100) + "%" if torp_shots > 0 else '0%'

        eb.add_field(name='Battles', value=str(battles))  # 0
        eb.add_field(name='Max Experience', value=max_xp)  # 5
        eb.add_field(name='Main Battery Hit Rate', value=main_hitrate)  # 10

        eb.add_field(name='Win Rate', value=win_rate)  # 1
        eb.add_field(name='Average Kills', value=avg_kills)  # 6
        eb.add_field(name='Secondary Battery Hit Rate', value=second_hitrate)  # 11

        eb.add_field(name='Average Damage', value=avg_dmg)  # 2
        eb.add_field(name='Average Plane Kills', value=avg_plane_kills)  # 7
        eb.add_field(name='Torpedo Hit Rate', value=torp_hitrate)  # 12

        eb.add_field(name='Max Damage', value=max_damage_dealt)  # 3
        eb.add_field(name='Max Planes Killed', value=max_planes_killed)  # 8
        eb.add_field(name='Survival Rate', value=survival_rate)  # 13

        eb.add_field(name='Average Experience', value=avg_exp)  # 4
        eb.add_field(name='Average Ships Spotted', value=avg_spotted)  # 9
        eb.add_field(name='Kills/Deaths', value=kda)  # 14

    else:
        eb.add_field(name='Error', value='The player doesn\'t have any battles played')

    return eb
