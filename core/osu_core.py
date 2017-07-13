from logging import WARN
from math import ceil
from typing import Union

from discord import Embed, File
from osu_sig import Mode, generate

from bot import HTTPStatusError, SessionManager


async def osu_player(player_data: list, mode: Mode,
                     colour) -> Union[str, Embed]:
    """
    Generate osu player info.
    :param player_data: the player data.
    :param mode: the game mode.
    :param colour: the colour used for the embed.
    :return: A discord embed if success else an error message.
    """
    if not player_data:
        return 'Player not found!'
    res = player_data[0]
    name = res['username']
    id_ = res['user_id']
    playcount = res['playcount']
    count50 = res['count50']
    count100 = res['count100']
    count300 = res['count300']
    total = res['total_score']
    ranked = res['ranked_score']
    try:
        pp = ceil(float(res['pp_raw']))
    except TypeError:
        return 'This player does not have any games played in this mode.'
    pp_rank = res['pp_rank']
    country = res['country'].lower()
    c_rank = res['pp_country_rank']
    acc = "{0:.2f}".format(float(res['accuracy']))
    profile = f'https://osu.ppy.sh/u/{id_}'
    ss = res['count_rank_ss']
    s = res['count_rank_s']
    a = res['count_rank_a']

    embed = Embed(colour=colour)
    mode_str = {
        Mode.osu: 'osu!',
        Mode.taiko: 'Taiko',
        Mode.ctb: 'Catch the Beat',
        Mode.mania: 'osu!mania'
    }[mode]
    embed.set_author(name=f"{name}'s player data | Mode: {mode_str}")
    embed.add_field(
        name=f'Plays: {int(playcount):,}',
        value=f'**SS**: {int(ss):,} | **S**: {int(s):,} | **A**: {int(a):,}',
        inline=False
    )
    embed.add_field(
        name='Scoring',
        value=(f'**50**: {int(count50):,} | **100**: {int(count100):,} '
               f'| **300**: {int(count300):,}'),
    )
    ranked_rate = int(int(ranked) * 100 / int(total))
    embed.add_field(
        name='Total score', value=f'{int(total):,} ({ranked_rate}% ranked)'
    )
    embed.add_field(name='PP', value=f'{int(pp):,}pp', inline=False)
    embed.add_field(name='Rank', value=f'#{int(pp_rank):,}')
    embed.add_field(
        name='Country', value=f':flag_{country}: (#{int(c_rank):,})')
    embed.add_field(name='Accuracy', value=f'{acc}%')
    embed.add_field(name='Profile', value=profile)
    return embed


async def generate_sig(name: str, mode: Mode, colour_str,
                       session_manager: SessionManager) -> Union[str, File]:
    """
    Generate an osu! player signature.
    :param name: the name of the player.
    :param mode: the osu! game mode.
    :param colour_str: the colour used for the signature.
    :param session_manager: the SessionManager instance.
    :return: A discord File object if success, else an error message.
    """
    sig = generate(
        name, colour_str, mode, 1,
        xpbar=True, xpbarhex=True, onlineindicator=3
    )
    try:
        bytes_io = await session_manager.bytes_img(sig)
    except HTTPStatusError as e:
        session_manager.logger.log(WARN, str(e))
        return f'Could not generate player signature.'
    return File(bytes_io, 'osu.png')


async def get_player_resp(session_manager: SessionManager, key: str, name: str,
                          mode: Mode = Mode.osu) -> Union[str, list]:
    """
    Get api response for player from osu api.
    :param session_manager: the SessionManager instance.
    :param key: the api key.
    :param name: the name of the player.
    :param mode: the game mode, defaults to osu!
    :return: the json api response if success else an error message.
    """
    url = 'https://osu.ppy.sh/api/get_user?'
    params = {
        'k': key,
        'm': mode.value,
        'u': name,
        'event_days': 31,
        'type': 'string'
    }
    try:
        return await session_manager.get_json(url, params)
    except HTTPStatusError as e:
        return f'Sorry, something went wrong with the osu! api.\n{e}'


def parse_query(query: tuple) -> tuple:
    """
    Process the search query from user input.
    :param query: the search query
    :return: (name, mode)
    """
    mode_dict = {
        '--o': Mode.osu,
        '--t': Mode.taiko,
        '--c': Mode.ctb,
        '--m': Mode.mania
    }
    if query[-1] in mode_dict:
        mode = mode_dict[query[-1]]
        name = ' '.join(query[:-1])
    else:
        name = ' '.join(query)
        mode = Mode.osu
    return name, mode
