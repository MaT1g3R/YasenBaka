from wowspy.wowspy import Region, Wows

from core.helpers import get_date, combine_dict


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


def all_time_stats(region: Region, api: Wows, id_):
    """
    Returns a detailed dictionary of the player's stats
    :param region: the region of the player
    :param api: the wows api 
    :param id_: the player id
    :return: all time stats of the player
    """
    all_time_response = api.player_personal_data(
        region, id_, fields='hidden_profile,statistics.pvp',
        language='en')['data']
    no_hidden = {k: all_time_response[k] for k in all_time_response
                 if all_time_response[k]['hidden_profile'] is False}

    if no_hidden:
        res = combine_dict(list(no_hidden.values()))
        return res['statistics']['pvp']
    else:
        return None


def recent_stats(region: Region, api: Wows, id_: int, all_time_stats_: dict):
    """
    Get the recent stats of the player
    :param region: the region of the player
    :param api: the wows api
    :param id_: the id of ther player
    :param all_time_stats_: all time stats of the player
    :return: the recent stats of the player
    """
    dates = [get_date(i) for i in range(6)]
    date_stats = api.player_statistics_by_date(region, id_,
                                               dates=','.join(dates),
                                               language='en', fields='pvp'
                                               )['data'][str(id_)]['pvp']
    recent_stats_ = {}
    if date_stats is None:
        return None
    for date in reversed(dates):
        if date in date_stats and all_time_stats_['battles'] - \
                date_stats[date]['battles'] > 0:
            for key, val in date_stats[date].items():
                if key in all_time_stats_:
                    recent_stats_[key] = all_time_stats_[key] - \
                                         date_stats[date][key]
            break
    return recent_stats_ if 'battles' in recent_stats_ \
                            and recent_stats_['battles'] > 0 else None


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
    # ru = api.warships(api.region.RU, language='en', fields='tier')['data']
    asia = api.warships(api.region.AS, language='en', fields='tier')['data']
    return {
        'na': na,
        'eu': eu,
        'ru': None,
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
    hidden = api.player_personal_data(
        region, id_, fields='hidden_profile',
        language='en')['data'][str(id_)]
    if hidden['hidden_profile']:
        return None
    else:
        res = {}
        response = api.statistics_of_players_ships(
            region, account_id=id_,
            fields='pvp.battles,pvp.damage_dealt,pvp.wins,'
                   'pvp.survived_battles,pvp.torpedoes,pvp.frags,'
                   'pvp.main_battery,pvp.second_battery,pvp.ships_spotted,'
                   'pvp.planes_killed,pvp.xp,pvp.capture_points,'
                   'pvp.dropped_capture_points,ship_id',
            language='en')
        response = response['data'][str(id_)]
        for d in response:
            res[d['ship_id']] = d['pvp']
        return res


def list_player_ship_stats(region: Region, api, id_: list):
    """
    Get combined ship stats for a list of players
    :param region: the region
    :param api: the wows api
    :param id_: a list of player ids
    :return: the combined ship stats of the list of players
    """
    res = []
    for i in id_:
        try:
            temp = player_ship_stats(region, api, i)
            if temp is not None:
                res.append(temp)
        except KeyError:
            continue
    res = combine_dict(res)
    return res


def find_clan_id(region: Region, api: Wows, search: str):
    """
    Search for a clan id
    :param region: the region of the clan
    :param api: the wows api
    :param search: the search query
    :return: the clan id if found else None
    """
    res = api.clans(
        region, language='en', limit=1, search=search, fields='clan_id')['data']
    return res[0]['clan_id'] if res else None


def get_clan_info(region: Region, api: Wows, id_: int):
    """
    Get detailed info about a clan
    :param region: the region
    :param api: the wows api
    :param id_: the clan id
    :return: the info about the clan
    """
    return api.clan_details(
        region, id_, fields='-clan_id,-old_name,-renamed_at,-old_tag',
        language='en')['data'][str(id_)]


def get_player_clan_info(region: Region, api: Wows, id_: int):
    """
    Get player's clan info
    :param region: th region
    :param api: wows api
    :param id_: the player id
    :return: the player's clan info
    """
    return api.player_clan_data(region, id_)['data'][str(id_)]
