"""Osu commands"""
from discord.ext import commands

from core.osu_core import process_query, osu_embed, PlayerNotFoundError, \
    NoGameError


class Osu:
    def __init__(self, bot):
        self.bot = bot
        self.key = self.bot.data.api_keys['Osu']

    @commands.command(pass_context=True)
    async def osu(self, ctx, *query: str):
        try:
            q, m = process_query(query)
            embed, sig = osu_embed(self.key, q, m)
            await self.bot.send_message(ctx.message.channel, embed=embed)
            await  self.bot.send_file(ctx.message.channel, sig)
        except PlayerNotFoundError:
            await self.bot.say('Player not found!')
        except NoGameError:
            await self.bot.say('The player doesn\'t have any games played in '
                               'that game mode!')
