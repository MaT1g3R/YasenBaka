"""World of Warships commands for this bot"""
from discord.ext import commands
import requests
import json
from helpers import format_eq, generate_image_online, read_json, write_json, get_server_id, is_admin


class WorldOfWarships:
    """ WoWs commands """
    def __init__(self, bot, wows_api):
        self.bot = bot
        self.wows_api = wows_api
        self.shame_list = read_json('data//shamelist.json')
        na_ships_url = 'https://api.worldofwarships.com/wows/' \
                       'encyclopedia/ships/?application_id={}'.format(self.wows_api)
        na_ship_api_response = requests.get(na_ships_url).text
        na_ships_json_data = json.loads(na_ship_api_response)
        write_json('data//na_ships.json', na_ships_json_data)
        self.na_ships = read_json('data//na_ships.json')['data']
        self.ssheet = read_json('data//sheet.json')
        self.day_list = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
        self.day_dict = {
                'sun': 'Sunday',
                'mon': 'Monday',
                'tue': 'Tuesday',
                'wed': 'Wednesday',
                'thu': 'Thursday',
                'fri': 'Friday',
                'sat': 'Saturday'
            }

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
        result.append('Tier: {}' .format(ship_dict['tier']))
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
    async def shame(self, ctx, user_name: str, region: str= 'NA'):
        """Get shamed by a bot"""
        if region not in ['NA', 'EU', 'RU', 'AS']:
            await self.bot.say('Region must be in ' + str(['NA', 'EU', 'RU', 'AS']) + ' or blank for default(NA)')
            return
        if ctx.message.server is not None:
            server_id = ctx.message.server.id
            if user_name.startswith('<@!'):
                user_name = user_name[3:-1]
            elif user_name.startswith('<@'):
                user_name = user_name[2:-1]

            if server_id in self.shame_list and user_name in self.shame_list[server_id]:
                url = "http://{}.warshipstoday.com/signature/{}/dark.png".format(
                    self.shame_list[server_id][user_name][0], self.shame_list[server_id][user_name][1])
                fn = generate_image_online(url, 'data//shame.png')
                await self.bot.send_file(ctx.message.channel, fn)
                return

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
        try:
            if json_data["meta"]["count"] < 1:
                await self.bot.say("Can't find player")
                return
        except KeyError:
            await self.bot.say("Can't find player")
            return

        playerid = json_data["data"][0]["account_id"]

        urls = {'NA': "http://na.warshipstoday.com/signature/{}/dark.png".format(playerid),
                'EU': 'http://eu.warshipstoday.com/signature/{}/dark.png'.format(playerid),
                'RU': 'http://ru.warshipstoday.com/signature/{}/dark.png'.format(playerid),
                'AS': 'http://asia.warshipstoday.com/signature/{}/dark.png'.format(playerid)}
        url = urls[region]

        fn = generate_image_online(url, 'data//shame.png')
        await self.bot.send_file(ctx.message.channel, fn)

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
    async def addshame(self, ctx, user_name: str, region: str= 'NA'):
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
        region_codes ={
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
        write_json('data//shamelist.json', self.shame_list)
        self.shame_list = read_json('data//shamelist.json')
        await self.bot.say('Add success!') if new_entry else await self.bot.say('Edit Success!')

    @commands.command(pass_context=True)
    async def removeshame(self, ctx):
        """Remove you from the shame shamelist"""
        server_id = ctx.message.server.id
        if str(ctx.message.author.id) in self.shame_list[server_id]:
            self.shame_list[server_id].pop(str(ctx.message.author.id), None)
            write_json('data//shamelist.json', self.shame_list)
            self.shame_list = read_json('data//shamelist.json')
            await self.bot.say('Remove success!')
        else:
            await self.bot.say('Removed failed, you were not in the shamelist to begin with.')

    @commands.command(pass_context=True)
    async def newsheet(self, ctx):
        if not is_admin(ctx, ctx.message.author.id):
            await self.bot.say('This is an admin only command!')
        else:
            self.ssheet[str(get_server_id(ctx))] = {}
            write_json('data//sheet.json', self.ssheet)
            self.ssheet = read_json('data//sheet.json')
            await self.bot.say('New spread sheet created! The old one has been removed!')

    @commands.command(pass_context=True)
    async def addmatch(self, ctx, dayinweek: str, *datetime):
        if not is_admin(ctx, ctx.message.author.id):
            await self.bot.say('This is an admin only command!')
        elif str(get_server_id(ctx)) not in self.ssheet:
            await self.bot.say('Your server doesn\'t seem to have a spreadsheet, please consult `?help newsheet`')
        else:
            dayinweek = dayinweek[:3].lower()
            if dayinweek not in self.day_list:
                await self.bot.say('Please enter a vaild day in the week!')
                return
            datetime = ' '.join(datetime)
            self.ssheet[str(get_server_id(ctx))][dayinweek] = {}
            self.ssheet[str(get_server_id(ctx))][dayinweek]['time'] = datetime
            self.ssheet[str(get_server_id(ctx))][dayinweek]['players'] = []
            write_json('data//sheet.json', self.ssheet)
            self.ssheet = read_json('data//sheet.json')
            await self.bot.say('Match on {} added!'.format(self.day_dict[dayinweek]))

    @commands.command(pass_context=True)
    async def removematch(self, ctx, dayinweek):
        if not is_admin(ctx, ctx.message.author.id):
            await self.bot.say('This is an admin only command!')
        elif str(get_server_id(ctx)) not in self.ssheet:
            await self.bot.say('Your server doesn\'t seem to have a spreadsheet, please consult `?help newsheet`')
        elif dayinweek[:3].lower() not in self.ssheet[str(get_server_id(ctx))]:
            await self.bot.say('There doesn\'t seem to be a match on that day.')
        else:
            del self.ssheet[str(get_server_id(ctx))][dayinweek]
            write_json('data//sheet.json', self.ssheet)
            self.ssheet = read_json('data//sheet.json')
            await self.bot.say('Match on {} removed!'.format(self.day_dict[dayinweek]))

    @commands.command(pass_context=True)
    async def joinmatch(self, ctx, *dayinweek):
        if str(get_server_id(ctx)) not in self.ssheet:
            await self.bot.say('Your server doesn\'t seem to have a spreadsheet, please consult `?help newsheet`')
            return
        dayinweek = [s[:3].lower() for s in dayinweek]
        vaild = dayinweek != []
        for day in dayinweek:
            if day not in self.day_list:
                vaild = False
                break
        if not vaild:
            await self.bot.say('Wrong day in week format, join match aborted, '
                               'no data has been saved to the spread sheet.')
            return
        else:
            no_match_day = [s for s in dayinweek if s not in self.ssheet[str(get_server_id(ctx))]]
            yes_match_day = [s for s in dayinweek if s in self.ssheet[str(get_server_id(ctx))]]

            for d in yes_match_day:
                if ctx.message.author.id not in self.ssheet[str(get_server_id(ctx))][d]['players']:
                    self.ssheet[str(get_server_id(ctx))][d]['players'].append(ctx.message.author.id)

            no_match_day = [self.day_dict[d] for d in no_match_day]
            yes_match_day = [self.day_dict[d] for d in yes_match_day]
            yes_str = ' ,'.join(yes_match_day)
            no_str = ' ,'.join(no_match_day)
            write_json('data//sheet.json', self.ssheet)
            self.ssheet = read_json('data//sheet.json')
            await self.bot.say('You joined the matchs on {}!'.format(yes_str))
            if no_str != '':
                await self.bot.say('You couldn\'t join matches on {}'
                                   ' because there\'re no matches on these days.'.format(no_str))

    @commands.command(pass_context=True)
    async def quitmatch(self, ctx, *dayinweek):
        if str(get_server_id(ctx)) not in self.ssheet:
            await self.bot.say('Your server doesn\'t seem to have a spreadsheet, please consult `?help newsheet`')
            return
        dayinweek = [s[:3].lower() for s in dayinweek]
        vaild = dayinweek != []
        for day in dayinweek:
            if day not in self.day_list:
                vaild = False
                break
        if not vaild:
            await self.bot.say('Wrong day in week format, quit match aborted, '
                               'no data has been saved to the spread sheet.')
            return
        else:
            quit_days = []
            for day in dayinweek:
                if day in self.ssheet[str(get_server_id(ctx))]:
                    try:
                        self.ssheet[str(get_server_id(ctx))][day]['players'].remove(ctx.message.author.id)
                        quit_days.append(day)
                    except ValueError:
                        continue

            write_json('data//sheet.json', self.ssheet)
            self.ssheet = read_json('data//sheet.json')
            quit_days = [self.day_dict[d] for d in quit_days]
            await self.bot.say('You have quit the matches on: {}'.format(' ,'.join(quit_days)))

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
                res = sorted(
                    [
                        '{}: {}\nPlayes: {}\nPlayer count: {}'.format(
                            self.day_dict[key],
                            val['time'],
                            ', '.join([ctx.message.server.get_member(player).name for player in val['players']]),
                            len(val['players'])
                        )
                        for key, val in self.ssheet[str(get_server_id(ctx))].items()
                        ]
                    , key=lambda x: self.day_list.index(x[:3].lower()))

                await self.bot.say('```{}```'.format('\n\n'.join(res)))
