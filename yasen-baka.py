"""The main bot run file"""
from asyncio import get_event_loop
from os import getenv
from pathlib import Path
from sqlite3 import connect
from time import time

from aiohttp import ClientSession
from wowspy import WowsAsync

from bot import AnimeSearcher, Yasen, version_info as vs
from bot.logger import get_console_handler, setup_logging
from cogs import *
from config import Config
from data import data_path
from data_manager import DataManager
from scripts.clear_cache import clean
from world_of_warships import WowsManager

IN_DOCKER = str(getenv('IN_DOCKER')) == '1'
DB_PATH = Path('/db') if IN_DOCKER else data_path


async def run():
    session = ClientSession()
    config = Config('config.json')
    start_time = int(time())
    logger = setup_logging(start_time, data_path.joinpath('logs'))
    if config.console_logging:
        logger.addHandler(get_console_handler())
    v = f'{vs.releaselevel} {vs.major}.{vs.minor}.{vs.micro}'
    if vs.serial:
        v += f'-{vs.serial}'
    anime_search = await AnimeSearcher.from_sqlite(
        {'user': config.mal_user, 'password': config.mal_pass},
        DB_PATH / 'minoshiro.db',
        cache_pages=1, cache_mal_entries=40, logger=logger
    )
    session_manager = anime_search.session_manager
    data_manager = DataManager(connect(f'{DB_PATH / "yasen_db"}'))
    wows_api = WowsAsync(config.wows, session)
    wows_manager = await WowsManager.wows_manager(
        session_manager, wows_api, logger
    )
    bot = Yasen(
        logger=logger,
        version=v,
        config=config,
        start_time=start_time,
        data_manager=data_manager,
        anime_search=anime_search,
        wows_manager=wows_manager,
        wows_api=wows_api
    )
    karen_files = [Path(f) for f in data_path.joinpath('Karen').iterdir()]
    kanna_files = [Path(f) for f in data_path.joinpath('Kanna').iterdir()]

    cogs = [Listeners(bot), Fun(bot), Weeb(bot, kanna_files, karen_files),
            BotInfo(bot), Nsfw(bot), Osu(bot), Utility(bot), Moderation(bot),
            WorldOfWarships(bot), Music(bot), OwnerOnly(bot)]
    return bot, cogs


if __name__ == '__main__':
    clean(('dumps', 'music_cache'))
    loop = get_event_loop()
    b, c = loop.run_until_complete(run())
    try:
        b.start_bot(c)
    except KeyboardInterrupt:
        loop.close()
        exit(0)
