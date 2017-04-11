import textwrap
from os.path import join
from file_system import freadlines, fopen_generic


def split_text(text, i):
    """
    Splits text into a list
    :param text: The text to be splitted
    :type text: str | list
    :param i: the number of sections the text needs to be split into
    :type i: int
    :return: The split up text
    :rtype: list
    """
    if isinstance(text, list):
        text = ''.join(text)
    return textwrap.wrap(text, int(len(text) / i))


def get_distro():
    """
    Name of your Linux distro (in lowercase).
    """
    raw = ' '.join(freadlines(fopen_generic(join('/', 'etc', 'issue'))))
    res = ''
    for s in raw:
        if s != '\\':
            res += s
        else:
            break
    while res.endswith(' '):
        res = res[:-1]

    return res


def get_server_id(ctx):
    """
    Get the server id of a context
    :param ctx: the context
    :type ctx: context
    :return: the server id
    :rtype: str
    """
    try:
        return ctx.message.server.id
    except AttributeError:
        return None


def is_admin(ctx):
    """
    Check if an user is an admin
    :return: True if the user is an admin
    :rtype: bool
    """
    try:
        return ctx.message.server.get_member(ctx.message.author.id)\
            .server_permissions.administrator
    except AttributeError:
        return False
