import re
from logging import INFO, WARN
from traceback import format_exc

from discord import File, Game, Message, TextChannel
from discord.abc import Messageable
from discord.ext.commands import CommandNotFound, Context

from bot import Yasen
from bot.bot_utils import command_error_handler, format_command_error
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
        _mention = f'<@!?{self.bot.client_id}>'
        self.mention = re.compile(_mention)
        self.mention_msg = re.compile(f'^{_mention}\s*[^\s]+.*$')

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

        is_guild = isinstance(channel, TextChannel)
        stripped = self.__strip_mention(content)
        if stripped and stripped.lower() == 'prefix' and is_guild:
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
