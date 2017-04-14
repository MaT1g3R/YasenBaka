from wowspy.wowspy import Region, Wows

from core.helpers import get_date


def find_player_id(region: Region, api: Wows, name):
    """
    Search wows for a player based on name
    :param region: the region the player is in 
    :param api: the wows api object
    :param name: the name of the player
    :return: the player's id if found else none
    """
    warships_api_respose = \
        api.players(region, name, fields='account_id', limit=1)
    try:
        if warships_api_respose["meta"]["count"] < 1:
            return None
    except KeyError:
        return None
    return warships_api_respose["data"][0]["account_id"]


def player_stats(region: Region, api: Wows, id_: int):
    """
    Returns a detailed dictionary of the player's stats
    :param region: the region of the player
    :param api: the wows api 
    :param id_: the player id
    :return: (all_time_stats, recent_stats)
    """
    dates = [get_date(i) for i in range(6)]
    all_time_response = api.player_personal_data(
        region, id_, fields='hidden_profile,statistics.pvp',
        language='en')['data'][str(id_)]
    if all_time_response['hidden_profile']:
        return None
    all_time_stats = all_time_response['statistics']['pvp']
    date_stats = api.player_statistics_by_date(region, id_,
                                               dates=','.join(dates),
                                               language='en', fields='pvp'
                                               )['data'][str(id_)]['pvp']
    recent_stats = {}
    if date_stats is None:
        return all_time_stats, None
    for date in reversed(dates):
        if date in date_stats \
                and all_time_stats['battles'] - date_stats[date]['battles'] > 0:
            for key, val in date_stats[date].items():
                if key in all_time_stats:
                    recent_stats[key] = all_time_stats[key] - \
                                        date_stats[date][key]
            break

    return all_time_stats, recent_stats


def get_ship_tier_dict(region: Region, api: Wows):
    """
    Get a dictionary of ship id mapped to tier
    :param region the region for the request
    :param api: the wows api 
    :return: a dictionary of ship id mapped to tier
    """
    return api.warships(region, language='en', fields='tier')['data']


def get_all_ship_tier(api: Wows):
    """
    Get ship id mapped to tier for all regions
    :param api: wows api
    :return: ship id mapped to tier for all regions
    """
    na = api.warships(api.region.NA, language='en', fields='tier')['data']
    eu = api.warships(api.region.EU, language='en', fields='tier')['data']
    ru = api.warships(api.region.RU, language='en', fields='tier')['data']
    asia = api.warships(api.region.AS, language='en', fields='tier')['data']
    return {
        'na': na,
        'eu': eu,
        'ru': ru,
        'asia': asia
    }


def player_ship_stats(region: Region, api, id_: int):
    """
    Get a dictionary of stats mapped to ship for the player
    :param region: the region of the player
    :param api: the wows api 
    :param id_: the player id
    :return: stats mapped to ship for the player
    """
    res = {}
    response = api.statistics_of_players_ships(
        region, account_id=id_)['data'][str(id_)]
    for d in response:
        res[d['ship_id']] = d['pvp']
    return res
