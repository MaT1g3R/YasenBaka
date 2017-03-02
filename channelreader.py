"""Handles mointoring of text channels"""
from random import choice


class ChannelReader:
    """
    Channel reading functions
    """
    def __init__(self, bot):
        self.bot_id = '<@243230010532560896>'
        self.bot_nick = '<@!243230010532560896>'
        self.bot_name = 'Yasen-Baka#6539'
        self.bot = bot
        with open('lewd.txt') as f:
            self.lewd = f.read().splitlines()
        self.lewd.append('( ͡° ͜ʖ ͡°)')
    async def on_message(self, message):
        """
        Events for read messages
        :param message: A discord message
        :type message: disord.message
        :return: nothing
        :rtype: None
        """
        # Local vars
        lowerstr = message.content.lower()
        # Sends ayaya pic when someone says ayaya
        if "ayaya" in lowerstr and not lowerstr.startswith("enqueued ") and not lowerstr.startswith("now playing "):
            await self.bot.send_message(message.channel, "http://i.imgur.com/g3Qi8Ft.png")
        # Respnods to /o/ and \o\
        elif message.content == "/o/" and str(message.author) != self.bot_name:
            await self.bot.send_message(message.channel, '\\o\\')
        elif message.content == "\\o\\" and str(message.author) != self.bot_name:
            await self.bot.send_message(message.channel, '/o/')
        # Sends a random lewd pic when someone says lewd
        elif message.content.lower() == "lewd" and str(message.author) != self.bot_name:
            await self.bot.send_message(message.channel, choice(self.lewd))

