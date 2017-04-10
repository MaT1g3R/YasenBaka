"""
The yasen bot object
"""
from discord.ext.commands import Bot


class Yasen(Bot):
    """
    The yasen bot object
    """
    def __init__(self, prefix, description, api_keys: dict, data):
        """
        Initialize a bot object
        :param prefix the prefix this bot will use
        :param description the description of this bot
        :param api_keys: the api keys used by this bot
        :param data: the data this bot will store
        """
        super().__init__(command_prefix=prefix, description=description)
        self.api_keys = api_keys
        self.data = data

    def start_bot(self, cogs):
        """
        Start the bot
        :param cogs: the cogs to add to this bot
        """
        self.remove_command('help')
        for cog in cogs:
            self.add_cog(cog)
        self.run(self.api_keys['Discord'])
