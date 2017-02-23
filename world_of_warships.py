"""World of Warships commands for this bot"""
from discord.ext import commands
import requests
import json
from helpers import format_eq, generate_image_online, read_json, write_json


class WorldOfWarships:
    """ WoWs commands """
    def __init__(self, bot, wows_api):
        self.bot = bot
        self.wows_api = wows_api
        self.shame_list = read_json('shamelist.json')
        na_ships_url = 'https://api.worldofwarships.com/wows/' \
                       'encyclopedia/ships/?application_id={}'.format(self.wows_api)
        na_ship_api_response = requests.get(na_ships_url).text
        na_ships_json_data = json.loads(na_ship_api_response)
        write_json('na_ships.json', na_ships_json_data)
        self.na_ships = read_json('na_ships.json')['data']

    @commands.command(pass_context=True)
    async def ship(self, ctx, *input_: str):
        """ look for a ship on the wargaming wiki"""
        if ctx.message.server is not None and ctx.message.server.id == '229386752861798401':
            return
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
        if ctx.message.server is not None and ctx.message.server.id == '229386752861798401':
            return
        if region not in ['NA', 'EU', 'RU', 'AS']:
            await self.bot.say('Region must be in ' + str(['NA', 'EU', 'RU', 'AS']) + ' or blank for default(NA)')
            return
        if ctx.message.server is not None:
            server_id = ctx.message.server.id
            if user_name.startswith('<@!'):
                user_name = '<@' + user_name[3:-1] + '>'
            if server_id in self.shame_list and user_name in self.shame_list[server_id]:
                url = "http://na.warshipstoday.com/signature/{}/dark.png".format(self.shame_list[server_id][user_name])
                fn = generate_image_online(url)
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

        fn = generate_image_online(url)
        await self.bot.send_file(ctx.message.channel, fn)

    @commands.command(pass_context=True)
    async def shamelist(self, ctx):
        """Get the entire shame shamelist"""
        if ctx.message.server is None or ctx.message.server.id == '229386752861798401':
            return
        res = []
        for key in self.shame_list[ctx.message.server.id]:
            id_ = key[2:-1]
            res.append(ctx.message.server.get_member(id_).name)

        res_str = '```' + ', '.join(res) + '```'
        await self.bot.say('You can be shamed by pings if you are in the shamelist! Use the `?addshame` command '
                           'with your WoWs username to add yourself to '
                           'the shamelist and use the `?removeshame` command '
                           'without any other inputs to remove you from the shamelist')
        await self.bot.say(res_str)

    @commands.command(pass_context=True)
    async def addshame(self, ctx, user_name: str):
        """Add you to the shame shamelist"""
        if ctx.message.server is None or ctx.message.server.id == '229386752861798401':
            return
        new_entry = False
        user_id = "<@" + str(ctx.message.author.id) + ">"
        server_id = ctx.message.server.id
        request_url = "https://api.worldofwarships.com/wows/account/list/?" \
                      "application_id={}&search={}".format(self.wows_api, user_name)
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
        if ctx.message.server.id not in self.shame_list:
            self.shame_list[server_id] = {}
            new_entry = True
        if user_id not in self.shame_list[server_id]:
            self.shame_list[server_id][user_id] = None
            new_entry = True
        self.shame_list[ctx.message.server.id][user_id] = playerid
        write_json('shamelist.json', self.shame_list)
        self.shame_list = read_json('shamelist.json')
        await self.bot.say('Add success!') if new_entry else await self.bot.say('Edit Success!')

    @commands.command(pass_context=True)
    async def removeshame(self, ctx):
        """Remove you from the shame shamelist"""
        if ctx.message.server is None or ctx.message.server.id == '229386752861798401':
            return
        server_id = ctx.message.server.id
        if "<@" + str(ctx.message.author.id) + ">" in self.shame_list[server_id]:
            self.shame_list[server_id].pop("<@" + str(ctx.message.author.id) + ">", None)
            write_json('shamelist.json', self.shame_list)
            self.shame_list = read_json('shamelist.json')
            await self.bot.say('Remove success!')
        else:
            await self.bot.say('Removed failed, you were not in the shamelist to begin with.')
