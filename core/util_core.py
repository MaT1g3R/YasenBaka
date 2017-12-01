from contextlib import contextmanager
from typing import Union

from aiohttp_wrapper import HTTPStatusError, SessionManager
from discord import Member, User


@contextmanager
def delete(path):
    yield
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def get_avatar(target: Union[User, Member]) -> str:
    """
    Get the avatar url of a given user/member because the library built-in
    function is bad.
    :param target: the target.
    :return: the avatar url of the target.
    """
    if target.avatar and target.avatar.startswith('a'):
        return f'{target.avatar_url}.gif'
    else:
        return target.avatar_url


async def convert_currency(session_manager: SessionManager, key: str,
                           from_: str, to: str, amt: float) -> str:
    """
    Converts currency and return a human readable result.
    :param session_manager: the SessionManager instance.
    :param key: the api key.
    :param from_: the base currency.
    :param to: the target currency.
    :param amt: the amount to be converted.
    :return: A string for the result.
    """
    base, target = from_.upper(), to.upper()
    url = 'http://www.apilayer.net/api/live?'
    params = {
        'access_key': key,
        'currencies': f'{base},{target}',
        'source': 'USD',
        'format': '1'
    }
    try:
        js = await session_manager.get_json(url, params)
    except HTTPStatusError as e:
        return f'Something went wrong with the apilayer API\n{e}'

    data = js.get('quotes', None)
    if not data:
        return 'Please enter vaild currency codes.'
    try:
        rate = (float(data[f'USD{target}']) / float(data[f'USD{base}']))
    except KeyError:
        return 'Please enter vaild currency codes.'
    if amt.is_integer():
        amt = int(amt)
    return f'{amt} {base} = {amt*rate:.2f} {target}'
