from itertools import chain
from logging import CRITICAL, ERROR, INFO, WARN
from traceback import format_exc

from discord import Game, Message
from discord.ext.commands import CommandNotFound, Context

from bot import Yasen
from bot.bot_utils import command_error_handler, format_command_error
from scripts.helpers import code_block


class Listeners:
    def __init__(self, bot: Yasen):
        self.bot = bot

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
        if author.bot:
            return
        pass

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
