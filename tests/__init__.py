from random import sample
from sqlite3 import connect

from data_manager import DataManager

__tables = [
    'CREATE TABLE nsfw('
    'site VARCHAR NOT NULL,'
    'tag VARCHAR NOT NULL,'
    'UNIQUE (site, tag)'
    ')',

    'CREATE TABLE prefix('
    'guild_id VARCHAR PRIMARY KEY,'
    'prefix VARCHAR NOT NULL'
    ')',

    'CREATE TABLE shame('
    'guild_id VARCHAR NOT NULL,'
    'member_id VARCHAR NOT NULL,'
    'region VARCHAR NOT NULL,'
    'player_id VARCHAR NOT NULL,'
    'UNIQUE (guild_id, member_id, region)'
    ')',

    'CREATE TABLE skip_count('
    'guild_id VARCHAR PRIMARY KEY,'
    'count INT NOT NULL'
    ')'
]


def get_manager():
    conn = connect(':memory:')
    for sql in __tables:
        conn.execute(sql)
    return DataManager(conn)


def random_strs(amt):
    return [str(i) for i in sample(range(1, 10000), amt)]


__all__ = ['get_manager', 'random_strs']
