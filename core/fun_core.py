from random import choice, randint

from discord import File

from bot import SessionManager
from core.nsfw_core import get_lewd
from data_manager import DataManager


def generate_dice_rolls(s: str):
    """
    Generate dice rolls based on input string
    :param s: the input string
    :return: a list of dice rolls
    """
    try:
        rolls, limit = [int(s) for s in s.split('d')]
        return (':game_die: '
                + ', '.join(str(randint(1, limit)) for _ in range(rolls)))
    except ValueError:
        return 'Format must to be in NdN!'


def event_probability(prob: str, tries: int):
    """
    Return the probability of something happeneing in x number of tries
    :param prob: the probability of the event happeneing
    :param tries: the number of tries
    :return: the probability of the event happeneing
    """
    try:
        prob = float(prob.replace('%', '')) / 100 if '%' in prob else float(
            prob)
        return round((1 - (1 - prob) ** tries), 4)
    except ValueError:
        return


async def random_kanna(kanna_files: list,
                       session_manager: SessionManager,
                       data_manager: DataManager) -> File:
    """
    Returns a tuple of kanna picture and if it's a file.
    :param kanna_files: list of local kanna files.
    :param session_manager: the SessionManager.
    :param data_manager: the data manager.
    :return: a kanna image as a discord File object.
    """
    _, url, __ = await get_lewd(
        session_manager, 'safebooru', ('kanna_kamui',), data_manager)
    path = str(choice(kanna_files))
    try:
        if url:
            url_bytes = await session_manager.bytes_io(url)
        else:
            url_bytes = None
    except:
        url_bytes = None
    return choice((File(path), File(url_bytes))) if url_bytes else File(path)


def parse_repeat(n, msg) -> tuple:
    """
    Parse the argument for the repeat command.
    :param n: the number of times of repeat.
    :param msg: the message to be repeated.
    :return: (number of times of repeat, message to be repeated)
    :raises ValueError:
        if n is not an integre between 1 and 5, or msg is None,
        or len(msg) > 2000.
    """
    try:
        n = int(n)
        if not 1 <= n <= 5:
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError('Please enter a number between 1 and 5.')
    if not msg or len(msg) > 2000:
        raise ValueError('Please enter a message with length less than 2000 '
                         'for me to repeat.')
    return n, msg
