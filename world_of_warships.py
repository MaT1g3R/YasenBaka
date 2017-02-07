"""World of Warships commands for this bot"""
from discord.ext import commands
import requests
import json
import urllib.request
import textwrap


class WorldOfWarships:
    """ WoWs commands """
    def __init__(self, bot, wows_api):
        self.bot = bot
        self.wows_api = wows_api
        with open('shamelist.json') as data_file:
            tmp_shame_list = json.load(data_file)
        self.shame_list = tmp_shame_list
        na_ships_url = 'https://api.worldofwarships.com/wows/' \
                       'encyclopedia/ships/?application_id={}'.format(self.wows_api)
        na_ship_api_response = requests.get(na_ships_url).text
        na_ships_json_data = json.loads(na_ship_api_response)
        with open('na_ships.json', 'w') as fp:
            json.dump(na_ships_json_data, fp)
        with open('na_ships.json') as data_file:
            self.na_ships = json.load(data_file)['data']

    @commands.command()
    async def ship(self, *input_: str):
        """ look for a ship on the wargaming wiki"""
        ship_name = ' '.join(input_).title()
        if ship_name.startswith('Arp'):
            ship_name = ship_name.replace('Arp', 'ARP')
        for key, val in self.na_ships.items():
            if val['name'] == ship_name:
                await self.try_say(str(val))
                return
        await self.bot.say('Ship not found!')

    @commands.command(pass_context=True)
    async def shame(self, ctx, user_name: str, region: str= 'NA'):
        """Get shamed by a bot"""
        if region not in ['NA', 'EU', 'RU', 'AS']:
            await self.bot.say('Region must be in ' + str(['NA', 'EU', 'RU', 'AS']) + ' or blank for default(NA)')
            return
        if user_name.startswith('<@!'):
            user_name = '<@' + user_name[3:-1] + '>'
        if user_name in self.shame_list:
            url = "http://na.warshipstoday.com/signature/{}/dark.png".format(self.shame_list[user_name])
            fn = self.generate_image_online(url)
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

        fn = self.generate_image_online(url)
        await self.bot.send_file(ctx.message.channel, fn)

    def generate_image_online(self, url):
        """
        Generates an image file from a image hot link
        :param url: The url
        :type url: str
        :return: The generated image path
        :rtype: str
        """
        fn = url.split('/')[-1]
        urllib.request.urlretrieve(url, fn)
        return fn

    @commands.command(pass_context=True)
    async def shamelist(self, ctx):
        """Get the entire shame shamelist"""
        res = []
        for key in self.shame_list:
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
        old_dict = dict(self.shame_list)
        user_id = "<@" + str(ctx.message.author.id) + ">"
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
        self.shame_list[user_id] = playerid
        with open('shamelist.json', 'w') as fp:
            json.dump(self.shame_list, fp)
        with open('shamelist.json') as data_file:
            self.shame_list = json.load(data_file)
        await self.bot.say('Add success!') if user_id not in old_dict else await self.bot.say('Edit Success!')

    @commands.command(pass_context=True)
    async def removeshame(self, ctx):
        """Remove you from the shame shamelist"""
        if "<@" + str(ctx.message.author.id) + ">" in self.shame_list:
            self.shame_list.pop("<@" + str(ctx.message.author.id) + ">", None)
            with open('shamelist.json', 'w') as fp:
                json.dump(self.shame_list, fp)
            with open('shamelist.json') as data_file:
                self.shame_list = json.load(data_file)
            await self.bot.say('Remove success!')
        else:
            await self.bot.say('Removed failed, you were not in the shamelist to begin with.')

    async def try_say(self, text, i=1):
        """
        Try to say the block of text until the bot succeeds
        :param text: The block of text
        :type text: str | list
        :param i: how many sections the text needs to be split into
        :type i: int
        :return: nothing
        :rtype: None
        """
        try:
            if isinstance(text, list):
                for txt in text:
                    await self.bot.say('```markdown\n'+txt+'```')
            elif isinstance(text, str):
                    await self.bot.say('```markdown\n' + text + '```')
        except Exception:
            i += 1
            await self.try_say(self.split_text(text, i), i)

    def split_text(self, text, i):
        """
        Splits text into a list
        :param text: The text to be splitted
        :type text: str | list
        :param i: the number of sections the text needs to be split into
        :type i: int
        :return: The split up text
        :rtype: list
        """
        if isinstance(text, list):
            text = ''.join(text)
        return textwrap.wrap(text, int(len(text)/i))
