from pathlib import Path
from random import choice, random
from typing import List, Tuple, Union

from discord import File

from bot import SessionManager
from core.nsfw_core import get_lewd
from data_manager import DataManager


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
