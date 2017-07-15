from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen
from core.osu_core import generate_sig, get_player_resp, osu_player, parse_query


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
        Description: Get an osu! player's data.
        Flags: |
            You can use a flag to specify the game mode. Default is osu!
            `--o` osu!
            `--t` Taiko
            `--c` Catch the Beat
            `--m` osu!mania
        Usage: "`{prefix}osu player name --flag` Flag is optional,
        replace **--flag** with a flag listed above if you intend to use it."
        """
        name, mode = parse_query(query)
        resp = await get_player_resp(
            self.bot.session_manager, self.bot.config.osu, name, mode
        )
        if isinstance(resp, str):
            await ctx.send(resp)
            return
        embed = await osu_player(resp, mode, self.bot.config.colour)
        if isinstance(embed, str):
            await ctx.send(embed)
            return

        await ctx.send(embed=embed)
        sig = await generate_sig(
            name, mode, self.bot.config.colour_str, self.bot.session_manager)
        if isinstance(sig, str):
            await ctx.send(str)
        else:
            await ctx.send(file=sig)
