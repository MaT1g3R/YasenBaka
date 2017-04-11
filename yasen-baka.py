"""The main bot run file"""
from os.path import join
from discord import game
import stackexchange
from data_class import Data
from file_system import read_all_files, read_json, write_json, \
    fopen_generic, freadlines
from wowspy.wowspy import Wows
from yasen import Yasen
from wows_core import coeff_all_region

# Bot cog imports
from util import Util
from fun import Fun
from osu_commands import Osu


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
    sheet_data = read_json(fopen_generic(join('data', 'sheet.json')))

    c_a_r = coeff_all_region()
    coefficients = c_a_r[0]
    expected = c_a_r[1]

    ship_dict = wows_api.warships(wows_api.region.NA, fields='tier')['data']
    ship_list = [k for k in ship_dict.keys()]

    data = Data(api_keys=api_keys, kanna_files=kanna_files, lewds=lewds, so=so,
                help_message=help_message, shame_list=shame_list,
                na_ships=na_ships, sheet_data=sheet_data,
                coefficients=coefficients, expected=expected,
                ship_dict=ship_dict, ship_list=ship_list, wows_api=wows_api)
    return data

if __name__ == '__main__':
    description = 'Yo Teitoku, Yasennnnn!'
    prefix = '!'
    bot = Yasen(prefix, description, data_factory())
    cogs = [Util(bot), Fun(bot), Osu(bot)]

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
