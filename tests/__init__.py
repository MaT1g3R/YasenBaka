from pathlib import Path
from random import sample
from sqlite3 import connect

from data_manager import DataManager

__db_path = str(
    Path(
        Path(__file__).parent.joinpath('test_data').joinpath('test_db')
    ).resolve()
)


def get_manager():
    return DataManager(connect(__db_path))


def clear_db():
    with connect(__db_path) as connection:
        connection.execute('DELETE FROM nsfw')
        connection.execute('DELETE FROM prefix')
        connection.execute('DELETE FROM shame')
        connection.commit()


def random_strs(amt):
    return [str(i) for i in sample(range(1, 10000), amt)]


__all__ = ['get_manager', 'clear_db', 'random_strs']
