"""Handles mointoring of text channels"""
import cleverbot_io
cleverbot = cleverbot_io.set(user='XXXXXXXXXXXXXXXX', key='XXXXXXXXXXXXXXXX', nick='yasenbaka')

class ChannelReader:
    """
    Channel reading functions
    """

    def __init__(self, bot):
        self.bot = bot

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

    def check_message(self, message, expected):
        """
        A helper method to check if a message's content matches with expected result and the author isn't the bot.
        :param message: the message to be checked
        :param expected: the expected result
        :return: true if the message's content equals the expected result and the author isn't the bot
        """
        return message.content == expected and message.author.id != self.bot.user.id

    async def on_message(self, message):
        """
        Events for read messages
        :param message: A discord message
        :type message: disord.message
        :return: nothing
        :rtype: None
        """
        # Converted to comments because the disgust of these triggers lol
        # if self.check_message(message, '/o/'):
        #     await self.bot.send_message(message.channel, '\\o\\')
        # elif self.check_message(message, '\\o\\'):
        #     await self.bot.send_message(message.channel, '/o/')
        # elif self.check_message(message, 'o7'):  # Yousoro!
        #     await self.bot.send_message(message.channel, 'http://i.imgur.com/Pudz3G4.gif')

        if message.content.startswith(self.bot_id()):
            await self.bot.send_message(message.channel, ':speech_left: ' + cleverbot.ask(message.content[22:]))
        elif message.content.startswith(self.bot_nick()):
            await self.bot.send_message(message.channel, ':speech_left: ' + cleverbot.ask(message.content[23:]))
