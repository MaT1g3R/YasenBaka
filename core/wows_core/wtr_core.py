import json
import requests


def get_coeff(region: str):
    """
    Get the coefficients used for WTR calculation and calculate the average 
    expected server wide
    :param region: the region 
    :return: a tuple of (coefficients, expected_average)
    :rtype: tuple
    """
    coeff_url = 'https://api.{}.warships.today/json/wows/' \
                'ratings/warships-today-rating/coefficients'.format(region)
    coeff_res = json.loads(requests.get(coeff_url).content)
    expected = coeff_res['expected']
    coefficients = coeff_res['coefficients']
    return coefficients, expected


def coeff_all_region():
    """
    Get coefficients and expected average from all regions
    :return: a tuple of dictionaries, (coefficients, expected)
    :rtype: tuple
    """
    coefficients = {}
    expected = {}
    na = get_coeff('na')
    coefficients['na'] = na[0]
    expected['na'] = na[1]

    eu = get_coeff('eu')
    coefficients['eu'] = eu[0]
    expected['eu'] = eu[1]

    asia = get_coeff('asia')
    coefficients['asia'] = asia[0]
    expected['asia'] = asia[1]

    ru = get_coeff('ru')
    coefficients['ru'] = ru[0]
    expected['ru'] = ru[1]

    return coefficients, expected


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
    adjusted_base = min(value, base)
    for_adjusting = max(0, value - base)
    coef = 1 + (average_level - neutral_level) * per_level_bonus
    return adjusted_base + for_adjusting * coef


def wtr_absolute(expected, coeff, actual: dict, ship_dict):
    """
    Calculate the absolute WTR for a player
    :param expected: the expected stats values
    :param coeff: the coefficents used in calculation
    :param actual: the actual stats of the player
    :param ship_dict: dict of ship_id mapped to ship tier
    :return: the wtr of the player
    """
    total = 0
    battles = 0
    for d in expected:
        ship_id = d['ship_id']
        if ship_id not in actual:
            continue
        tier = ship_dict[str(ship_id)]['tier'] if str(ship_id) in ship_dict \
            else 7.5
        stats = actual[ship_id]
        temp_b = stats['battles']
        if temp_b > 0:
            stats_for_calc = {
                "capture_points": stats['capture_points']/temp_b,
                "planes_killed": stats['planes_killed']/temp_b,
                "damage_dealt": stats['damage_dealt']/temp_b,
                "frags": stats['frags']/temp_b,
                "dropped_capture_points":
                    stats['dropped_capture_points']/temp_b,
                "wins": stats['wins']/temp_b
            }
            wtr = calc_wtr(d, stats_for_calc, coeff, tier)
            total += wtr*temp_b
            battles += temp_b
    return round(total/max(battles, 1))


def warships_today_url(region, player_id):
    """
    Generate a warships today signiture url for a player
    :param region: the region the player is in
    :param player_id: the player id
    :return: the sig url
    """
    return 'http://{}.warshipstoday.com/signature/{}/dark.png'\
        .format(region, str(player_id))


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
