from pathlib import Path
from random import choice, random
from typing import List, Tuple, Union

from aiohttp_wrapper import SessionManager
from discord import Embed, File
from minoshiro import Medium

from bot.anime_searcher import AnimeSearcher
from core.nsfw_core import get_lewd
from data_manager import DataManager

colours = {
    Medium.ANIME: 0x1660A5,
    Medium.MANGA: 0x2fbf56,
    Medium.LN: 0x994647
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
    if not search:
        await ctx.send('Please enter a search term.')
        return
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
    data, to_be_cached, names, medium = await ani_search.get(search, medium)
    if not data:
        return 'Sorry, nothing found.', to_be_cached, names, medium
    return make_embed(data, colours[medium]), to_be_cached, names, medium


def make_embed(data, colour):
    embed = Embed(colour=colour)
