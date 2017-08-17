import re
from datetime import datetime
from html import unescape
from pathlib import Path
from random import choice, random
from typing import List, Tuple, Union

from aiohttp_wrapper import SessionManager
from discord import Embed, File
from minoshiro import Medium, Site

from bot.anime_searcher import AnimeSearcher
from core.nsfw_core import get_lewd
from data_manager import DataManager

colours = {
    Medium.ANIME: 0x1660A5,
    Medium.MANGA: 0x2fbf56,
    Medium.LN: 0x994647
}

site_names = {
    Site.MAL: 'MAL',
    Site.ANILIST: 'AL',
    Site.ANIMEPLANET: 'A-P',
    Site.ANIDB: 'A-DB',
    Site.KITSU: 'KIT',
    Site.MANGAUPDATES: 'MU',
    Site.LNDB: 'LNDB',
    Site.NOVELUPDATES: 'NU'
}


async def random_picture(files: List[Path], tags: Tuple[str],
                         session_manager: SessionManager,
                         data_manager: DataManager) -> Union[File, str]:
    """
    Returns a random file from local and safebooru with safebooru tags.
    :param files: list of local files.
    :param tags: a tuple of safebooru tags.
    :param session_manager: the SessionManager.
    :param data_manager: the data manager.
    :return: a random image
    """
    file = File(str(choice(files)))
    if random() < 0.5:
        return file
    _, url, __ = await get_lewd(
        session_manager, 'safebooru', tags, data_manager)
    return url or file


async def search_weeb(ctx, search, medium):
    """
    Search for an anime/manga/light novel.
    :param ctx: Discord context
    :param search: the search term.
    :param medium: the medium type.
    """
    if not search:
        await ctx.send('Please enter a search term.')
        return
    async with ctx.typing():
        res, to_be_cached, names, medium = await get_weeb_res(
            ctx.bot.anime_search, search, medium
        )
    if isinstance(res, str):
        await ctx.send(res)
    else:
        await ctx.send(embed=res)
    if to_be_cached and names:
        await ctx.bot.anime_search.cache(to_be_cached, names, medium)


async def get_weeb_res(ani_search: AnimeSearcher, search, medium):
    """
    Get result for weeb search.
    :param ani_search: the `AnimeSearcher`
    :param search: the search term.
    :param medium: the medium type.
    :return: A tuple of (Search result, to_be_cached, names, medium)
    """
    data, to_be_cached, names, medium = await ani_search.get(search, medium)
    if not data:
        return 'Sorry, nothing found.', to_be_cached, names, medium
    return make_embed(data, medium), to_be_cached, names, medium


def make_embed(data, medium):
    """
    Make the embed for the weeb search.
    :param data: All of the data for the search.
    :param medium: the medium type.
    :return: An embed if the search was found, else an error message.
    """
    mal = data.get(Site.MAL, {})
    anilist = data.get(Site.ANILIST, {})
    kitsu = data.get(Site.KITSU, {})
    kitsu_attr = kitsu.get('attributes', {})
    mu = data.get(Site.MANGAUPDATES, {})
    anidb = data.get(Site.ANIDB, {})
    nu = data.get(Site.NOVELUPDATES, {})
    name = get_name(mal, anilist, kitsu_attr, anidb, mu, nu)
    if not name:
        return 'Sorry, nothing found.'
    colour = colours[medium]
    des = []
    type_ = get_type(mal, kitsu_attr)
    status = get_status(mal, anilist, kitsu_attr)
    length = get_len(medium, mal, anilist, kitsu_attr)
    genres = get_genres(anilist)
    if type_:
        des.append(type_.title())
    if status:
        des.append(f'Status: {status.title()}')
    if length:
        des.append(length)
    if genres:
        des.append(f'Genres: {", ".join(genres)}')
    embed = Embed(colour=colour, title=name)
    if des:
        embed.description = ' | '.join(des)
    pic = get_pic(mal, anilist, kitsu_attr)
    if pic:
        embed.set_image(url=pic)
    airing_info = get_airing(mal, anilist, kitsu_attr)
    if airing_info:
        embed.add_field(name=':calendar: Publishing info', value=airing_info)

    rating = get_rating(anilist, kitsu_attr, mu)
    if rating:
        embed.add_field(name=':star: Ratings', value=rating)
    synopsis = get_synopsis(mal, anilist, kitsu_attr)
    if synopsis:
        embed.add_field(name=':blue_book: Synopsis', value=synopsis,
                        inline=False)
    links = get_links(data)
    if links:
        embed.add_field(name=':link: Links', value=links, inline=False)
    return embed


def get_synopsis(mal, anilist, kitsu_attr):
    """
    Get the synopsis for the weeb search.
    :param mal: The MAL search result.
    :param anilist: The anilist search result.
    :param kitsu_attr: The attributes of kitsu search result.
    :return:
    """
    synopsis = mal.get('synopsis')
    anilist_des = anilist.get('description')
    if anilist_des and (not synopsis or len(anilist_des) < len(synopsis)):
        synopsis = anilist_des
    kitsu_des = kitsu_attr.get('synopsis')
    if kitsu_des and (not synopsis or len(kitsu_des) < len(synopsis)):
        synopsis = kitsu_des
    if not synopsis:
        return
    synopsis = cleanup_des(synopsis.rstrip())
    if len(synopsis) > 1000:
        return f'{synopsis[:1000]}\n......'
    else:
        return synopsis


def cleanup_des(desc):
    """
    Clean up the synopsis.
    :param desc: the raw synopsis.
    :return: cleaned up synopsis.
    """
    cleanr = re.compile('[<\[].*?[>\]]')
    cleantext = re.sub(cleanr, '', desc)
    return unescape(cleantext)


def get_name(mal, anilist, kitsu_attr, anidb, mu, nu):
    """
    Get the name of the search.
    :param mal: The MAL search result.
    :param anilist: The anilist search result.
    :param kitsu_attr: The attributes of kitsu search result.
    :param anidb: The anidb search result.
    :param mu: The manga updates search result.
    :param nu: The novel updates search result.
    :return: The name of the search.
    """
    mal_name = mal.get('title')
    if mal_name:
        return mal_name

    anilist = anilist.get('title', {})
    anilist_name = extract(anilist, ('english', 'romaji', 'native'))
    if anilist_name:
        return anilist_name

    kitsu = kitsu_attr.get('titles', {})
    kitsu_name = extract(kitsu, ('en', 'en_jp', 'ja_jp'))
    if kitsu_name:
        return kitsu_name

    anidb = anidb.get('titles')
    if anidb:
        return anidb[0]

    manga_updates = mu.get('title')
    if manga_updates:
        return manga_updates

    novel_updates = nu.get('title')
    if novel_updates:
        return novel_updates


def get_type(mal, kitsu_attr):
    """
    Get the type of the weeb media.
    :param mal: The MAL search result.
    :param kitsu_attr: The attributes of kitsu search result.
    :return: the type of the weeb media
    """
    mal_type = mal.get('type')
    if mal_type:
        return mal_type

    show_type = kitsu_attr.get('showType')
    subtype = kitsu_attr.get('subtype')
    if show_type or subtype:
        return show_type or subtype


def get_status(mal, anilist, kitsu_attr):
    """
    Get the airing status of the search.
    :param mal: The MAL search result.
    :param anilist: The anilist search result.
    :param kitsu_attr: The attributes of kitsu search result.
    :return: the airing status of the search.
    """
    mal_status = mal.get('status')
    if mal_status:
        return mal_status

    anilist_status = anilist.get('status')
    if anilist_status:
        return anilist_status

    kitsu_status = kitsu_attr.get('status')
    if kitsu_status:
        return kitsu_status


def get_airing(mal, anilist, kitsu_attr):
    """
    Get the airing dates for the search.
    :param mal: The MAL search result.
    :param anilist: The anilist search result.
    :param kitsu_attr: The attributes of kitsu search result.
    :return: the airing dates for the search.
    """

    def anilist_date(d):
        if not d:
            return
        year = d.get('year')
        month = d.get('month')
        day = d.get('day')
        if not (year and month and day):
            return
        return f'{year}-{month}-{day}'

    start = None
    end = None
    next_ = None

    mal_start = mal.get('start_date')
    if mal_start and not mal_start.startswith('0000'):
        start = mal_start

    mal_end = mal.get('end_date')
    if mal_end and not mal_end.startswith('0000'):
        end = mal_end

    anilist_start = anilist.get('startDate')
    if not start:
        start = anilist_date(anilist_start)

    anilist_end = anilist.get('endDate')
    if not end:
        end = anilist_date(anilist_end)

    anilist_next = anilist.get('nextAiringEpisode', {})

    if anilist_next:
        anilist_next = anilist_next.get('airingAt')
        try:
            next_ = datetime.fromtimestamp(anilist_next).strftime('%Y-%m-%d')
        except TypeError:
            next_ = None

    kitsu_start = kitsu_attr.get('startDate')
    if not start:
        start = kitsu_start
    kitsu_end = kitsu_attr.get('endDate')
    if not end:
        end = kitsu_end

    if start and end:
        return f'Start date: {start} | End date: {end}'
    elif start and next_:
        return f'Start date: {start} | Next: {next_}'
    elif start:
        return f'Start date: {start}'
    elif next_:
        return f'Next: {next_}'


def get_len(medium, mal, anilist, kitsu_attr):
    """
    Get the length of the search.
    :param medium: the medium type.
    :param mal: The MAL search result.
    :param anilist: The anilist search result.
    :param kitsu_attr: The attributes of kitsu search result.
    :return: the length of the search.
    """
    if medium == Medium.ANIME:
        noun = 'Episodes'
        anilist_mal_key = 'episodes'
        kitsu_key = 'episodeCount'
    else:
        noun = 'Volumes'
        anilist_mal_key = 'volumes'
        kitsu_key = 'volumeCount'

    mal_len = mal.get(anilist_mal_key)
    if mal_len and mal_len != '0':
        return f'{noun}: {mal_len}'

    anilist_len = anilist.get(anilist_mal_key)
    if anilist_len:
        return f'{noun} {anilist_len}'

    kitsu_len = kitsu_attr.get(kitsu_key)
    if kitsu_len:
        return f'{noun} {kitsu_len}'


def get_genres(anilist):
    """
    Get the genres for the search.
    :param anilist: The anilist search result.
    :return: the genres for the search.
    """
    lst = anilist.get('genres', [])
    if not lst:
        return
    return [s for s in lst if s]


def get_links(data):
    """
    Get all links for the search.
    :param data: all of the search data.
    :return: all links for the search.
    """
    res = []
    for site in Site:
        site_data = data.get(site, {})
        url = site_data.get('url')
        if url:
            res.append(f'[{site_names[site]}]({url})')
    return ' | '.join(res) if res else None


def get_rating(anilist, kitsu_attr, mu):
    """
    Get the rating for the search.
    :param anilist: The anilist search result.
    :param kitsu_attr: The attributes of kitsu search result.
    :param mu: The manga updates search result.
    :return: the rating for the search.
    """
    res = []
    anilist_rating = anilist.get('meanScore')
    if anilist_rating:
        res.append(f'Anilist - {anilist_rating}/100')
    kitsu_rating = kitsu_attr.get('averageRating')
    if kitsu_rating:
        res.append(f'Kitsu - {kitsu_rating}/100')
    mu_rating = mu.get('rating')
    if mu_rating:
        res.append(f'Manga Updates - {mu_rating}/10')
    return '\n'.join(res) if res else None


def get_pic(mal, anilist, kitsu_attr):
    """
    Get the image url for the search.
    :param mal: The MAL search result.
    :param anilist: The anilist search result.
    :param kitsu_attr: The attributes of kitsu search result.
    :return: the image url for the search.
    """
    kitsu_img = kitsu_attr.get('coverImage', {})
    kitsu_img = extract(kitsu_img, ('original', 'large'))
    if kitsu_img:
        return kitsu_img

    anilist_img = anilist.get('coverImage', {})
    anilist_img = extract(anilist_img, ('large', 'medium'))
    if anilist_img:
        return anilist_img
    mal_img = mal.get('image')
    if mal_img:
        return mal_img


def extract(d, keys):
    """
    Extract a key from a dict.
    :param d: The dict.
    :param keys: A list of keys, in order of priority.
    :return: The most important key with an value found.
    """
    if not d:
        return
    for key in keys:
        tmp = d.get(key)
        if tmp:
            return tmp
