"""Handles mointoring of text channels"""
from cleverbot import Cleverbot
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
        self.clever = {}
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
        author_name = message.author.name
        lowerstr = str(message.content).lower()
        # Clever bot functions
        if message.content.startswith(self.bot_id or self.bot_nick):
            if message.content.startswith(self.bot_id):
                temp_bot_id = self.bot_id
            else:
                temp_bot_id = self.bot_nick
            if author_name not in self.clever:
                self.clever[author_name] = Cleverbot(author_name)
            await self.bot.send_message(message.channel, "To <@{}>: ".format(message.author.id) + self.clever
                                        [author_name].ask(message.content.replace(temp_bot_id, '')))
        # Sends ayaya pic when someone says ayaya
        elif "ayaya" in lowerstr and not lowerstr.startswith("enqueued ") and not lowerstr.startswith("now playing "):
            await self.bot.send_message(message.channel, "http://i.imgur.com/g3Qi8Ft.png")
        # Respnods to /o/ and \o\
        elif message.content == "/o/" and str(message.author) != self.bot_name:
            await self.bot.send_message(message.channel, '\\o\\')
        elif message.content == "\\o\\" and str(message.author) != self.bot_name:
            await self.bot.send_message(message.channel, '/o/')
        # Sends a random lewd pic when someone says lewd
        elif message.content.lower() == "lewd" and str(message.author) != self.bot_name:
            await self.bot.send_message(message.channel, choice(self.lewd))
