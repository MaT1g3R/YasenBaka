"""
The yasen bot object
"""
from discord.ext.commands import Bot

from core.helpers import split_text


class Yasen(Bot):
    """
    The yasen bot object
    """

    def __init__(self, prefix, description, data):
        """
        Initialize a bot object
        :param prefix the prefix this bot will use
        :param description the description of this bot
        :param data: the data this bot will store
        """
        super().__init__(command_prefix=prefix, description=description)
        self.data = data

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
        except Exception:
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

