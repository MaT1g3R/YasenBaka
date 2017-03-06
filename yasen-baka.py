"""The main bot run file"""
from discord.ext import commands
from music_player import Music
from channelreader import ChannelReader
from discord import game
from fun import Fun
from world_of_warships import WorldOfWarships
from helpers import read_json
from util import Util
from osu_commands import Osu

if __name__ == '__main__':
    description = 'Yo Teitoku, Yasennnnn!'
    yasen_baka = commands.Bot(command_prefix=['?'], description=description)

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
        await yasen_baka.change_presence(game=game.Game(name='?help'))


    my_apis = read_json('data//api_keys.json')

    yasen_baka.remove_command('help')
    yasen_baka.add_cog(Util(yasen_baka, my_apis['StackExchange']))
    yasen_baka.add_cog(Fun(yasen_baka))
    yasen_baka.add_cog(WorldOfWarships(yasen_baka, my_apis['WoWs']))
    yasen_baka.add_cog(Music(yasen_baka))
    yasen_baka.add_cog(ChannelReader(yasen_baka, my_apis['SimSimi']))
    yasen_baka.add_cog(Osu(yasen_baka, my_apis['Osu']))
    yasen_baka.run(my_apis['Discord'])
