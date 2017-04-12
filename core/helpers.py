import textwrap
from os.path import join
from file_system import freadlines, fopen_generic
from requests import get
import xml.etree.ElementTree as Et
from shutil import copyfileobj
from datetime import timedelta, date


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


def safebooru(tag):
    """
    Get a list of pictures from safebooru based on tag
    :param tag: the tag to search for 
    :return: a list of picture links based on the tag
    """
    url = "https://safebooru.org//index.php?page=dapi&s=post&q=index&tags={}"\
        .format(tag)
    result = get(url).content
    root = Et.fromstring(result)
    return ['https:' + child.attrib['file_url'] for child in root]


def generate_image_online(url, fn):
    """
    Generates an image file from a image hot link
    :param url: The url
    :param fn: the file name
    :type url: str
    :return: The generated image path
    :rtype: str
    """
    response = get(url, stream=True)
    if response.status_code == 200:
        with open(fn, 'wb') as f:
            response.raw.decode_content = True
            copyfileobj(response.raw, f)
    return fn


def comma(val):
    """
    Return a comma seprated number
    :param val: the number
    :return: the comma seprated number
    """
    return "{:,}".format(int(val))


def split_list(lst, max_length):
    """
    Split a list into sublists
    :param lst: the list to be split
    :param max_length: the max allowed length of the result
    :return: a list of split up lists
    """
    return [lst[i:i + max_length] for i in range(0, len(lst), max_length)]


def get_date(diff):
    """
    Return yesterday's date in YYYYMMDD format
    :return: yesterday's date in YYYYMMDD format
    """
    yesterday = date.today() - timedelta(diff)
    return yesterday.strftime('%Y%m%d')


def format_eq(term1, term2):
    """
    checks if the value of term1 and term2 are equal, 
    and return the range between them
    :param term1: the first term
    :type term1: object
    :param term2: the second term
    :type term2: object
    :return: the range between them
    :rtype: str
    """
    return str(term1) if term1 == term2 else str(min(term1, term2)) + '-' + str(
        max(term1, term2))
