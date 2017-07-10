from collections import Iterable
from datetime import timedelta
from itertools import chain
from textwrap import wrap


def code_block(s: str, lan: str = ''):
    """
    Turn a string into markdown code blocks.
    :param s: the string.
    :param lan: the language, optional.
    :return: the list of code block strings.
    """
    res = wrap(s, 1800, replace_whitespace=False)
    str_out = [f'```{lan}\n' + s.replace('`', chr(0x1fef)) + '\n```'
               for s in res]
    return str_out


def flatten(in_) -> list:
    """
    Flaten a input list/tuple into a list
    :param in_: the input
    :return: a flattened list of the input
    >>> flatten(([0, 1], [2, 3], [[4, 5], 6]))
    [0, 1, 2, 3, 4, 5, 6]
    >>> flatten((['0', '1'], ['2', '34'], [[4, 5], 6]))
    ['0', '1', '2', '34', 4, 5, 6]
    >>> flatten(([None, '1'], ['2', '34'], [[4, 5], 6]))
    ['1', '2', '34', 4, 5, 6]
    """
    if isinstance(in_, Iterable) and not isinstance(in_, str):
        return list(chain(*(flatten(lst) for lst in in_)))
    return [in_] if in_ is not None else []


def timedelta_str(delta: timedelta) -> str:
    """
    Get a string representation of a timedelta object.
    :param delta: the time delta.
    :return: a string representation of the timedelta object.
    """
    days = delta.days
    hrs, secs = divmod(delta.seconds, 3600)
    mins, secs = divmod(secs, 60)
    res = f'{hrs}h:{mins:02}m:{secs:02}s'
    if days:
        day_s = 'day' if days == 1 else 'days'
        return f'{days} {day_s}, {res}'
    return res
