"""
The yasen bot object
"""
from datetime import datetime, timedelta
from itertools import chain
from logging import CRITICAL, ERROR
from traceback import format_exc
from typing import Optional

from discord import ConnectionClosed, Game, Permissions, Status
from discord.abc import Messageable
from discord.ext.commands import AutoShardedBot, Context
from discord.utils import oauth_url
from wowspy import WowsAsync

from config import Config
from data_manager import DataManager
from data_manager.data_utils import get_prefix
from scripts.helpers import code_block
from world_of_warships import WowsManager
from .anime_searcher import AnimeSearcher


class Yasen(AutoShardedBot):
    """
    The yasen bot object
    """

    def __init__(self, *,
                 logger,
                 version: str,
                 config: Config,
                 start_time: int,
                 wows_api=WowsAsync,
                 data_manager: DataManager,
                 wows_manager: WowsManager,
                 anime_search: AnimeSearcher):
        self.config = config
        self.logger = logger
        self.version = version
        self.start_time = start_time
        self.data_manager = data_manager
        self.anime_search = anime_search
        self.session_manager = anime_search.session_manager
        self.wows_manager = wows_manager
        self.wows_api = wows_api
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
        c = self.get_channel(self.config.error_log)
        return c if isinstance(c, Messageable) else None

    @property
    def uptime(self) -> timedelta:
        """
        Get the uptime of the bot.
        :return: A timedelta object between now and the start time.
        """
        return datetime.now() - datetime.fromtimestamp(self.start_time)

    @property
    def invite_link(self):
        return oauth_url(self.client_id, permissions=Permissions.all())

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

        :param shard_id: The shard_id to change the presence to. If not
        specified or ``None``, then it will change the presence of every
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
            if retry:
                self.logger.warn(str(e))
                await self.logout()
                await self.login(self.config.token)
                await self.try_change_presence(
                    retry, game=game, status=status, afk=afk,
                    shard_id=shard_id)
            else:
                raise e

    def start_bot(self, cogs):
        """
        Start the bot.
        :param cogs: the list of cogs.
        """
        self.remove_command('help')
        for cog in cogs:
            self.add_cog(cog)
        self.run(self.config.token)

    def get_channels(self, type_: Optional[type] = None):
        """
        Get all channels the bot can see with an optional filter.
        :param type_: the type of the channel desired, None for all.
        :return: A generator that retrives all channels with type `type_`
        """
        if type_:
            for guild in self.guilds:
                for channel in guild.channels:
                    if isinstance(channel, type_):
                        yield channel
        else:
            yield from super().get_all_channels()

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
                await arg.send(':x: I ran into a critical error. '
                               'It has been reported to my developer.')
                header = f'**ERROR**\n{ig}'
                lvl = ERROR
                break
        self.logger.log(lvl, log_msg)
        await self.send_tb(header, tb)

    async def send_tb(self, header: str, tb: str):
        """
        Send traceback to error log channel if it exists.
        :param header: the header.
        :param tb: the traceback.
        """
        channel = self.error_log
        if channel:
            await channel.send(header)
            for s in code_block(tb, 'Python'):
                await channel.send(s)
