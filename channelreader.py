"""Handles mointoring of text channels"""
import requests
import json
import time


class ChannelReader:
    """
    Channel reading functions
    """

    def __init__(self, bot, key):
        self.bot = bot
        self.key = key
        self.surl = 'http://api.simsimi.com/request.p?key={}&ft=1.0&lc=en&text={}'
        self.start_time = None
        self.end_time = None

    def bot_id(self):
        """
        Returns bot id
        :rtype str
        """
        return '<@%s>' % self.bot.user.id

    def bot_nick(self):
        """
        Returns bot nicknameÒ
        :rtype str
        """
        return '<@!%s>' % self.bot.user.id

    def bot_name(self):
        """
        Returns bot name with discriminator
        :rtype str
        """
        return '%s#%s' % (self.bot.user.name, self.bot.user.discriminator)

    async def on_message(self, message):
        """
        Events for read messages
        :param message: A discord message
        :type message: disord.message
        :return: nothing
        :rtype: None
        """
        # Respnods to /o/ and \o\
        if message.content == "/o/" and message.author.id != self.bot.user.id:
            await self.bot.send_message(message.channel, '\\o\\')
        elif message.content == "\\o\\" and message.author.id != self.bot.user.id:
            await self.bot.send_message(message.channel, '/o/')

        if message.content.startswith(self.bot_id()):
            msg = message.content[22:]
            r = json.loads(requests.get(self.surl.format(self.key, msg)).text)
            await self.bot.send_message(message.channel, r['response'])
        elif message.content.startswith(self.bot_nick()):
            msg = message.content[23:]
            r = json.loads(requests.get(self.surl.format(self.key, msg)).text)
            await self.bot.send_message(message.channel, r['response'])
        elif message.content == '?ping':
            self.start_time = int(round(time.time() * 1000))
            msg = await self.bot.send_message(message.channel, 'Pong! :hourglass:')
            self.end_time = int(round(time.time() * 1000))
            await self.bot.edit_message(msg, 'Pong! | :timer: {}ms'.format(self.end_time - self.start_time))
