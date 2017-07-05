"""Initialize the bot"""

import sqlite3
from os.path import join

# Core imports
from core import data_factory
from core.command_handler import get_prefix
from shell.botsorgapi import Botsorgapi
# Bot cog imports
from shell.channelreader import ChannelReader
from shell.fun import Fun
from shell.music_player import Music
from shell.nsfw import Nsfw
from shell.osu_commands import Osu
from shell.util import Util
from shell.world_of_warships import WorldOfWarships
from shell.yasen import Yasen


def init(shard_count=1, shard_id=0):
    description = 'Yo Teitoku, Yasennnnn!'
    connection = sqlite3.connect(join('data', 'mydb'))
    cursor = connection.cursor()

    bot = Yasen(
        '?', get_prefix, description, data_factory(), cursor, connection,
        shard_count, shard_id)
    cogs = [Util(bot), Fun(bot), Osu(bot), ChannelReader(bot),
            WorldOfWarships(bot), Music(bot), Nsfw(bot), Botsorgapi(bot)]

    return bot, cogs
