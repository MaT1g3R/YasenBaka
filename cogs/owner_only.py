from discord import Forbidden, TextChannel
from discord.embeds import Embed
from discord.ext.commands import Context, command

from bot import Yasen
from scripts.checks import is_owner


class OwnerOnly:
    __slots__ = ('bot',)

    def __init__(self, bot: Yasen):
        self.bot = bot

    async def __local_check(self, ctx: Context):
        return await is_owner(ctx)

    @command()
    async def announce(self, ctx: Context, *, msg: str):
        """
        Send an announcement to every guild.

        This is hidden in the help message
        """
        res = Embed(
            colour=self.bot.config.colour,
            title='This is an announcement from my developer.',
            description=msg
        )
        await send_anncoucements(self.bot, res)


async def send_anncoucements(bot: Yasen, embed: Embed):
    for guild in bot.guilds:
        for ch in sorted(guild.channels, key=announce_key):
            if not isinstance(ch, TextChannel):
                continue
            try:
                await ch.send(embed=embed)
                break
            except Forbidden:
                continue


def announce_key(channel):
    if not isinstance(channel, TextChannel):
        return 5

    if channel.is_nsfw():
        return 4
    name = channel.name.lower()
    if 'announce' in name:
        return 0

    if 'general' in name:
        return 1

    if 'bot' in name:
        return 2

    return 3
