from discord import File
from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen
from core.osu_core import osu_player, parse_query


class Osu:
    """
    Class of Osu commands.
    """

    def __init__(self, bot: Yasen):
        """
        Init the instance of this class.
        :param bot: the Yasen bot instace.
        """
        self.bot = bot

    @commands.command()
    async def osu(self, ctx: Context, *query):
        """
        Description: "Get an osu! player's data."
        Flags: |
            "You can use a flag to specify the game mode for the data. Default is osu!"
            `--o` osu!
            `--t` Taiko
            `--c` Catch the Beat
            `--m` osu!mania
        Usage: "`{prefix}osu player name --flag` Flag is optional,
        replace **--flag** with a flag listed above if you intend to use it."
        """
        name, mode = parse_query(query)
        res = await osu_player(self.bot.api_consumer, name, mode)
        if isinstance(res, str):
            await ctx.send(res)
            return
        embed, img, path = res
        if isinstance(img, File):
            await ctx.send(embed=embed)
            await ctx.send(file=img)
            path.unlink()
        else:
            await ctx.send(img, embed=embed)
