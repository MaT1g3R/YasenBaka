"""A file of all helper functions"""
import textwrap
from os import listdir
from os.path import isfile, join
import urllib.request
import urllib.parse
import json
import requests
from codecs import open as copen
import xml.etree.ElementTree as ET
from datetime import date, timedelta


def fopen_generic(filepath, filemode='rU', coding='utf8', buffering=-1):
    """
    Reads files using system seperators with friendly encodings
    :param filepath: file path
    :type filepath: str
    :param filemode: file mode (default 'rU')
    :type filemode: str
    :param coding: encoding for file (default 'utf8')
    :type coding: str
    :param buffering: buffer mode, see https://docs.python.org/2/library/functions.html#open (default -1)
    :type buffering: int
    :return file pointer
    :rtype file
    """
    if isfile(filepath):
        return copen(filepath, filemode, coding, 'replace', buffering)
    return None


def freadlines(fp, keep_open=False):
    """
    Splits file lines
    :param fp: file pointer
    :param keep_open: keep fp open (default false)
    :type fp: file
    :type keep_open: bool | int
    :return: file lines
    :rtype: list
    """
    if fp is not None:
        lines = fp.readlines()
        if not keep_open:
            fp.close()
        return lines
    return []


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


def format_eq(term1, term2):
    """
    checks if the value of term1 and term2 are equal, and return the range between them
    :param term1: the first term
    :type term1: object
    :param term2: the second term
    :type term2: object
    :return: the range between them
    :rtype: str
    """
    return str(term1) if term1 == term2 else str(min(term1, term2)) + '-' + str(max(term1, term2))


async def try_say(bot, text, i=1):
    """
    Try to say the block of text until the bot succeeds
    :param bot: The bot
    :type bot: discord.ext.commands.Bot
    :param text: The block of text
    :type text: str | list
    :param i: how many sections the text needs to be split into
    :type i: int
    :return: nothing
    :rtype: None
    """
    try:
        if isinstance(text, list):
            for txt in text:
                await bot.say('```markdown\n' + txt + '```')
        elif isinstance(text, str):
            await bot.say('```markdown\n' + text + '```')
    except Exception:
        i += 1
        await try_say(bot, split_text(text, i), i)


def read_kana_files():
    """
    Reads the kanna pictures
    :return: All path of kanna pics
    :rtype: list
    """
    root = join('data', 'kanna_is_cute_af')
    return [join(root, f) for
            f in listdir(root) if isfile(join(root, f))]


def is_admin(ctx, id_):
    """
    Check if an user is an admin
    :return: True if the user is an admin
    :rtype: bool
    """
    try:
        return ctx.message.server.get_member(id_).server_permissions.administrator
    except AttributeError:
        return False


def generate_image_online(url, fn):
    """
    Generates an image file from a image hot link
    :param url: The url
    :param fn: the file name
    :type url: str
    :return: The generated image path
    :rtype: str
    """
    urllib.request.urlretrieve(url, fn)
    return fn


def generate_latex_online(latex):
    """
    Generate latex image from latex website
    :param latex: the latex equation to be rendered
    :type latex: str
    :return: The path to rendered latex image
    :rtype: str
    """
    url = 'http://frog.isima.fr/cgi-bin/bruno/tex2png--10.cgi?'
    url += urllib.parse.quote(latex, safe='')
    fn = join('data', 'latex.png')
    urllib.request.urlretrieve(url, fn)
    return fn


def read_json(fp, keep_open=False):
    """
    Read a json file into a dictionary
    :param fp: the file pointer
    :type fp: file
    :param keep_open: keep file open (default False)
    :type keep_open: bool | int
    :return: the dictionary
    :rtype: dict
    """
    if fp is not None:
        data = json.load(fp)
        if not keep_open:
            fp.close()
        return data
    return {}


def write_json(fp, data, keep_open=False):
    """
    Write a dictionary into a json file
    :param fp: The json file
    :type fp: ffile
    :param data: The dictionary
    :type data: dict
    :param keep_open: keep file open (default False)
    :type keep_open: bool | int
    :return: nothing
    :rtype: None
    """
    if fp is not None:
        json.dump(data, fp)
        if not keep_open:
            fp.close()


def update_command_blacklist(add, command, id_):
    """
    Update the command blacklist for the server
    :param add: The mode, true for add, false for del
    :type add: bool
    :param command: the command
    :type command: str
    :param id_: the server id
    :type id_: str
    :return: nothing
    :rtype: None
    """
    my_dict = read_json(fopen_generic(join('data', 'command_blacklist.json')))
    if id_ not in my_dict:
        my_dict[id_] = []
    if add is False:
        if command in my_dict[id_]:
            my_dict[id_].remove(command)
    else:
        if command not in my_dict[id_]:
            my_dict[id_].append(command)
    write_json(fopen_generic(join('data', 'command_blacklist.json'), 'w'), my_dict)


def is_banned(command, id_):
    """
    Check if a command in banned in this server
    :param command: the command
    :type command: str
    :param id_: the server id
    :type id_: str
    :return: True if it's banned
    :rtype: bool
    """
    data = read_json(fopen_generic(join('data', 'command_blacklist.json')))
    try:
        return True if id_ in data and \
                       command in data[id_] else False
    except AttributeError:
        return False


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


def convert_currency(base, amount, target):
    """
    Conver currency to another
    :param base: str
    :param amount: str
    :param target: str
    :return: str
    """
    key = read_json(fopen_generic(join('data', 'api_keys.json')))['Currency']
    request_url = 'http://www.apilayer.net/api/live?access_key={}& currencies =USD,{}{}&format=1' \
        .format(key, base, target)
    response = requests.get(request_url).text
    try:
        parsed_data = json.loads(response)['quotes']
    except KeyError:
        raise KeyError
    try:
        rate = float(parsed_data['USD{}'.format(target)]) / float(parsed_data['USD{}'.format(base)])
        return "{0:.2f}".format(float(amount) * rate)
    except KeyError:
        raise KeyError


def safebooru(tag):
    """
    Get a list of pictures from safebooru based on tag
    :param tag: the tag to search for 
    :return: a list of picture links based on the tag
    """
    url = "https://safebooru.org//index.php?page=dapi&s=post&q=index&tags={}".format(tag)
    result = requests.get(url).content
    root = ET.fromstring(result)
    return ['https:' + child.attrib['file_url'] for child in root]


def get_distro():
    """
    Name of your Linux distro (in lowercase).
    """
    with open("/etc/issue") as f:
        return f.read().lower().split()[:3]


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