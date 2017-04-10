"""The main bot run file"""
from discord import game
from os.path import join
from helpers import read_json, fopen_generic
from shell.yasen import Yasen

if __name__ == '__main__':
    description = 'Yo Teitoku, Yasennnnn!'
    prefix = '!'
    my_apis = read_json(fopen_generic(join('data', 'beta_api_keys.json')))
    bot = Yasen(prefix, description, my_apis, None)
    cogs = []

    @bot.event
    async def on_ready():
        """
        Event for when bot is ready
        :return: nothing
        :rtype: None
        """
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')
        await bot.change_presence(game=game.Game(name='?help | ?info'))

    bot.start_bot(cogs)
