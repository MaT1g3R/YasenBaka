"""The main bot run file"""
from os.path import join
from discord import game
import stackexchange
from wowspy.wowspy import Wows

# Core imports
from core.data_class import Data
from core.file_system import read_all_files, read_json, write_json, \
    fopen_generic, freadlines
from core.wows_core.wtr_core import coeff_all_region
from core.wows_core.wg_core import get_all_ship_tier


# Bot cog imports
from shell.yasen import Yasen
from shell.util import Util
from shell.fun import Fun
from shell.osu_commands import Osu
from shell.channelreader import ChannelReader
from shell.world_of_warships import WorldOfWarships
from shell.music_player import Music


def data_factory():
    """
    Creates an instance of Data 
    :rtype: Data
    """
    api_keys = read_json(fopen_generic(join('data', 'beta_api_keys.json')))
    wows_api = Wows(api_keys['WoWs'])

    write_json(fopen_generic(join('data', 'na_ships.json'), 'w'),
               wows_api.warships(wows_api.region.NA))

    kanna_files = read_all_files(join('data', 'kanna_is_cute_af'))
    lewds = freadlines(fopen_generic(join('data', 'lewd.txt')))
    lewds.append('( ͡° ͜ʖ ͡°)')
    so = stackexchange.Site(stackexchange.StackOverflow, api_keys[
        'StackExchange'], impose_throttling=True)
    help_message = read_json(fopen_generic(join('data', 'help.json')))
    shame_list = read_json(fopen_generic(join('data', 'shamelist.json')))
    na_ships = read_json(fopen_generic(join('data', 'na_ships.json')))['data']

    coefficients, expected = coeff_all_region()

    ship_dict = get_all_ship_tier(wows_api)

    data = Data(api_keys=api_keys, kanna_files=kanna_files, lewds=lewds, so=so,
                help_message=help_message, shame_list=shame_list,
                na_ships=na_ships, coefficients=coefficients, expected=expected,
                ship_dict=ship_dict, wows_api=wows_api)
    return data

if __name__ == '__main__':
    description = 'Yo Teitoku, Yasennnnn!'
    prefix = '!'
    bot = Yasen(prefix, description, data_factory())
    cogs = [Util(bot), Fun(bot), Osu(bot), ChannelReader(bot),
            WorldOfWarships(bot), Music(bot)]

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
        await bot.change_presence(game=game.Game(name='!help | !info'))

    bot.start_bot(cogs)
