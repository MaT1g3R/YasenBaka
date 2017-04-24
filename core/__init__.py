from os.path import join

import stackexchange
from pybooru import Danbooru
from wowspy.wowspy import Wows

from config import api
from core.data_class import Data
from core.file_system import fopen_generic, read_json, read_all_files, \
    write_json, freadlines
from core.wows_core.wg_core import get_all_ship_tier
from core.wows_core.wtr_core import coeff_all_region


def data_factory():
    """
    Creates an instance of Data 
    :rtype: Data
    """
    api_keys = api.API
    wows_api = Wows(api_keys['WoWs'])

    kanna_files = read_all_files(join('data', 'kanna_is_cute_af'))
    so = stackexchange.Site(stackexchange.StackOverflow, api_keys[
        'StackExchange'], impose_throttling=True)

    coefficients, expected = coeff_all_region()

    ship_dict = get_all_ship_tier(wows_api)

    usr, key = api_keys['Danbooru']
    danbooru = Danbooru('danbooru', username=usr, api_key=key)
    # avatar = open(join('config', 'avatar.png'), 'rb').read() \
    #     if isfile(join('config', 'avatar.png')) else None

    data = Data(api_keys=api_keys, kanna_files=kanna_files, so=so,
                coefficients=coefficients, expected=expected,
                ship_dict=ship_dict, wows_api=wows_api,
                avatar=None, danbooru=danbooru)
    return data
