from discord import ChannelType
from pybooru import Danbooru, PybooruAPIError
from requests import get, ConnectionError, HTTPError
from json import loads, decoder
from random import choice
import xml.etree.ElementTree as Et


SORRY = 'Sorry! nothing found'
ERROR = 'Something went wrong with the {} API. ' \
        'Please report this to my owner or await a fix.'
SEARCH = '//post.json?tags={}'


def is_nsfw(ctx):
    """
    Detiremine if nsfw is enabled for this channel
    :param ctx: the context
    :return: if nsfw is enabled in this channel
    """
    return \
        ctx.message.channel.type == ChannelType.private \
        or ctx.message.channel.name.lower() == 'nsfw'


def danbooru(search, api: Danbooru):
    """
    Search danbooru for lewds
    :param search: the search term
    :param api: the danbooru api object
    :return: lewds
    """
    if len(search) > 2:
        return 'You cannot search for more than 2 tags at a time'
    try:
        res = api.post_list(tags=' '.join(search), random=True, limit=1)
    except PybooruAPIError:
        return ERROR.format('Danbooru')
    base = 'https://danbooru.donmai.us'
    return base+res[0]['large_file_url'] \
        if len(res) > 0 and 'large_file_url' in res[0] \
        else SORRY


# def sankaku(search):
#     """
#     Search sankaku for lewdsresources
#     :param search: the search term
#     :return: lewds
#     """
#     # https://safebooru.org//index.php?page=dapi&s=post&q=index&tags={}
#     base = 'https://chan.sankakucomplex.com'
#     r_url = base + '/post.json?tag={}'.format('%20'.join(search))
#     try:
#         res = loads(r_url)
#     except decoder.JSONDecodeError:
#         res = 'Something went wrong with the sankaku API. ' \
#               'Please report this to my owner or await a fix.'


def k_or_y(search, site_name):
    """
    Search konachan or yandere for lewds
    :param site_name: which site to search for 
    :param search: the search term
    :return: lewds
    """
    base = {
        'Konachan': 'https://konachan.com',
        'Yandere': 'https://yande.re'
    }[site_name]
    r_url = base + SEARCH.format('%20'.join(search))
    try:
        res = loads(get(r_url).content)
    except decoder.JSONDecodeError:
        return ERROR.format(site_name)
    if len(res) <= 0:
        return SORRY
    else:
        img = choice(res)['file_url']
        return 'https:' + img if site_name == 'Konachan' else img


def gelbooru(search):
    """
    Search gelbooru for lewds
    :param search: the search term 
    :return: lewds
    """
    url = "https://gelbooru.com//index.php?page=dapi&s=post&q=index&tags={}" \
        .format('%20'.join(search))
    try:
        result = get(url).content
    except ConnectionError and HTTPError:
        return ERROR.format('Gelbooru')
    root = Et.fromstring(result)
    res = ['https:' + child.attrib['file_url'] for child in root]
    return choice(res) if len(res) > 0 else SORRY


if __name__ == '__main__':
    # danbooru = db()
    # r =danbooru.tag_list(name='ass,haruna_(kantai_collection)')
    # r = danbooru.post_list(tags='ass haruna_(kantai_collection)', random=True, limit=1)[0]['large_file_url']
    # print('https://danbooru.donmai.us'+r)
    # print(r)
    # print(gelbooru(['']))
    # print(k_or_y([' haruna_(kancolle)', 'ass'], 'Yandere'))
    pass
