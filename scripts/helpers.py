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
