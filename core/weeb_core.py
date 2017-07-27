from pathlib import Path
from random import choice, random
from typing import List, Tuple, Union

from discord import File

from bot import HTTPStatusError, SessionManager
from core.nsfw_core import get_lewd
from data_manager import DataManager


async def wolke_image(session_manager: SessionManager, key: str,
                      type_: str) -> str:
    """
    Search wolke api for image by type.
    :param session_manager: the SessionManager instance.
    :param key: the api key.
    :param type_: the type of the image.
    :return: the image url if found else an error message.
    """
    url = 'https://staging-api.ram.moe/images/random?'
    header = {'Authorization': key}
    params = {'type': type_}
    try:
        js = await session_manager.get_json(
            url, params,
            headers=header
        )
    except HTTPStatusError as e:
        return f'Sorry, something went wrong with the Wolke api.\n{e}'
    else:
        img = js.get('url', None)
        return img or 'Sorry, nothing found.'


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
