from core.discord_functions import get_server_id, build_embed
from wowspy.wowspy import Wows, Region
from core.wows_core.wg_core import player_stats, find_player_id, \
    player_ship_stats
from core.wows_core.wtr_core import wtr_absolute, choose_colour
from core.helpers import comma


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
    stats = player_stats(region, api, id_)
    if stats is not None:
        all_time_stats, recent_stats = stats
        nick_name = api.player_personal_data(
            region, id_, language='en', fields='nickname'
        )['data'][str(id_)]['nickname']
        battles = all_time_stats['battles']
        ship_stats = player_ship_stats(region, api, id_)
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
            torp_hitrate = "{0:.2f}".format((torp_hits / torp_shots) * 100) +\
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
            if recent_stats is not None and recent_stats['battles'] > 0:
                recent_battles = recent_stats['battles']
                recent_actual = {
                    "damage_dealt":
                        recent_stats['damage_dealt'] / recent_battles,
                    "frags": recent_stats['frags'] / recent_battles,
                    "wins": recent_stats['wins'] / recent_battles
                }
                k_v += [
                    ('Recent Stats', str(recent_battles) + ' Battles', False),
                    ('Win Rate',
                     str("{0:.2f}".format(recent_actual['wins'] * 100)) + '%'),
                    ('Average Damage', str(int(recent_actual['damage_dealt']))),
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


def find_player(ctx, shame_list, query: str, region: Region, api: Wows):
    """
    Search for a wows player and returns its region and id
    :param ctx: the server context
    :param shame_list: the shamelist
    :param query: the search query
    :param region: the wows player region
    :param api: the wows api 
    :return: (Region, id)
    :rtype: tuple
    """
    server_id = get_server_id(ctx)
    if server_id is None:
        return
    query_l = ''
    if query.startswith('<@!'):
        query_l = query[3:-1]
    elif query.startswith('<@'):
        query_l = query[2:-1]
    if server_id in shame_list and query_l in shame_list[server_id]:
        return region_converter(shame_list[server_id][query_l][0], True), \
               shame_list[server_id][query_l][1]
    else:
        return region, find_player_id(region, api, query)


def generate_shamelist(ctx, shame_list):
    """
    Generate shamelist text for a server
    :param ctx: the server context
    :param shame_list: the entire shame list
    :return: the shame list for displaying
    """
    server_id = get_server_id(ctx)
    if server_id in shame_list:
        res = [ctx.message.server.get_member(key).name for key in
               shame_list[server_id]]
        return '```{}```'.format(', '.join(res)) if res else None
    return None


def process_add_shame(ctx, shamelist, query, region: str, api: Wows):
    """
    Return a new instance of shamelist object with the new entry added
    :param ctx: the server context
    :param shamelist: the origional shame list
    :param query: the search query
    :param region: the region of the player
    :param api: the wows api
    :return: (shamelist, new_entry)
    :rtype: tuple
    """
    shamelist = dict(shamelist)
    server_id = str(get_server_id(ctx))
    region = region_converter(region, False)
    user_id = str(ctx.message.author.id)
    playerid = find_player_id(region, api, query)
    if playerid is None:
        return None, None
    warships_region = region.value
    if warships_region == 'com':
        warships_region = 'na'
    if ctx.message.server.id not in shamelist:
        shamelist[server_id] = {}
    new_entry = user_id not in shamelist[server_id]
    shamelist[server_id][user_id] = [warships_region, playerid]
    return shamelist, new_entry


def process_remove_shame(ctx, shamelist):
    """
    Process remove shame event
    :param ctx: the server context
    :param shamelist: the shame list
    :return: a new instance of shame list with the entry removed
    """
    shamelist = dict(shamelist)
    server_id = str(get_server_id(ctx))
    user_id = str(ctx.message.author.id)
    if user_id in shamelist[server_id]:
        shamelist[server_id].pop(user_id, None)
        return shamelist
    return None
