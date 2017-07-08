import re
from itertools import chain
from logging import CRITICAL, ERROR, INFO, WARN
from traceback import format_exc

from discord import File, Game, Message, TextChannel
from discord.abc import Messageable
from discord.ext.commands import CommandNotFound, Context

from bot import Yasen
from bot.bot_utils import command_error_handler, format_command_error
from data import data_path
from data_manager.data_utils import get_prefix
from scripts.helpers import code_block


class Listeners:
    """
    Class for event listeners.
    """

    def __init__(self, bot: Yasen):
        self.bot = bot
        _mention = f'<@!?{self.bot.client_id}>'
        self.mention = re.compile(_mention)
        self.mention_msg = re.compile(f'^{mention}\s*[^\s]+.*$')
        self.o7 = File(str(data_path.joinpath('o7.gif')))

    async def on_ready(self):
        """
        Event for when bot gets ready.
        """
        g = Game(name=f'{self.bot.version} | {self.bot.default_prefix}help')
        self.bot.logger.log(INFO, f'Logged in as: {self.bot.user}')
        self.bot.logger.log(INFO, f'Client Id: {self.bot.client_id}')
        await self.bot.try_change_presence(True, game=g)

    async def on_command_error(self, context: Context, exception):
        """
        Custom command error handling.
        :param context:
        :param exception:
        """
        if isinstance(exception, CommandNotFound):
            return
        try:
            res = command_error_handler(exception)
        except Exception as e:
            tb = format_exc()
            msg, triggered = format_command_error(e, context)
            self.bot.logger.log(WARN, f'\n{msg}\n\n{tb}')
            await context.send(f'{msg}')
            await self.__send_tb(
                f'**WARNING** Triggered message:\n{triggered}', tb
            )
        else:
            await context.send(res)

    async def on_error(self, event_method, *args, **kwargs):
        """
        General error handling for discord
        Check :func:`discord.Client.on_error` for more details.
        """
        ig = 'Ignoring exception in {}\n'.format(event_method)
        tb = format_exc()
        log_msg = f'\n{ig}\n{tb}'
        header = f'**CRITICAL**\n{ig}'
        lvl = CRITICAL
        for arg in chain(args, kwargs.values()):
            if isinstance(arg, Context):
                await arg.send('')
                header = f'**ERROR**\n{ig}'
                lvl = ERROR
                break
        self.bot.logger.log(lvl, log_msg)
        await self.__send_tb(header, tb)

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

        is_guild = isinstance(channel, TextChannel)
        stripped = self.__strip_mention(content)
        if stripped.lower() == 'prefix' and is_guild:
            msg = (f'The prefix for this guild is: `{prefix}`\n'
                   f'`{prefix}prefix set <YOUR_PREFIX>` to set the '
                   f'prefix for this guild.\n`{prefix} reset` to reset'
                   f' the prefix for this guild to default. `({prefix})`')
            await channel.send(msg)
        elif stripped:
            resp = await self.bot.api_consumer.program_o(stripped, author.id)
            await channel.send(resp)
        elif content == '/o/':
            await channel.send('\\o\\')
        elif content == '\\o\\':
            await channel.send('/o/')
        elif content == 'o7':
            await channel.send(file=self.o7)

    async def __send_tb(self, header: str, tb: str):
        """
        Send traceback to error log channel if it exists.
        :param header: the header.
        :param tb: the traceback.
        """
        channel = self.bot.error_log
        if channel:
            await channel.send(header)
            for s in code_block(tb, 'Python'):
                await channel.send(s)

    def __strip_mention(self, s: str):
        """
        Strip message starts with mention to the bot.
        :param s: the input string.
        :return: the message without the mention.
        """
        match = self.mention_msg.fullmatch(s)
        mention = self.mention.findall(s)
        if match and mention:
            return match.string.replace(mention[0], '', count=1).strip()
