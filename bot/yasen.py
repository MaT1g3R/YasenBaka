"""
The yasen bot object
"""
from logging import INFO, WARN
from typing import Optional

from discord import ConnectionClosed, Game, Status
from discord.abc import Messageable
from discord.ext.commands import AutoShardedBot, Context

from config import Config
from data_manager import DataManager
from data_manager.data_utils import get_prefix


class Yasen(AutoShardedBot):
    """
    The yasen bot object
    """

    def __init__(
            self, config: Config, data_manager: DataManager, logger,
            version: str):
        self.data_manager = data_manager
        self.config = config
        self.logger = logger
        self.version = version
        super().__init__(get_prefix)

    @property
    def default_prefix(self):
        return self.config.default_prefix

    @property
    def client_id(self):
        return self.user.id

    @property
    def error_log(self) -> Optional[Messageable]:
        """
        Get the error log channel for the bot.
        :return: the error log channel.
        """
        id_ = self.config.error_log
        if id_ is None:
            return None
        c = self.get_channel(id_)
        return c if isinstance(c, Messageable) else None

    async def send_tb(self, tb: list, header: str):
        """
        Send traceback to error log channel if it exists.
        :param tb: the list of traceback.
        :param header: the header.
        """
        channel = self.error_log
        if not channel:
            return
        await channel.send(header)
        for s in tb:
            await channel.send(s)

    async def on_ready(self):
        """
        Event for when bot gets ready.
        """
        g = Game(name=f'{self.version} | {self.default_prefix}help')
        self.logger.log(INFO, f'Logged in as: {self.user}')
        self.logger.log(INFO, f'Client Id: {self.client_id}')
        await self.try_change_presence(True, game=g)

    async def try_change_presence(
            self, retry: bool, *,
            game: Optional[Game] = None,
            status: Optional[Status] = None,
            afk: bool = False,
            shard_id: Optional[int] = None):
        """
        Try changing presence of the bot.

        :param retry: True to enable retry. Will log out the bot.

        :param game: The game being played. None if no game is being played.

        :param status: Indicates what status to change to. If None, then
        :attr:`Status.online` is used.

        :param afk: Indicates if you are going AFK. This allows the discord
        client to know how to handle push notifications better
        for you in case you are actually idle and not lying.

        :param shard_id: The shard_id to change the presence to. If not specified
        or ``None``, then it will change the presence of every
        shard the bot can see.

        :raises InvalidArgument:
        If the ``game`` parameter is not :class:`Game` or None.

        :raises ConnectionClosed:
        If retry parameter is set to False and ConnectionClosed was raised by
        super().change_presence
        """
        try:
            await self.wait_until_ready()
            await super().change_presence(
                game=game, status=status, afk=afk, shard_id=shard_id)
        except ConnectionClosed as e:
            self.logger.log(WARN, str(e))
            if retry:
                await self.logout()
                await self.login(self.config.token)
                await self.try_change_presence(
                    retry, game=game, status=status, afk=afk, shard_id=shard_id)
            else:
                raise e

    async def on_command_error(self, context: Context, exception):
        """
        Custom command error handling.
        :param context:
        :param exception:
        :return:
        """
        pass
