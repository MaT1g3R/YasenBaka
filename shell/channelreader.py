"""Handles mointoring of text channels"""
from channel_reader_core import check_message


class ChannelReader:
    """
    Channel reading functions
    """

    def __init__(self, bot):
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
        if check_message(self.bot, message, '/o/'):
            await self.bot.send_message(message.channel, '\\o\\')
        elif check_message(self.bot, message, '\\o\\'):
            await self.bot.send_message(message.channel, '/o/')
        elif check_message(self.bot, message, 'o7'):  # Yousoro!
            await self.bot.send_message(message.channel,
                                        'http://i.imgur.com/Pudz3G4.gif')
