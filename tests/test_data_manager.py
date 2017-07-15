from random import randint, sample

from pytest import fixture

from data_manager import DataManager
from tests import *


@fixture(scope='function')
def manager():
    _manager = get_manager()
    yield _manager
    clear_db()


def random_players(amt):
    """
    Generate a list of random players.
    :param amt: the amount of players to generate.
    :return: a list of random players.
    """
    ids = random_strs(5 * amt)
    players = []
    _regions = ('NA', 'EU', 'RU', 'AS')
    for _ in range(amt):
        regions = sample(_regions, randint(1, 4))
        player = {}
        for region in regions:
            player[region] = ids.pop()
        res = (player, ids.pop())
        players.append(res)
    return players


def test_prefix(manager: DataManager):
    """
    Test prefix methods in DataManager
    """
    assert manager.get_all_prefix() == {}
    expected = {}
    amt = 10
    prefixes, ids = random_strs(amt), random_strs(amt)
    for id_, prefix in zip(prefixes, ids):
        manager.set_prefix(id_, prefix)
        assert manager.get_prefix(id_) == prefix
        expected[id_] = prefix
    assert manager.get_all_prefix() == expected == manager.prefix


def test_shame(manager: DataManager):
    """
    Test shame methods in DataManager
    """
    assert manager.get_all_shame() == {}
    guild_nums = 10
    guild_ids = random_strs(guild_nums)
    expected = {}
    for guild in guild_ids:
        player_amt = randint(1, 10)
        expected[guild] = {}
        for player, member in random_players(player_amt):
            for reg, id_ in player.items():
                manager.set_shame(guild, member, reg, id_)
                assert manager.get_shame(guild, member, reg) == id_
            expected[guild][member] = player
    assert expected == manager.get_all_shame() == manager.shame


def test_nsfw(manager: DataManager):
    """
    Test nsfw methods in DataManager
    """
    sites = random_strs(7)
    expected = {}
    for site in sites:
        tags = random_strs(60)
        expected[site] = tags
        manager.set_nsfw_tags(site, tags)
    assert manager.get_nsfw_tags() == expected == manager.nsfw
