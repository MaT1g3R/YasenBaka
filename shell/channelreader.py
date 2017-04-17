"""Handles mointoring of text channels"""
from core.channel_reader_core import check_message, check_message_startwith,\
    clean_message, linux_meme, interject
from core.program_o import chat_response


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
        elif check_message_startwith(self.bot, message, self.bot.bot_id()) or \
                check_message_startwith(self.bot, message, self.bot.bot_nick()):
            prefix = self.bot.bot_id() if \
                check_message_startwith(self.bot, message, self.bot.bot_id())\
                else self.bot.bot_nick()
            cleaned = clean_message(message, prefix)
            if linux_meme(cleaned):
                await self.bot.send_message(message.channel, interject())
            else:
                res = chat_response(cleaned, message.author.id)
                await self.bot.send_message(message.channel, res)

