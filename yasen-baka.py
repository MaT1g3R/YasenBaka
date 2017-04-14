"""The main bot run file"""

from discord import game

# Core imports
from core import data_factory
# Bot cog imports
from shell.channelreader import ChannelReader
from shell.fun import Fun
from shell.music_player import Music
from shell.osu_commands import Osu
from shell.util import Util
from shell.world_of_warships import WorldOfWarships
from shell.yasen import Yasen

if __name__ == '__main__':
    description = 'Yo Teitoku, Yasennnnn!'
    prefix = '!'
    bot = Yasen(prefix, description, data_factory())
    cogs = [Util(bot), Fun(bot), Osu(bot), ChannelReader(bot),
            WorldOfWarships(bot), Music(bot)]


    @bot.event
    async def on_ready():
        """
        Event for when bot is ready
        :return: nothing
        :rtype: None
        """
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')
        await bot.change_presence(game=game.Game(name='!help | !info'))


    bot.start_bot(cogs)
