"""
The yasen bot object
"""

from discord import game
from discord.ext.commands import Bot, CommandOnCooldown

from core.discord_functions import message_sender
from core.helpers import split_text


class Yasen(Bot):
    """
    The yasen bot object
    """

    def __init__(self, default_prefix, prefix, description,
                 data, cursor, connection, shard_count=1, shard_id=0):
        """
        Initialize a bot object
        :param default_prefix: the default prefix for the bot
        :param prefix the prefix this bot will use
        :param description the description of this bot
        :param data: the data this bot will store
        :param cursor: the database cursor
        :param connection: the database conn
        """
        super().__init__(command_prefix=prefix, description=description,
                         shard_count=shard_count, shard_id=shard_id)
        self.default_prefix = default_prefix
        self.data = data
        self.cursor = cursor
        self.conn = connection
        self.shard_count = shard_count
        self.shard_id = shard_id

    def start_bot(self, cogs):
        """
        Start the bot
        :param cogs: the cogs to add to this bot
        """
        self.remove_command('help')
        for cog in cogs:
            self.add_cog(cog)
        self.run(self.data.api_keys['Discord'])

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
                    await self.say('```markdown\n' + txt + '```')
            elif isinstance(text, str):
                await self.say('```markdown\n' + text + '```')
        except:
            i += 1
            await self.try_say(split_text(text, i), i)

    def bot_id(self):
        """
        Returns the bot id in <@> format
        :return: bot id in <@> format
        """
        return '<@%s>' % self.user.id

    def bot_nick(self):
        """
        Returns the bot id in <@!> format
        :return: the bot id in <@!> format
        """
        return '<@!%s>' % self.user.id

    async def on_command_error(self, exception, context):
        """
        Custom command error handling
        :param exception: the expection raised
        :param context: the context of the command
        """
        if isinstance(exception, CommandOnCooldown):
            await message_sender(self, context.message.channel, str(exception))
        else:
            raise exception

    async def on_ready(self):
        """
        Event for when bot is ready
        :return: nothing
        :rtype: None
        """
        g = '{}help'.format(self.default_prefix)
        if self.shard_count > 1:
            g = '{}/{} | '.format(self.shard_id + 1, self.shard_count) + g
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.change_presence(game=game.Game(name=g))
        if self.data.avatar is not None:
            await self.edit_profile(avatar=self.data.avatar)
