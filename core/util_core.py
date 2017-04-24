"""
Core for the util cog
"""
import math
import resource
import sys
import time
from json import loads
from os.path import join
from subprocess import check_output, STDOUT, CalledProcessError
from urllib import request, parse

from discord import Member, ChannelType, version_info
from google import search
from html2text import html2text
from requests import get

from core.discord_functions import build_embed, get_server_id
from core.helpers import get_distro
from config.help import COMMAND_LISTS


def time_elapsed(start_time):
    """
    Get the time elapsed from start_time in a h:mm:ss format
    :param start_time: the start time, in seconds
    :return: time elapsed from start_time in a h:mm:ss format
    :rtype: str
    """
    time_elapsed_ = int(time.time() - start_time)
    hours = math.floor(time_elapsed_ / (60 * 60))  # How the fuck do i math
    time_elapsed_ -= hours * 3600
    minutes = math.floor(time_elapsed_ / 60)
    time_elapsed_ -= minutes * 60
    minutes_str = str(minutes) if minutes >= 10 else '0' + str(minutes)
    seconds_str = str(time_elapsed_) if time_elapsed_ >= 10 \
        else '0' + str(time_elapsed_)
    return '{}:{}:{}'.format(str(hours), minutes_str, seconds_str)


def default_help(prefix):
    """
    Generate the default help message.
    :param prefix: the prefix of the bot
    :return: the default help message.
    """
    res = ''
    for key, val in COMMAND_LISTS:
        res += key + ':```' + ', '.join(sorted(val)) + '```'
    res += '{0}help [command] for more info on that command, ' \
        'such as `{0}help play`'.format(prefix) \
        + '\nYou can also talk to the bot by ' \
          'mentioning her!\nExample usage: <@243230010532560896> ' \
          'hi'
    return res


def process_pmall(ctx, message_in: list):
    """
    Process the pmall request from the bot
    :param ctx: the context of the request
    :param message_in: the message including the mentions
    :return: A tuple of (members, content)
    :rtype: tuple
    """
    message = message_in[:]
    m_d = {member.id: member for member in ctx.message.server.members}
    member_ids = []
    while len(message) > 0:
        s = message[0]
        if s.startswith('<@!') and s.endswith('>') and s[3:-1] in m_d:
            member_ids.append(message.pop(0)[3:-1])
        elif s.startswith('<@') and s.endswith('>') and s[2:-1] in m_d:
            member_ids.append(message.pop(0)[2:-1])
        else:
            break
    return [member for member in m_d.values() if member.id in member_ids], ' ' \
        .join(message)


def generate_latex_online(latex):
    """
    Generate latex image from latex website
    :param latex: the latex equation to be rendered
    :type latex: str
    :return: The path to rendered latex image
    :rtype: str
    """
    url = 'http://frog.isima.fr/cgi-bin/bruno/tex2png--10.cgi?'
    url += parse.quote(latex, safe='')
    fn = join('data', 'latex.png')
    request.urlretrieve(url, fn)
    return fn


def joined_time(member: Member):
    """
    :param member: the discord member
    :return: when the member joined the server
    :rtype: str
    """
    return \
        ' '.join(
            str.split(
                '{0.name} joined in {0.joined_at}'.format(member), ' ')[:-1])


def anime_search(name: str):
    """
    Search for an anime on MAL
    :param name: the name of the anime
    :return: the url to the MAL page
    """
    name = name.replace(' ', '+')
    for url in search(name, stop=20):
        if 'https://myanimelist.net/anime' in url:
            return url
    return 'Anime not found!'


def stack_answer(so, question: str):
    """
    Ask stackoverflow a question
    :param so: stackoverflow api object
    :param question: the question to be asked
    :return: the answer from stackoverflow
    """
    q = question.replace(' ', '+') + ' site:stackoverflow.com'
    q_url = ''
    for url in search(q, stop=2):
        if 'stackoverflow.com/questions/' in url:
            q_url = url
            break
    if q_url == '':
        return "Question not found!"

    start_index = q_url.find('questions') + 10
    finish_index = q_url[start_index:].find('/') + start_index
    question_id = int(q_url[start_index:finish_index])
    question = so.question(question_id)
    return html2text(question.answers[0].body)


def convert_currency(key, base, amount, target):
    """
    Conver currency to another
    :param key: currency api key
    :param base: the base currency
    :param amount: the amount of money
    :param target: the target currency to convert to
    :return: the conversion result
    :rtype: str
    """
    request_url = \
        'http://www.apilayer.net/api/live?access_key={}' \
        '&currencies={},{}&source=USD&format=1'.format(key, base, target)
    response = get(request_url).content
    try:
        parsed_data = loads(response)['quotes']
    except KeyError:
        raise KeyError
    try:
        rate = float(parsed_data['USD{}'.format(target)]) \
               / float(parsed_data['USD{}'.format(base)])
        return "{0:.2f}".format(float(amount) * rate)
    except KeyError:
        raise KeyError


def info_builder(ctx, servers, all_members, all_channels, voice_clients,
                 user, uptime):
    """
    Return the bot's information, in a discord embed object
    :param ctx: the context of the bot
    :param servers: an iterator for all servers the bot is in
    :param all_members: an iterator for all members the bot can see
    :param all_channels: an iterator for all channels the bot is in
    :param voice_clients: an iterator for all voice channels the bot is in
    :param user: the bot user
    :param uptime: bot uptime
    :rtype: Embed
    """
    server_count = len([s for s in servers])
    user_count = len([u for u in all_members])
    text_channel_count = len(
        [c for c in all_channels if c.type == ChannelType.text])
    voice_count = len([v for v in voice_clients])
    ram = "{0:.2f}".format(
        float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))
    ram = str(ram) + 'MB'
    lib_ver = version_info
    colour = 0x4286f4
    author = {
        'name': user.name,
        'icon_url': '{0.avatar_url}'.format(user)
    }
    k_v = [
        ('RAM used', ram),
        ('Uptime', uptime),
        ('Python version', sys.version[:5]),
        ('Library',
         'Discord.py v{}.{}.{}'.format(
             lib_ver.major, lib_ver.minor, lib_ver.micro)),
        ('System', get_distro()),
        ('Developers', 'ラブアローシュート#6728\nNaomi#3264'),
        ('Servers', str(server_count)),
        ('Users', str(user_count)),
        ('Text channels', str(text_channel_count)),
        ('Voice channels', str(voice_count)),
        ('Source code and invite link', 'https://github.com/MaT1g3R/YasenBaka'
         , False),
        ('Support server', 'https://discord.gg/BnPbz6q')
    ]
    footer = 'Requested by {}'.format(
        ctx.message.author.display_name + '#' +
        ctx.message.author.discriminator)
    return build_embed(k_v, colour, author=author, footer=footer)


def bash_script(command: list):
    """
    Run a bash script
    :param command: the bash command
    :return: the result of the command
    """
    try:
        output = check_output(command, stderr=STDOUT)
        res_str = output.decode()
        return \
            ":white_check_mark: Command success!\nOutput:\n" \
            "```\n{}\n```".format(res_str)
    except CalledProcessError as ex:
        res_str = ex.output.decode()
        return \
            ":no_entry_sign: Command failed!\nOutput:" \
            "\n```\n{}\n```".format(res_str)


def raw_bash(command: list):
    """
    Raw bash access
    :param command: the command in a list 
    :return: the result
    """
    output = check_output(command, stderr=STDOUT)
    return output.decode()
