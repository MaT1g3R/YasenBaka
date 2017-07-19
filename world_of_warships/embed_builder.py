from discord import Embed

from scripts.helpers import try_divide


def get_shame_embed(embed: Embed, all_time_stats, wtr, nick_name, clan_tag,
                    recent_stats, recent_date, profile_url) -> Embed:
    a = embed.add_field
    embed.set_author(
        name=f'{nick_name} | Clan: {clan_tag} <- Link to profile',
        url=profile_url
    )
    battles = all_time_stats['battles']
    if not battles:
        a(
            name='Error',
            value="The player doesn't have any battles played."
        )
        return embed
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
    # max_xp = str(all_time_stats['max_xp'])
    # max_planes_killed = str(all_time_stats['max_planes_killed'])

    kda = f'{(warships_killed / deaths):.2f}' if deaths else '\u221E'
    a(name='All Time Stats', value=f'{battles:,} Battles', inline=False)
    a(name='WTR', value=f'{wtr:,}')
    a(name='Win Rate', value=f'{((wins / battles) * 100):.2f}%')
    a(name='Max Damage Dealt', value=f'{max_damage_dealt:,}')
    a(name='Average Damage', value=f'{(damage_dealt // battles):,}')
    a(name='Average Experience', value=f'{(xp//battles):,}')
    a(name='Average Kills', value=f'{(warships_killed / battles):.2f}')
    a(
        name='Average Plane Kills',
        value=f'{(planes_killed / battles):.2f}'
    )
    a(
        name='Average Ships Spotted',
        value=f'{(ships_spotted / battles):.2f}'
    )
    a(
        name='Main Battery Hit Rate',
        value=f'{(try_divide(main_hits, main_shots) * 100):.2f}%'
    )
    a(
        name='Secondary Battery Hit Rate',
        value=f'{(try_divide(second_hits, second_shots) * 100):.2f}%'
    )
    a(
        name='Torpedo Hit Rate',
        value=f'{(try_divide(torp_hits, torp_shots) * 100):.2f}%'
    )
    a(
        name='Survival Rate',
        value=f'{((survived_battles / battles) * 100):.2f}%'
    )
    a(name='Kills/Deaths', value=kda)

    if recent_stats:
        recent_battles = recent_stats['battles']
        avg_wins = recent_stats['wins'] / recent_battles
        avg_frags = recent_stats['frags'] / recent_battles
        avg_dmg = recent_stats['damage_dealt'] // recent_battles
        a(
            name=f'Recent Stats (Since {recent_date[:4]}-'
                 f'{recent_date[4:6]}-{recent_date[6:]})',
            value=f'{recent_battles} Battles',
            inline=False
        )

        a(name='Win Rate', value=f'{(avg_wins * 100):.2f}%')
        a(name='Average Damage', value=f'{avg_dmg:,}')
        a(name='Average Kills', value=f'{avg_frags:.2f}')
    del a
    return embed


def build_clan_embed(embed: Embed, total_stats, clan_name, clan_description,
                     clan_wtr, clan_tag, clan_active, clan_creation_date,
                     creator_name, leader_name, members_count) -> Embed:
    embed.set_author(name=clan_name)
    a = embed.add_field
    battles = total_stats['battles']
    if not battles:
        a(
            name='Error',
            value="The clan doesn't have any battles played."
        )
        return embed
    damage_dealt = total_stats['damage_dealt']
    wins = total_stats['wins']
    survived_battles = total_stats['survived_battles']
    torp_shots = total_stats['torpedoes']['shots']
    torp_hits = total_stats['torpedoes']['hits']
    kills = total_stats['frags']
    main_shots = total_stats['main_battery']['shots']
    main_hits = total_stats['main_battery']['hits']
    second_shots = total_stats['second_battery']['shots']
    second_hits = total_stats['second_battery']['hits']
    ships_spotted = total_stats['ships_spotted']
    plane_kills = total_stats['planes_killed']
    xp = total_stats['xp']

    a(name='Tag', value=clan_tag)
    a(name='Description', value=clan_description)
    a(name='Active', value=str(clan_active))
    a(name='Created At', value=clan_creation_date)
    a(name='Creator', value=creator_name)
    a(name='Leader', value=leader_name)
    a(name='Members Count', value=str(members_count))
    a(name='Clan Average Stats', value=f'In total of {battles:,} Battles',
      inline=False)

    if clan_wtr is not None:
        a(name='WTR', value=f'{clan_wtr:,}')
    a(name='Win Rate', value=f'{(100*wins/battles):.2f}%')
    a(name='Average Damage', value=f'{round(damage_dealt/battles):,}')
    a(name='Average Experience', value=f'{round(xp/battles):,}')
    a(name='Average Kills', value=f'{kills/battles:.2f}')
    a(name='Average Plane Kills', value=f'{plane_kills/battles:.2f}')
    a(name='Average Ships Spotted', value=f'{ships_spotted/battles:.2f}')
    a(name='Main Battery Hit Rate', value=f'{100*main_hits/main_shots:.2f}%')
    a(name='Secondary Battery Hit Rate',
      value=f'{100*second_hits/second_shots:.2f}%')
    a(name='Torpedo Hit Rate', value=f'{100*torp_hits/torp_shots:.2f}%')
    a(name='Survival Rate', value=f'{100*survived_battles/battles:.2f}%')
    a(name='Kills/Deaths', value=f'{kills/(battles-survived_battles):.2f}')
    del a
    return embed
