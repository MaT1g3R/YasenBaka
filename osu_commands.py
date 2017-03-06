"""Osu commands"""
from osu import get_user
import json
from discord.ext import commands
from math import ceil
from helpers import generate_image_online


class Osu:

    def __init__(self, bot, key):
        self.bot = bot
        self.key = key

    @commands.command(pass_context=True)
    async def osu(self, ctx, *query: str):
        try:
            mode_dict = {
                '--osu': 0,
                '--Taiko': 1,
                '--CTB': 2,
                '--mania': 3
            }
            mode = 0
            if query[-1] in mode_dict:
                mode = mode_dict[query[-1]]
                query = ' '.join(query[:-1])
            else:
                query = ' '.join(query)

            # (0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania)
            res = json.loads(get_user(self.key, query, mode, '', 31))[0]
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
            avatar = 'https://a.ppy.sh/{}'.format(id_)
            profile = 'https://osu.ppy.sh/u/{}'.format(id_)
            ss = res['count_rank_ss']
            s = res['count_rank_s']
            a = res['count_rank_a']

            out = '**{}\'s profile information**\n'.format(name) + \
                  'Username: {} (ID: {})\n'.format(name, id_) + \
                  'Plays: {} (SS: {} | S: {} | A: {})\n'.format(playcount, ss, s, a) + \
                  'Scoring: (50: {} | 100: {} | 300: {})\n'.format(count50, count100, count300) +\
                  'Total score: {} ({}% ranked)\n'.format(total, int(int(ranked)/int(total))*100) + \
                  'PP: {}pp\n'.format(pp) + \
                  'Rank: #{}\n'.format(pp_rank) + \
                  'Country: :flag_{}: (#{})\n'.format(country, c_rank) + \
                  'Accuracy: {}%\n'.format(acc) + \
                  'Profile: {}'.format(profile)
            await self.bot.say(out)
            await self.bot.send_file(ctx.message.channel, generate_image_online(avatar, 'data//osu.jpg'))
        except IndexError:
            await self.bot.say('Player not found!')

