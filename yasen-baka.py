"""The main bot run file"""
from discord.ext import commands
from latex import LaTeX
from music_player import Music
from channelreader import ChannelReader
from discord import game
from main_commands import Commands
from world_of_warships import WorldOfWarships
import json

if __name__ == '__main__':
    description = 'Yo Teitoku, Yasennnnn!'
    yasen_baka = commands.Bot(command_prefix=['!', '?', 'pip '], description=description)

    @yasen_baka.event
    async def on_ready():
        """
        Event for when bot is ready
        :return: nothing
        :rtype: None
        """
        print('Logged in as')
        print(yasen_baka.user.name)
        print(yasen_baka.user.id)
        print('------')
        await yasen_baka.change_presence(game=game.Game(name='Yasen'))

    with open('api_keys.json') as data_file:
        my_apis = json.load(data_file)
    yasen_baka.remove_command('help')
    yasen_baka.add_cog(Commands(yasen_baka, my_apis['StackExchange']))
    yasen_baka.add_cog(WorldOfWarships(yasen_baka, my_apis['WoWs']))
    yasen_baka.add_cog(Music(yasen_baka))
    yasen_baka.add_cog(LaTeX(yasen_baka))
    yasen_baka.add_cog(ChannelReader(yasen_baka))
    yasen_baka.run(my_apis['Discord'])
