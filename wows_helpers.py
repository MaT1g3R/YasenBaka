import json
import requests


def calc_wtr(expected, actual, coefficients, average_level):
    """
    Calculate WTR of a player based on the WTR formula on Warships today
    :param expected the server average
    :param actual the actual value for the player
    :param coefficients the coefficients 
    :param average_level the average level of the player's ships
    :return: the calculated value
    """
    wins = actual['wins']/expected['wins'] if expected['wins'] > 0 else 0
    damage_dealt = actual['damage_dealt']/expected['damage_dealt'] if expected['damage_dealt'] > 0 else 0
    ship_frags = actual['ship_frags']/expected['ship_frags'] if expected['ship_frags'] > 0 else 0
    capture_points = actual['capture_points']/expected['capture_points'] if expected['capture_points'] > 0 else 0
    dropped_capture_points = actual['dropped_capture_points']/expected['dropped_capture_points'] \
        if expected['dropped_capture_points'] > 0 else 0
    planes_killed = actual['planes_killed']/expected['planes_killed'] if expected['planes_killed'] > 0 else 0

    ship_frags_importance_weight = coefficients['ship_frags_importance_weight']

    wins_weight = coefficients['wins_weight']

    damage_weight = coefficients['damage_weight']

    frags_weight = coefficients['frags_weight']

    capture_weight = coefficients['capture_weight']

    dropped_capture_weight = coefficients['dropped_capture_weight']

    nominal_rating = coefficients['nominal_rating']

    frags = 1.0  # fallback to avoid division by zero

    if expected['planes_killed'] + expected['frags'] > 0:
        aircraft_frags_coef = \
            expected['planes_killed']/(expected['planes_killed'] + ship_frags_importance_weight * expected['frags'])
        ship_frags_coef = 1 - aircraft_frags_coef
        if aircraft_frags_coef == 1:
            frags = planes_killed
        elif ship_frags_coef == 1:
            frags = ship_frags
        else:
            frags = ship_frags*ship_frags_coef + planes_killed*aircraft_frags_coef

    wtr = \
        wins*wins_weight + \
        damage_dealt*damage_weight + \
        frags*frags_weight + \
        capture_points*capture_weight + \
        dropped_capture_points*dropped_capture_weight

    return __adjust(wtr*nominal_rating, average_level, nominal_rating)


def __adjust(value, average_level, base):
    """
    Helper function to adjust the wtr 
    :param value: the wtr value
    :param average_level: the average level of the player
    :param base: the base wtr
    :return: the adjusted wtr value
    """
    neutral_level = 7.5
    per_level_bonus = 0.1
    adjusted_base = value if value < base else base
    for_adjusting = value-base if value-base > 0 else 0
    coef = 1 + (average_level - neutral_level) * per_level_bonus
    return int(adjusted_base + for_adjusting * coef)


def warships_today_url(region, player_id):
    """
    Generate a warships today signiture url for a player
    :param region: the region the player is in
    :param player_id: the player id
    :return: the sig url
    """
    return 'http://{}.warshipstoday.com/signature/{}/dark.png'.format(region, str(player_id))


def find_player_id(region, api, name):
    """
    Search wows for a player based on name
    :param region: the region the player is in 
    :param api: the wows api key
    :param name: the name of the player
    :return: the player's id if found else none
    """
    wows_api_url = \
        'https://api.worldofwarships.{}/wows/account/list/?application_id={}&search={}'.format(region, api, name)
    r = requests.get(wows_api_url).text
    warships_api_respose = json.loads(r)
    try:
        if warships_api_respose["meta"]["count"] < 1:
            return None
    except KeyError:
        return None
    return warships_api_respose["data"][0]["account_id"]


def player_stats(region, api, id_, all_time: bool):
    """
    Returns a detailed dictionary of the player's stats
    :param region: the region of the player
    :param api: the wows api key
    :param id_: the player id
    :param all_time: if want the alltime stats
    :return: the player's stats in a dicionary
    """
    all_time_url = 'https://api.worldofwarships.{}/wows/account/info/' \
                   '?application_id={}&fields=statistics.pvp&account_id={}'.format(region, api, id_)
    recent_url = 'https://api.worldofwarships.{}/wows/account/statsbydate/?application_id={}&account_id={}&fields=pvp'\
        .format(region, api, id_)

    all_time_stats = json.loads(requests.get(all_time_url).content)['data'][id_]['statistics']['pvp']
    if all_time:
        return all_time_stats
    else:
        sliced_stats_dict = json.loads(requests.get(recent_url).content)['data'][id_]['pvp']
        sliced_stats = {}
        for key in sliced_stats_dict:
            sliced_stats = sliced_stats_dict[key]
        res = {}
        for key, val in sliced_stats.items():
            if key in all_time_stats and key in sliced_stats:
                res[key] = all_time_stats[key] - sliced_stats[key]
        return res


def calculate_average_tier(region, api, id_, ship_dict):
    """
    Calculate the average tier for the player
    :param region: the region of the player
    :param api: the wows api key
    :param id_: the player id 
    :param ship_dict: a dictionary of ship id mapped to tier
    :return: the average tier of the player
    """
    ship_stats = player_ship_stats(region, api, id_, ship_dict)
    total_battles = 0
    total_tier = 0
    for key, val in ship_stats.items():
        battles = val['battles']
        tier = ship_dict[key]
        total_battles += battles
        total_tier += tier*battles
    return total_tier/total_battles


def get_ship_tier_dict(region, api):
    """
    Get a dictionary of ship id mapped to tier
    :param region the region for the request
    :param api: the wows api key
    :return: a dictionary of ship id mapped to tier
    """
    url = 'https://api.worldofwarships.{}/wows/encyclopedia/ships/?application_id={}&fields=tier'.format(region, api)
    r = json.loads(requests.get(url).content)
    return r['data']


def player_ship_stats(region, api, id_, ship_dict):
    """
    Get a dictionary of stats mapped to ship for the player
    :param region: the region of the player
    :param api: the wows api key
    :param id_: the player id
    :param ship_dict: a dictionary of all ship ids: tier
    :return: stats mapped to ship for the player
    """
    ship_list = []
    for key in ship_dict:
        ship_list.append(str(key))
    url = 'https://api.worldofwarships.{}/wows/ships/stats/?application_id={}&account_id={}&ship_id='\
        .format(region, api, id_)
    res = {}
    for sub_list in __split_list(ship_list, 90):
        request_ship_param = ','.join(sub_list)
        request_url = url + request_ship_param
        resonse = json.loads(requests.get(request_url).content)
        response_list = resonse['data'][id_]
        for d in response_list:
            res[d['ship_id']] = d
    return res


def __split_list(lst, max_length):
    """
    Split a list into sublists
    :param lst: the list to be split
    :param max_length: the max allowed length of the result
    :return: a list of split up lists
    """
    return [lst[i:i + max_length] for i in range(0, len(lst), max_length)]


_region = 'com'
_api = '506858830d8d4e449b95a5b02d78111c'
_id_ = '1023711050'
print(player_stats('com', _api, _id_, False))
