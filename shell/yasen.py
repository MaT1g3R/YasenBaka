"""
The yasen bot object
"""
from discord.ext.commands import Bot


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
