from platform import python_version

from discord import Embed, TextChannel, VoiceChannel, __version__ as discord_v

from bot import (Yasen, __author__ as author, __title__ as name,
                 __url__ as source)
from scripts.helpers import timedelta_str
from scripts.system import ram_usage, system_name, total_ram


def get_info_embed(bot: Yasen) -> Embed:
    """
    Get an info embed for the bot.
    :param bot: the bot instance.
    :return: A discord embed of this bot.
    """
    all_ch = bot.get_all_channels()
    embed = Embed(colour=bot.config.colour)
    embed.set_author(name=f'{name} | {bot.version}',
                     icon_url=bot.user.avatar_url)
    a = embed.add_field
    a(name='RAM used/System RAM', value=ram_str())
    a(name='Uptime', value=timedelta_str(bot.uptime))
    a(name='Python version', value=python_version())
    a(name='Library', value=f'Discord.py {discord_v}')
    a(name='System', value=system_name())
    a(name='Developers', value='\n'.join(author))
    a(name='Guilds', value=f'{len(bot.guilds):,}')
    a(name='Members', value=f'{len(tuple(bot.get_all_members())):,}')
    a(name='Text Channels',
      value=f'{len([c for c in all_ch if isinstance(c, TextChannel)]):,}')
    a(name='Voice Channels',
      value=f'{len([c for c in all_ch if isinstance(c, VoiceChannel)]):,}',
      inline=False)
    a(name='Support Guild', value=f'[{name} Support]({bot.config.support})')
    a(name='Source Code', value=f'[{name} Source]({source})')
    a(name='Invite Link', value=f'[{name} Invite]({bot.invite_link})')
    del a
    return embed


def ram_str() -> str:
    """
    Get a string representation of used RAM/total RAM.
    :return: a string representation of used RAM/total RAM.
    """
    to_str = lambda ram: (f'{ram:.2f}MiB'
                          if ram < 1024 else f'{ram/1024:.2f}GiB')
    return f'{to_str(ram_usage())}/{to_str(total_ram())}'
