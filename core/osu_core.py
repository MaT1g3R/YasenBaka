from math import ceil
from time import time
from typing import Union

from discord import Embed, File
from osu_sig import Mode, generate

from core.api_consumer import APIConsumer
from data import data_path


async def osu_player(api_consumer: APIConsumer, name: str,
                     mode: Mode = None) -> Union[str, tuple]:
    """
    Generate osu player info.
    :param api_consumer: the APIConsumer instance.
    :param name: the name of the player.
    :param mode: the game mode.
    :return: a tuple of (embed, image file, file path) if success,
    else an error msg.
    """
    js = await api_consumer.osu_player(name, mode)
    if isinstance(js, str):
        return js
    if not js:
        return 'Player not found!'
    res = js[0]
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

    embed = Embed(colour=api_consumer.config.colour)
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

    sig = generate(
        name, api_consumer.config.colour_str, mode, 1,
        xpbar=True, xpbarhex=True, onlineindicator=3
    )
    try:
        path = data_path.joinpath('dumps').joinpath(
            f'osu_player_{name}_{int(time())}.png')
        file = File(str(await api_consumer.session_manager.save_img(sig, path)))
    except Exception as e:
        file = f'Could not generate player signature.\n{e}'
        path = None
    return embed, file, path


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
