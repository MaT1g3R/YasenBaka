import re
from collections import Iterable
from datetime import date, timedelta
from itertools import chain, zip_longest
from textwrap import wrap
from typing import List, Type, Union


def code_block(s: str, lan: str = ''):
    """
    Turn a string into markdown code blocks.
    :param s: the string.
    :param lan: the language, optional.
    :return: the list of code block strings.
    """
    res = wrap(s, 1800, replace_whitespace=False)
    return [f"```{lan}\n{s.replace('`', chr(0x1fef))}\n```" for s in res]


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


def split_camel(s: str) -> List[str]:
    """
    Split a string by starting chars of UpperCamelCase
    :param s: the input string.
    :return: a list of strings that was split by capital letters.
    """
    regex = re.compile('[A-Z][^A-Z]*')
    return regex.findall(s)


def lower_words(s: str) -> str:
    """
    Turn a word into lower case if it makes sense. (like "of", "is", etc.)
    :param s: the input string.
    :return: the output might be lower case.
    """
    tup = ('of',)
    return s.lower() if s.lower() in tup else s


def parse_number(s: str, t: Type) -> Union[int, float, None]:
    """
    Parse a string into a number.
    :param s: the string.
    :param t: the type of the number, int or float.
    :return: the parsed number if success, else None.
    """
    try:
        return t(s)
    except (TypeError, ValueError):
        return None


def get_date(diff: int) -> str:
    """
    Return a day's date by diff.
    :param diff: the difference in date in days.
    :return: the date in format YYYYMMDD
    """
    yesterday = date.today() - timedelta(diff)
    return yesterday.strftime('%Y%m%d')


def try_divide(numerator: Union[int, float], denominator: Union[int, float]):
    """
    Try to divide two numbers.
    :param numerator: the numerator.
    :param denominator: the denominator.
    :return: the result of the division if denominator is not zero else 0.
    """
    return numerator / denominator if denominator else 0


def combine_objects(*args):
    """
    Recursively combine just about anything.
    :return: the combined "sum" of the given parameters.
    >>> d1 = {'a': 1, 'b': 2}
    >>> d2 = {'a': 1, 'c':1}
    >>> d3 = combine_objects(d1, d2)
    >>> d3 == {'a': 2, 'b': 2, 'c': 1}
    True
    >>> d4 = {'d1': d1, 'd2': d2}
    >>> d5 = {'d1': d1, 'c':100}
    >>> d6 = combine_objects(d4, d5)
    >>> d6 == {'d1': {'a': 2, 'b': 4}, 'd2': d2, 'c': 100}
    True
    >>> combine_objects(d1, d2, d3) == {'a': 4, 'b': 4, 'c': 2}
    True
    >>> combine_objects(d4, d5, d6) == \
    {'d1':{'a': 4,'b':8}, 'd2': {'a':2,'c':2}, 'c': 200}
    True
    """

    def combine_two(d0, d1):
        if d0 is None or d1 is None:
            return d0 or d1
        if isinstance(d0, list) and isinstance(d1, list):
            return [combine_two(a, b) for a, b in zip_longest(d0, d1)]
        if isinstance(d0, dict) and isinstance(d1, dict):
            res = {}
            for key in set(list(d0.keys()) + list(d1.keys())):
                val0, val1 = d0.get(key, None), d1.get(key, None)
                res[key] = combine_two(val0, val1)
            return res
        return d0 + d1

    if not args:
        return
    if len(args) == 1:
        return args[0]
    if len(args) == 2:
        return combine_two(args[0], args[1])
    if len(args) > 2:
        mid = len(args) // 2
        return combine_objects(
            combine_objects(*args[:mid]),
            combine_objects(*args[mid:])
        )
