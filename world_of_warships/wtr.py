from wowspy import Region, WowsAsync

from bot import SessionManager
from scripts.helpers import try_divide


CONVERT_REGION = {
    Region.NA: 'na',
    Region.EU: 'eu',
    Region.RU: 'ru',
    Region.AS: 'asia'
}
async def get_coeff(region: str, session_manager: SessionManager) -> dict:
    """
    Get the coefficients used for WTR calculations.
    expected server wide
    :param region: the region.
    :param session_manager: the SessionManager.
    :return: the coefficients used for WTR calculations.
    """
    return await session_manager.get_json(
        f'https://api.{region}.warships.today/json/wows/ratings/'
        f'warships-today-rating/coefficients'
    )


async def coeff_all_region(session_manager: SessionManager) -> dict:
    """
    Get coefficients for all regions.
    :param session_manager: the SessionManager.
    :return: coefficients for all regions.
    """
    res = {}
    for region in ('na', 'eu', 'ru', 'asia'):
        resp = await get_coeff(region, session_manager)
        tmp = {}
        __expected = resp.get('expected', None)
        expected = {}
        for entry in __expected:
            expected[str(entry['ship_id'])] = entry
        for key in resp:
            if key == 'expected':
                continue
            tmp[key] = resp[key]
        tmp['expected'] = expected
        res[region] = tmp
    return res


async def get_ship_dicts(wows_api: WowsAsync):
    res = {}
    for region in Region:
        resp = await wows_api.warships(region, fields='tier', language='en')
        data = resp['data']
        res[region.name] = {key: val['tier'] for key, val in data.items()}
    return res


def calc_wtr(expected, actual, coefficients, average_level) -> float:
    """
    Calculate WTR of a player based on the WTR formula on Warships today.
    :param expected: the server average
    :param actual: the actual value for the player
    :param coefficients: the coefficients
    :param average_level: the average level of the player's ships
    :return: the calculated value
    """
    wins = try_divide(actual['wins'], expected['wins'])
    damage_dealt = try_divide(actual['damage_dealt'], expected['damage_dealt'])
    ship_frags = try_divide(actual['frags'], expected['frags'])
    capture_points = try_divide(
        actual['capture_points'], expected['capture_points']
    )
    dropped_capture_points = try_divide(
        actual['dropped_capture_points'], expected['dropped_capture_points']
    )
    planes_killed = try_divide(
        actual['planes_killed'], expected['planes_killed']
    )

    ship_frags_importance_weight = coefficients['ship_frags_importance_weight']

    wins_weight = coefficients['wins_weight']

    damage_weight = coefficients['damage_weight']

    frags_weight = coefficients['frags_weight']

    capture_weight = coefficients['capture_weight']

    dropped_capture_weight = coefficients['dropped_capture_weight']

    nominal_rating = coefficients['nominal_rating']

    if expected['planes_killed'] + expected['frags'] > 0:
        aircraft_frags_coef = (
            expected['planes_killed'] / (
                expected['planes_killed'] +
                ship_frags_importance_weight * expected['frags'])
        )

        ship_frags_coef = 1 - aircraft_frags_coef
        if aircraft_frags_coef == 1:
            frags = planes_killed
        elif ship_frags_coef == 1:
            frags = ship_frags
        else:
            frags = ((ship_frags * ship_frags_coef) +
                     (planes_killed * aircraft_frags_coef))
    else:
        frags = 1

    wtr = ((wins * wins_weight) +
           (damage_dealt * damage_weight) +
           (frags * frags_weight) +
           (capture_points * capture_weight) +
           (dropped_capture_points * dropped_capture_weight))

    return __adjust(wtr * nominal_rating, average_level, nominal_rating)


def __adjust(value, average_level, base) -> float:
    """
    Helper function to adjust the wtr.
    :param value: the wtr value.
    :param average_level: the average level of the player.
    :param base: the base wtr.
    :return: the adjusted wtr value.
    """
    neutral_level = 7.5
    per_level_bonus = 0.1
    adjusted_base = min(value, base)
    for_adjusting = max(0, value - base)
    coef = 1 + (average_level - neutral_level) * per_level_bonus
    return adjusted_base + for_adjusting * coef


async def wtr_absolute(all_expected, coeff, actual: dict, ship_dict) -> int:
    """
    Calculate the absolute WTR for a player
    :param all_expected: the expected stats values
    :param coeff: the coefficents used in calculation
    :param actual: the actual stats of the player
    :param ship_dict: dict of ship_id mapped to ship tier
    :return: the wtr of the player
    """
    total, total_battles = 0, 0
    for ship_id, stat in actual.items():
        expected = all_expected.get(str(ship_id), None)
        if not expected:
            continue
        tier = ship_dict.get(ship_id, 7.5)
        wtr, battles = await __wtr(expected, stat, tier, coeff)
        total += wtr
        total_battles += battles
    return round(total / max((total_battles, 1)))


async def __wtr(expected, stats, tier, coeff):
    """
    Helper function for wtr_absolute
    See wtr_absolute for parameters
    """
    battles = stats.get('battles', None)
    if battles:
        stats_for_calc = {
            'capture_points': stats['capture_points'] / battles,
            'planes_killed': stats['planes_killed'] / battles,
            'damage_dealt': stats['damage_dealt'] / battles,
            'frags': stats['frags'] / battles,
            'dropped_capture_points': stats['dropped_capture_points'] / battles,
            'wins': stats['wins'] / battles
        }
        wtr = calc_wtr(expected, stats_for_calc, coeff, tier)
        total = wtr * battles
        return total, battles
    return 0, 0


def choose_colour(wtr: int) -> int:
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
