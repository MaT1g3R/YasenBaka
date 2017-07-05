from pytest import fixture

from data_manager import DataManager
from tests import *


@fixture(scope='function')
def manager():
    _manager = get_manager()
    yield _manager
    clear_db()


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
    player_nums = 4
    guild_ids = random_strs(guild_nums)
    expected = {}
    for guild_id in guild_ids:
        expected[guild_id] = {}
        it = (random_strs(player_nums), random_strs(player_nums),
              random_strs(player_nums))
        for member, region, player_id in zip(it[0], it[1], it[2]):
            entry = {
                'region': region,
                'player_id': player_id
            }
            expected[guild_id][member] = entry
            manager.set_shame(guild_id, member, region, player_id)
            assert manager.get_shame(guild_id, member) == entry
    assert manager.get_all_shame() == expected == manager.shame


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
