"""Handles mointoring of text channels"""
import requests
import json


class ChannelReader:
    """
    Channel reading functions
    """
    def __init__(self, bot, key):
        self.bot_id = '<@243230010532560896>'
        self.bot_nick = '<@!243230010532560896>'
        self.bot_name = 'Yasen-Baka#6539'
        self.bot = bot
        self.key = key
        self.surl = 'http://api.simsimi.com/request.p?key={}&ft=1.0&lc=en&text={}'
    async def on_message(self, message):
        """
        Events for read messages
        :param message: A discord message
        :type message: disord.message
        :return: nothing
        :rtype: None
        """
        # Respnods to /o/ and \o\
        if message.content == "/o/" and str(message.author) != self.bot_name:
            await self.bot.send_message(message.channel, '\\o\\')
        elif message.content == "\\o\\" and str(message.author) != self.bot_name:
            await self.bot.send_message(message.channel, '/o/')

        if message.content.startswith(self.bot_id):
            msg = message.content[22:]
            r = json.loads(requests.get(self.surl.format(self.key, msg)).text)
            await self.bot.send_message(message.channel, r['response'])
        elif message.content.startswith(self.bot_nick):
            msg = message.content[23:]
            r = json.loads(requests.get(self.surl.format(self.key, msg)).text)
            await self.bot.send_message(message.channel, r['response'])
