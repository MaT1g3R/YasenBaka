import json
import requests
from helpers import split_list, get_date
from discord import Embed


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
    damage_dealt = actual['damage_dealt']/expected['damage_dealt'] \
        if expected['damage_dealt'] > 0 else 0
    ship_frags = actual['frags']/expected['frags'] \
        if expected['frags'] > 0 else 0
    capture_points = actual['capture_points']/expected['capture_points'] \
        if expected['capture_points'] > 0 else 0
    dropped_capture_points = actual['dropped_capture_points'] / expected[
        'dropped_capture_points'] \
        if expected['dropped_capture_points'] > 0 else 0
    planes_killed = actual['planes_killed']/expected['planes_killed'] \
        if expected['planes_killed'] > 0 else 0

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
            expected['planes_killed']/(expected['planes_killed'] +
                                       ship_frags_importance_weight
                                       * expected['frags'])
        ship_frags_coef = 1 - aircraft_frags_coef
        if aircraft_frags_coef == 1:
            frags = planes_killed
        elif ship_frags_coef == 1:
            frags = ship_frags
        else:
            frags = ship_frags*ship_frags_coef + planes_killed *\
                                                 aircraft_frags_coef

    wtr = \
        wins*wins_weight + \
        damage_dealt*damage_weight + \
        frags*frags_weight + \
        capture_points*capture_weight + \
        dropped_capture_points*dropped_capture_weight

    return int(__adjust(wtr*nominal_rating, average_level, nominal_rating))


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
    adjusted_base = min(value, base)
    for_adjusting = max(0, value - base)
    coef = 1 + (average_level - neutral_level) * per_level_bonus
    return adjusted_base + for_adjusting * coef


def warships_today_url(region, player_id):
    """
    Generate a warships today signiture url for a player
    :param region: the region the player is in
    :param player_id: the player id
    :return: the sig url
    """
    return 'http://{}.warshipstoday.com/signature/{}/dark.png'\
        .format(region, str(player_id))


def find_player_id(region, api, name):
    """
    Search wows for a player based on name
    :param region: the region the player is in 
    :param api: the wows api key
    :param name: the name of the player
    :return: the player's id if found else none
    """
    wows_api_url = 'https://api.worldofwarships.{}/wows/account/list/?' \
                   'application_id={}&search={}'.format(region, api, name)
    r = requests.get(wows_api_url).text
    warships_api_respose = json.loads(r)
    try:
        if warships_api_respose["meta"]["count"] < 1:
            return None
    except KeyError:
        return None
    return warships_api_respose["data"][0]["account_id"]


def player_stats(region, api, id_):
    """
    Returns a detailed dictionary of the player's stats
    :param region: the region of the player
    :param api: the wows api key
    :param id_: the player id
    :return: the player's stats in a dicionary
    """
    dates = []
    for i in range(0, 6):
        dates.append(get_date(i))
    id_ = str(id_)
    all_time_url = 'https://api.worldofwarships.{}/wows/account/info/' \
                   '?application_id={}&fields=hidden_profile,statistics.pvp&' \
                   'account_id={}'.format(region, api, id_)
    response = json.loads(requests.get(all_time_url).content)['data'][id_]
    if response['hidden_profile']:
        return None
    all_time_stats = response['statistics']['pvp']
    sliced_stats = None
    for date in dates:
        try:
            recent_url = 'https://api.worldofwarships.{}/wows/account/' \
                         'statsbydate/?application_id={}&dates={}&account_id=' \
                         '{}&fields=pvp'.format(region, api, date, id_)
            sliced_stats = json.loads(requests.get(recent_url).content
                                      )['data'][id_]['pvp'][date]
        except KeyError and TypeError:
            continue
        if all_time_stats['battles'] - sliced_stats['battles'] > 0:
            break
    if sliced_stats is None \
            or all_time_stats['battles'] - sliced_stats['battles'] == 0:
        return all_time_stats, None
    res = {}
    for key, val in sliced_stats.items():
        if key in all_time_stats and key in sliced_stats:
            res[key] = all_time_stats[key] - sliced_stats[key]
    return all_time_stats, res


def calculate_average_tier(region, api, id_, ship_dict, ship_list):
    """
    Calculate the average tier for the player
    :param region: the region of the player
    :param api: the wows api key
    :param id_: the player id 
    :param ship_dict: a dictionary of ship id mapped to tier
    :param ship_list a list of all ship ids
    :return: the average tier of the player
    """
    ship_stats = player_ship_stats(region, api, id_, ship_list)
    total_battles = 0
    total_tier = 0
    for key, val in ship_stats.items():
        battles = val['battles']
        tier = ship_dict[str(key)]['tier']
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
    url = 'https://api.worldofwarships.{}/wows/encyclopedia/ships/' \
          '?application_id={}&fields=tier'.format(region, api)
    r = json.loads(requests.get(url).content)
    return r['data']


def player_ship_stats(region, api, id_, ship_list):
    """
    Get a dictionary of stats mapped to ship for the player
    :param region: the region of the player
    :param api: the wows api key
    :param id_: the player id
    :param ship_list: a list of all ship ids
    :return: stats mapped to ship for the player
    """
    url = 'https://api.worldofwarships.{}/wows/ships/stats/?application_id={}' \
          '&account_id={}&fields=battles,ship_id&ship_id='\
        .format(region, api, id_)
    res = {}
    for sub_list in split_list(ship_list, 90):
        request_ship_param = ','.join(sub_list)
        request_url = url + request_ship_param
        resonse = json.loads(requests.get(request_url).content)
        response_list = resonse['data'][id_]
        try:
            for d in response_list:
                res[d['ship_id']] = d
        except TypeError:
            continue
    return res


def calculate_coeff(region):
    """
    Calculated the average expected server wide
    :return: the average expected in a dictionary format same as expected
    """
    coeff_url = 'https://api.{}.warships.today/json/wows/' \
                'ratings/warships-today-rating/coefficients'.format(region)
    coeff_res = json.loads(requests.get(coeff_url).content)
    expected = coeff_res['expected']
    n = len(expected)
    res = {}
    for d in expected:
        for key in d:
            if key not in res:
                res[key] = d[key]
            else:
                res[key] += d[key]
    for key, val in res.items():
        res[key] = val/n
    return coeff_res['coefficients'], res


def choose_colour(wtr):
    """
    Choose a colour to represent the wtr
    :param wtr: the wtr
    :return: a hex integer of the colour
    """
    if wtr < 300:
        return 0x930D0D
    elif wtr < 700:
        return 0xCD3333
    elif wtr < 900:
        return 0xCC7A00
    elif wtr < 1000:
        return 0xCCB800
    elif wtr < 1100:
        return 0x4D7326
    elif wtr < 1200:
        return 0x4099BF
    elif wtr < 1400:
        return 0x3972C6
    elif wtr < 1800:
        return 0x793DB6
    elif wtr >= 1800:
        return 0x401070
    else:
        return 0x930D0D


def build_embed(region, api, id_, coefficients, expected, ship_dict, ship_list):
    """
    Build an embed object of player's stats
    :param region: the player's region
    :param api: the wows api key
    :param id_: the player id_
    :param coefficients: from coeff.json provided by warships today
    :param expected: from coeff.json provided by warships today
    :param ship_dict: ship_id: tier
    :param ship_list: a list of all ship ids
    :return: a discord embed object
    """
    id_ = str(id_)
    stats = player_stats(region, api, id_)
    if stats is not None:
        recent_stats = stats[1]
        all_time_stats = stats[0]
        nick_url = 'https://api.worldofwarships.{}/wows/account/' \
                   'info/?application_id={}&account_id={}&fields=nickname'\
            .format(region, api, id_)
        nick_name = json.loads(requests.get(nick_url).content
                               )['data'][id_]['nickname']
        battles = all_time_stats['battles']
        all_time_actual = {
            "capture_points": all_time_stats['capture_points'] / battles
            if battles > 0 else 0,
            "planes_killed": (all_time_stats['planes_killed'] / battles)
            if battles > 0 else 0,
            "damage_dealt": (all_time_stats['damage_dealt'] / battles)
            if battles > 0 else 0,
            "frags": (all_time_stats['frags'] / battles) if battles > 0 else 0,
            "dropped_capture_points":
                all_time_stats['dropped_capture_points'] / battles
                if battles > 0 else 0,
            "wins": (all_time_stats['wins'] / battles) if battles > 0 else 0
        }
        average_tier = calculate_average_tier(region, api, id_,
                                              ship_dict, ship_list)
        all_time_wtr_val = calc_wtr(expected, all_time_actual,
                                    coefficients, average_tier)

        main_hits = all_time_stats['main_battery']['hits']
        main_shots = all_time_stats['main_battery']['shots']
        second_hits = all_time_stats['second_battery']['hits']
        second_shots = all_time_stats['second_battery']['shots']
        torp_hits = all_time_stats['torpedoes']['hits']
        torp_shots = all_time_stats['torpedoes']['shots']

        damage_dealt = all_time_stats['damage_dealt']
        max_damage_dealt = all_time_stats['max_damage_dealt']
        planes_killed = all_time_stats['planes_killed']
        wins = all_time_stats['wins']
        xp = all_time_stats['xp']
        survived_battles = all_time_stats['survived_battles']
        ships_spotted = all_time_stats['ships_spotted']
        warships_killed = all_time_stats['frags']
        deaths = battles - survived_battles

        # max_damage_dealt = str(all_time_stats['max_damage_dealt'])
        # max_xp = str(all_time_stats['max_xp'])
        # max_planes_killed = str(all_time_stats['max_planes_killed'])
        eb = Embed(colour=choose_colour(all_time_wtr_val))
        eb.set_author(name=nick_name)
        if battles > 0:
            win_rate = "{0:.2f}".format((wins / battles) * 100) + "%"
            avg_dmg = str(int(damage_dealt / battles))
            avg_exp = str(int(xp / battles))
            survival_rate = "{0:.2f}".format(
                (survived_battles / battles) * 100) + "%"
            avg_kills = str("{0:.2f}".format(warships_killed / battles))
            avg_plane_kills = str("{0:.2f}".format(planes_killed / battles))
            avg_spotted = str("{0:.2f}".format(ships_spotted / battles))
            kda = "{0:.2f}".format(warships_killed / deaths) if deaths > 0 \
                else '\u221E'
            main_hitrate = "{0:.2f}".format((main_hits / main_shots) * 100) + \
                           "%" if main_shots > 0 else '0%'
            second_hitrate = "{0:.2f}".format((second_hits /
                                               second_shots) * 100) + \
                             "%" if second_shots > 0 else '0%'
            torp_hitrate = "{0:.2f}".format((torp_hits / torp_shots) * 100) +\
                           "%" if torp_shots > 0 else '0%'
            eb.add_field(name='All Time Stats',
                         value=str(battles) + ' Battles', inline=False)
            eb.add_field(name='WTR', value=str(all_time_wtr_val))
            eb.add_field(name='Win Rate', value=win_rate)  # 1
            eb.add_field(name='Max Damage Dealt', value=str(max_damage_dealt))
            eb.add_field(name='Average Damage', value=avg_dmg)  # 2
            eb.add_field(name='Average Experience', value=avg_exp)  # 4
            eb.add_field(name='Average Kills', value=avg_kills)  # 6
            eb.add_field(name='Average Plane Kills', value=avg_plane_kills)  # 7
            eb.add_field(name='Average Ships Spotted', value=avg_spotted)  # 9
            eb.add_field(name='Main Battery Hit Rate', value=main_hitrate)  # 10
            eb.add_field(name='Secondary Battery Hit Rate',
                         value=second_hitrate)  # 11
            eb.add_field(name='Torpedo Hit Rate', value=torp_hitrate)  # 12
            eb.add_field(name='Survival Rate', value=survival_rate)  # 13
            eb.add_field(name='Kills/Deaths', value=kda)  # 14
            if recent_stats is not None:
                recent_battles = recent_stats['battles']
                recent_actual = {
                    "capture_points":
                        recent_stats['capture_points'] / recent_battles
                        if recent_battles > 0 else 0,
                    "planes_killed":
                        recent_stats['planes_killed'] / recent_battles
                        if recent_battles > 0 else 0,
                    "damage_dealt":
                        recent_stats['damage_dealt'] / recent_battles
                        if recent_battles > 0 else 0,
                    "frags":
                        recent_stats['frags'] / recent_battles
                        if recent_battles > 0 else 0,
                    "dropped_capture_points":
                        recent_stats['dropped_capture_points'] / recent_battles
                        if recent_battles > 0 else 0,
                    "wins": recent_stats['wins'] / recent_battles
                    if recent_battles > 0 else 0
                }
                recent_wtr_val = calc_wtr(expected, recent_actual,
                                          coefficients, average_tier)
                eb.add_field(name='Recent Stats',
                             value=str(recent_battles) + ' Battles',
                             inline=False)
                eb.add_field(name='WTR', value=str(recent_wtr_val))
                eb.add_field(name='Win Rate',
                             value=str("{0:.2f}".format(
                                 recent_actual['wins']*100)) + '%')
                eb.add_field(name='Average Damage',
                             value=str(int(recent_actual['damage_dealt'])))
                eb.add_field(name='Average Kills',
                             value=str("{0:.2f}"
                                       .format(recent_actual['frags'])))
        else:
            eb.add_field(name='Error',
                         value='The player doesn\'t have any battles played')
        return eb
    else:
        return None
