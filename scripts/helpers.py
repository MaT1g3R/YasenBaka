from collections import Iterable
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
    if in_ is None:
        return []
    elif isinstance(in_, Iterable) and not isinstance(in_, str):
        res = []
        for l in in_:
            res += flatten(l)
        return res
    else:
        return [in_]
