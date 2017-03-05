"""Handles mointoring of text channels"""


class ChannelReader:
    """
    Channel reading functions
    """
    def __init__(self, bot):
        self.bot_id = '<@243230010532560896>'
        self.bot_nick = '<@!243230010532560896>'
        self.bot_name = 'Yasen-Baka#6539'
        self.bot = bot
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
