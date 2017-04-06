"""Osu commands"""
from osu import get_user
import json
from discord.ext import commands
from math import ceil
from osu_sig import generate, Mode
from discord import Embed
from helpers import comma


class Osu:
    def __init__(self, bot, key):
        self.bot = bot
        self.key = key

    @commands.command(pass_context=True)
    async def osu(self, ctx, *query: str):
        try:
            mode_dict = {
                '--osu': Mode.osu,
                '--Taiko': Mode.taiko,
                '--CTB': Mode.ctb,
                '--mania': Mode.mania
            }
            mode = Mode.osu
            if query[-1] in mode_dict:
                mode = mode_dict[query[-1]]
                query = ' '.join(query[:-1])
            else:
                query = ' '.join(query)

            # (0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania)
            res = json.loads(get_user(self.key, query, mode.value, '', 31))[0]
            name = res['username']
            id_ = res['user_id']
            playcount = res['playcount']
            count50 = res['count50']
            count100 = res['count100']
            count300 = res['count300']
            total = res['total_score']
            ranked = res['ranked_score']
            pp = ceil(float(res['pp_raw']))
            pp_rank = res['pp_rank']
            country = res['country'].lower()
            c_rank = res['pp_country_rank']
            acc = "{0:.2f}".format(float(res['accuracy']))
            profile = 'https://osu.ppy.sh/u/{}'.format(id_)
            ss = res['count_rank_ss']
            s = res['count_rank_s']
            a = res['count_rank_a']
            sig = generate(name, '4286f4', mode, 1, xpbar=True,
                           xpbarhex=True, onlineindicator=3)

            res = Embed(colour=0x4286f4)
            res.set_author(name=name)
            res.add_field(name='Plays: {}'.format(comma(playcount)),
                          value='**SS**: {} | **S**: {} | **A**: {}'.format(
                              comma(ss), comma(s), comma(a)), inline=False)
            res.add_field(name='Scoring',
                          value='**50**: {} | **100**: {} | **300**: {}'
                          .format(comma(count50),
                                  comma(count100),
                                  comma(count300)))
            ranked_rate = int(int(ranked) * 100 / int(total))
            res.add_field(name='Total score', value='{} ({}% ranked)'.format(
                comma(total), ranked_rate))
            res.add_field(name='PP', value='{}pp'.format(comma(pp)),
                          inline=False)
            res.add_field(name='Rank', value='#{}'.format(comma(pp_rank)))
            res.add_field(name='Country', value=':flag_{}: (#{})'.format(
                country, comma(c_rank)))
            res.add_field(name='Accuracy', value='{}%'.format(acc))
            res.add_field(name='Profile', value=profile)
            # try:
            res.set_image(url=sig)
            await self.bot.send_message(ctx.message.channel, embed=res)
        except IndexError:
            await self.bot.say('Player not found!')
        except TypeError:
            await self.bot.say(
                'The player do not have any games in that game mode!')
