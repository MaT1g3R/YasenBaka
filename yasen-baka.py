"""The main bot run file"""
from asyncio import get_event_loop
from pathlib import Path
from sqlite3 import connect
from time import time

from aiohttp import ClientSession

from bot import SessionManager, Yasen, version_info as vs
from bot.logger import get_console_handler, setup_logging
from cogs import *
from config import Config
from data import data_path
from data_manager import DataManager


async def run():
    config = Config(True)
    start_time = int(time())
    logger = setup_logging(start_time, data_path.joinpath('logs'))
    if config.console_logging:
        logger.addHandler(get_console_handler())
    v = f'{vs.releaselevel} {vs.major}.{vs.minor}.{vs.micro}'
    if vs.serial:
        v += f'-{vs.serial}'
    data_manager = DataManager(connect('./tests/test_data/test_db'))
    session_manager = SessionManager(ClientSession(), logger)
    bot = Yasen(
        logger=logger,
        version=v,
        config=config,
        start_time=start_time,
        data_manager=data_manager,
        session_manager=session_manager
    )
    karen_files = [Path(f) for f in data_path.joinpath('Karen').iterdir()]
    kanna_files = [Path(f) for f in data_path.joinpath('Kanna').iterdir()]

    cogs = [Listeners(bot), Fun(bot), Weeb(bot, kanna_files, karen_files),
            BotInfo(bot), Nsfw(bot), Osu(bot), Utility(bot)]
    return bot, cogs


if __name__ == '__main__':
    loop = get_event_loop()
    b, c = loop.run_until_complete(run())
    b.start_bot(c)
