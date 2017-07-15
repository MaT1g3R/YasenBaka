import re
from json import dumps
from logging import INFO, WARN
from traceback import format_exc

from discord import File, Game, Guild, Message, TextChannel
from discord.abc import Messageable
from discord.ext.commands import CommandNotFound, Context

from bot import HTTPStatusError, Yasen
from bot.error_handler import command_error_handler, format_command_error
from data import data_path
from data_manager.data_utils import get_prefix


class Listeners:
    """
    Class for event listeners.
    """

    def __init__(self, bot: Yasen):
        self.bot = bot
        self.mention = None
        self.mention_msg = None
        self.o7 = File(str(data_path.joinpath('o7.gif')))

    async def on_ready(self):
        """
        Event for when bot gets ready.
        """
        g = Game(name=f'{self.bot.version} | {self.bot.default_prefix}help')
        self.bot.logger.log(INFO, f'Logged in as: {self.bot.user}')
        self.bot.logger.log(INFO, f'Client Id: {self.bot.client_id}')
        await self.bot.try_change_presence(True, game=g)
        await self.__post_guild_count()
        _mention = f'<@!?{self.bot.client_id}>'
        self.mention = re.compile(_mention)
        self.mention_msg = re.compile(f'^{_mention}\s*[^\s]+.*$')

    async def on_command_error(self, context: Context, exception):
        """
        Custom command error handling.
        :param context: the context of the exception raised.
        :param exception: the exception raised.
        """
        if isinstance(exception, CommandNotFound):
            return
        try:
            res = command_error_handler(exception)
        except Exception as e:
            tb = format_exc()
            msg, triggered = format_command_error(e, context)
            self.bot.logger.log(WARN, f'\n{msg}\n\n{tb}')
            await context.send(f':warning: I ran into an error while '
                               f'executing this command.\n{msg}')
            await self.bot.send_tb(
                f'**WARNING** Triggered message:\n{triggered}', tb
            )
        else:
            await context.send(res)

    async def on_message(self, message: Message):
        """
        Listener for Client.on_message.
        :param message: the message.
        """
        author = message.author
        content: str = message.content
        channel = message.channel
        prefix = get_prefix(self.bot, message)
        if (author.bot or
                content.startswith(prefix) or
                not isinstance(content, str) or
                not isinstance(channel, Messageable)):
            return

        stripped = self.__strip_mention(content)
        if stripped and stripped.lower() == 'prefix' \
                and isinstance(channel, TextChannel):
            msg = (f'The prefix for this guild is: `{prefix}`\n'
                   f'`{prefix}prefix set <YOUR_PREFIX>` to set the '
                   f'prefix for this guild.\n`{prefix} reset` to reset'
                   f' the prefix for this guild to default. `({prefix})`')
            await channel.send(msg)
        elif content == '/o/':
            await channel.send('\\o\\')
        elif content == '\\o\\':
            await channel.send('/o/')
        elif content == 'o7':
            await channel.send(file=self.o7)

    async def on_guild_join(self, guild: Guild):
        """
        Event for joining a guild.
        :param guild: the guild the Bot joined.
        """
        self.bot.logger.log(INFO, f'Joined guild {guild.name}')
        await self.__post_guild_count()

    async def on_guild_remove(self, guild: Guild):
        """
        Event for removing from a guild.
        :param guild: the guild the Bot was removed from.
        """
        self.bot.logger.log(INFO, f'Left guild {guild.name}')
        await self.__post_guild_count()

    async def __post_guild_count(self):
        """
        Post guild count to discordbots.org
        """
        if self.bot.config.is_beta:
            return
        url = f'https://discordbots.org/api/bots/{self.bot.client_id}/stats'
        data = dumps({
            'shard_id': str(self.bot.shard_id),
            'shard_count': str(self.bot.shard_count),
            'server_count': len(self.bot.guilds)
        })
        header = {
            'authorization': self.bot.config.botsorgapi,
            'content-type': 'application/json'
        }
        try:
            resp = await self.bot.session_manager.post(
                url, data=data, headers=header)
            await resp.release()
        except HTTPStatusError as e:
            self.bot.logger.log(WARN, str(e))

    def __strip_mention(self, s: str):
        """
        Strip message starts with mention to the bot.
        :param s: the input string.
        :return: the message without the mention.
        """
        if self.mention is None or self.mention_msg is None:
            return
        match = self.mention_msg.fullmatch(s)
        mention = self.mention.findall(s)
        if match and mention:
            return match.string.replace(mention[0], '', 1).strip()
