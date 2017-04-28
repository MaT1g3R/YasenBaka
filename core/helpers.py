import textwrap
import xml.etree.ElementTree as Et
from datetime import timedelta, date, datetime
from os.path import join
from shutil import copyfileobj

from requests import get

from core.file_system import freadlines, fopen_generic


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


def safebooru(tag):
    """
    Get a list of pictures from safebooru based on tag
    :param tag: the tag to search for 
    :return: a list of picture links based on the tag
    """
    url = "https://safebooru.org//index.php?page=dapi&s=post&q=index&tags={}" \
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


def clense_prefix(message: str, prefix: str):
    """
    Clean the message's prefix
    :param message: the message
    :param prefix: the prefix to be cleaned
    :return: A new message without the prefix
    """
    if not message.startswith(prefix):
        return message
    else:
        return message[len(prefix):]


def timestamp_to_string(timestamp: int):
    """
    Convert unix timestamp to a readable string
    :param timestamp: the unix time stamp
    :return: date time string
    """
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')


def combine_dict(dicts):
    """
    combine (nested) dictionaries with numbers as values,
    assuming same key in all dicts maps to the same data type
    :param dicts: a collection of dicts
    :return: the combined dict
    >>> d1 = {'a': 1, 'b': 2}
    >>> d2 = {'a': 1, 'c':1}
    >>> d3 = combine_dict((d1, d2))
    >>> d3 == {'a': 2, 'b': 2, 'c': 1}
    True
    >>> d4 = {'d1': d1, 'd2': d2}
    >>> d5 = {'d1': d1, 'c':100}
    >>> d6 = combine_dict((d4, d5))
    >>> d6 == {'d1': {'a': 2, 'b': 4}, 'd2': d2, 'c': 100}
    True
    >>> combine_dict((d1, d2, d3)) == {'a': 4, 'b': 4, 'c': 2}
    True
    >>> combine_dict((d4, d5, d6)) == \
    {'d1':{'a': 4,'b':8}, 'd2': {'a':2,'c':2}, 'c': 200}
    True
    """
    if len(dicts) == 0:
        return None
    elif len(dicts) == 1:
        return dicts[0]
    elif len(dicts) == 2:
        d1, d2 = dicts
        res = {}
        all_keys = set(list(d1.keys()) + list(d2.keys()))
        for key in all_keys:
            if key in d1 and key in d2:
                if isinstance(d1[key], dict):
                    res[key] = combine_dict((d1[key], d2[key]))
                else:
                    res[key] = d1[key] + d2[key]
            elif key in d1:
                res[key] = d1[key]
            elif key in d2:
                res[key] = d2[key]
        return res
    elif len(dicts) > 2:
        l = len(dicts)
        return combine_dict(
            (combine_dict(dicts[:l//2]), combine_dict(dicts[l//2:])))
