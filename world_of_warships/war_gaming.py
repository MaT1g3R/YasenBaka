from typing import Optional

from wowspy import Region, WowsAsync


async def __get_id(coro, logger, key):
    try:
        resp = await coro
    except Exception as e:
        logger.warn(str(e))
    else:
        data = resp.get('data', None)
        if not data:
            return
        return data[0].get(key, None)


async def get_player_id(region: Region, wows_api: WowsAsync,
                        logger, search) -> Optional[int]:
    """
    Get player id by search term.
    :param region: the region.
    :param wows_api: the WowsAsync instance.
    :param logger: the logger.
    :param search: the search query.
    :return: the player id.
    """
    coro = wows_api.players(region, search, language='en', limit=1)
    return await __get_id(coro, logger, 'account_id')


async def get_clan_id(region: Region, wows_api: WowsAsync,
                      logger, search) -> Optional[int]:
    """
    Get clan id by search term.
    :param region: the region.
    :param wows_api: the WowsAsync instance.
    :param logger: the logger.
    :param search: the search query.
    :return: the clan id.
    """
    coro = wows_api.clans(region, search=search, language='en', limit=1)
    return await __get_id(coro, logger, 'clan_id')
