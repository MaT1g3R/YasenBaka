"""
Core for the util cog
"""
import math
import time


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


def default_help(help_dict):
    """
    Generate the default help message.
    :param help_dict: the help message dictionary
    :return: the default help message.
    """
    music = ', '.join(sorted(help_dict['music']))
    fun = ', '.join(sorted(help_dict['fun']))
    util = ', '.join(sorted(help_dict['util']))
    wows = ', '.join(sorted(help_dict['wows']))
    sheet = ', '.join(help_dict['sheet_data'])

    return 'Command List:\nUtility:```{}```Fun:```{}```Music:```{}```' \
           'World of Warships:```{}```WoWs match spreadsheet:```{}```'.format(
            util, fun, music, wows, sheet) + \
           '?help [command] for more info on that command, such as `?help play`'


def process_pmall(ctx, *args):
    message = []
    lazy_bums = []
    for s in args:
        if s.startswith('<@!') and s.endswith('>'):
            lazy_bums.append(s[3:-1])
        elif s.startswith('<@') and s.endswith('>'):
            lazy_bums.append(s[2:-1])
        else:
            message.append(s)

    members = [member for member in ctx.message.server.members
               if member.id in lazy_bums]
    pass