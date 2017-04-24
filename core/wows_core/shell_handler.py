from wowspy.wowspy import Wows, Region

from core.discord_functions import get_server_id, build_embed
from core.helpers import comma
from core.wows_core.wg_core import all_time_stats, find_player_id, \
    player_ship_stats, recent_stats
from core.wows_core.wtr_core import wtr_absolute, choose_colour
from core.data_controller import \
    get_shame_list, get_shame, write_shame, remove_shame


def build_shame_embed(region: Region, api: Wows, id_, coefficients, expected,
                      ship_dict):
    """
    Build an embed object of player's stats
    :param region: the player's region
    :param api: the wows api
    :param id_: the player id_
    :param coefficients: from coeff.json provided by warships today
    :param expected: from coeff.json provided by warships today
    :param ship_dict: ship_id: tier
    :return: a discord embed object
    """
    all_time_stats_ = all_time_stats(region, api, id_)
    if all_time_stats_ is not None:
        recent_stats_ = recent_stats(region, api, id_, all_time_stats_)
        nick_name = api.player_personal_data(
            region, id_, language='en', fields='nickname'
        )['data'][str(id_)]['nickname']
        battles = all_time_stats_['battles']
        ship_stats = player_ship_stats(region, api, id_)
        main_hits = all_time_stats_['main_battery']['hits']
        main_shots = all_time_stats_['main_battery']['shots']
        second_hits = all_time_stats_['second_battery']['hits']
        second_shots = all_time_stats_['second_battery']['shots']
        torp_hits = all_time_stats_['torpedoes']['hits']
        torp_shots = all_time_stats_['torpedoes']['shots']
        damage_dealt = all_time_stats_['damage_dealt']
        max_damage_dealt = all_time_stats_['max_damage_dealt']
        planes_killed = all_time_stats_['planes_killed']
        wins = all_time_stats_['wins']
        xp = all_time_stats_['xp']
        survived_battles = all_time_stats_['survived_battles']
        ships_spotted = all_time_stats_['ships_spotted']
        warships_killed = all_time_stats_['frags']
        deaths = battles - survived_battles
        wtr = wtr_absolute(expected, coefficients, ship_stats, ship_dict)
        # max_damage_dealt = str(all_time_stats['max_damage_dealt'])
        # max_xp = str(all_time_stats['max_xp'])
        # max_planes_killed = str(all_time_stats['max_planes_killed'])
        colour = choose_colour(wtr)
        author = {
            'name': nick_name
        }
        k_v = []
        if battles > 0:
            win_rate = "{0:.2f}".format((wins / battles) * 100) + "%"
            avg_dmg = int(damage_dealt / battles)
            avg_exp = int(xp / battles)
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
            torp_hitrate = "{0:.2f}".format((torp_hits / torp_shots) * 100) + \
                           "%" if torp_shots > 0 else '0%'
            k_v += [
                ('All Time Stats', comma(battles) + ' Battles', False),
                ('WTR', comma(wtr)),
                ('Win Rate', win_rate),  # 1
                ('Max Damage Dealt', comma(max_damage_dealt)),
                ('Average Damage', comma(avg_dmg)),  # 2
                ('Average Experience', comma(avg_exp)),  # 4
                ('Average Kills', avg_kills),  # 6
                ('Average Plane Kills', avg_plane_kills),  # 7
                ('Average Ships Spotted', avg_spotted),  # 9
                ('Main Battery Hit Rate', main_hitrate),  # 10
                ('Secondary Battery Hit Rate', second_hitrate),  # 11
                ('Torpedo Hit Rate', torp_hitrate),  # 12
                ('Survival Rate', survival_rate),  # 13
                ('Kills/Deaths', kda)  # 14
            ]
            if recent_stats_ is not None:
                recent_battles = recent_stats_['battles']
                recent_actual = {
                    "damage_dealt":
                        recent_stats_['damage_dealt'] / recent_battles,
                    "frags": recent_stats_['frags'] / recent_battles,
                    "wins": recent_stats_['wins'] / recent_battles
                }
                k_v += [
                    ('Recent Stats', str(recent_battles) + ' Battles', False),
                    ('Win Rate',
                     str("{0:.2f}".format(recent_actual['wins'] * 100)) + '%'),
                    ('Average Damage',
                     comma(int(recent_actual['damage_dealt']))),
                    ('Average Kills',
                     str("{0:.2f}".format(recent_actual['frags'])))
                ]
        else:
            k_v += [('Error', 'The player doesn\'t have any battles played')]
        return build_embed(k_v, colour, author=author)
    else:
        return None


def process_shame(api, player_id: int, region: str, coefficients, expected,
                  ship_dict):
    """
    Process a shame request
    :param ship_dict: ship_dict
    :param expected: expected
    :param coefficients: coefficients
    :param api: wows api
    :param player_id: the player id for the player
    :param region: the region for the player
    :return: a discord embed object or warships today signiture
    """
    region = region_converter(region, False)
    res = build_shame_embed(region, api, player_id, coefficients, expected,
                            ship_dict)
    return res


def region_converter(r, is_warships: bool):
    """
    Converts a region string to Region enum
    :param r: the region string
    :param is_warships: if the string is a warships today region
    """
    if not is_warships:
        return {
            'NA': Region.NA,
            'EU': Region.EU,
            'AS': Region.AS,
            'RU': Region.RU
        }[r]
    return {
        'na': Region.NA,
        'eu': Region.EU,
        'asia': Region.AS,
        'ru': Region.RU
    }[r]


def find_player(ctx, cursor, query: str, region: Region, api: Wows):
    """
    Search for a wows player and returns its region and id
    :param ctx: the server context
    :param cursor: the database cursor
    :param query: the search query
    :param region: the wows player region
    :param api: the wows api 
    :return: (Region, id)
    :rtype: tuple
    """
    server_id = int(get_server_id(ctx))
    search = False
    query_id = None
    if query.startswith('<@!'):
        query_id = int(query[3:-1])
        search = True
    elif query.startswith('<@'):
        query_id = int(query[2:-1])
        search = True
    if search and server_id is not None:
        r, i = get_shame(cursor=cursor, server_id=server_id, user_id=query_id)
        if r is None:
            return None, None
        else:
            return region_converter(r, True), i
    else:
        return region, find_player_id(region, api, query)


def generate_shamelist(ctx, cursor):
    """
    Generate shamelist text for a server
    :param ctx: the server context
    :param cursor: the database cursor
    :return: the shame list for displaying
    """
    server_id = int(get_server_id(ctx))
    res = get_shame_list(cursor, server_id)
    return '```{}```'.format(', '.join([ctx.message.server.get_member(
        str(id_)).name for id_ in res])) if res else None


def process_add_shame(ctx, cursor, connection, query, region: str, api: Wows):
    """
    Return a new instance of shamelist object with the new entry added
    :param ctx: the server context
    :param cursor: the databse cursor
    :param connection: the databse connectionn
    :param query: the search query
    :param region: the region of the player
    :param api: the wows api
    :return: new_entry
    :rtype: bool
    """
    server_id = int(get_server_id(ctx))
    region = region_converter(region, False)
    user_id = int(ctx.message.author.id)
    playerid = find_player_id(region, api, query)
    if playerid is None:
        return None
    warships_region = region.value
    if warships_region == 'com':
        warships_region = 'na'
    return write_shame(
        cursor, connection, server_id, user_id, warships_region, playerid)


def process_remove_shame(ctx, cursor, connection):
    """
    Process remove shame event
    :param ctx: the server context
    :param cursor: the databse cursor
    :param connection: the databse connectionn    
    """
    server_id = int(get_server_id(ctx))
    user_id = int(ctx.message.author.id)
    remove_shame(cursor, connection, server_id, user_id)
