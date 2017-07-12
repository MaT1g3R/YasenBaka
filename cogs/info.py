from time import time

from discord import Message
from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen
from core.bot_info_core import get_info_embed
from core.help import cmd_help_embed, general_help, get_doc
from data_manager.data_utils import get_prefix


class BotInfo:
    def __init__(self, bot: Yasen):
        self.bot = bot

    @commands.command()
    async def info(self, ctx: Context):
        """
        Description: "Displays information about the bot."
        Usage: "`{prefix}info`"
        """
        await ctx.send(embed=get_info_embed(self.bot))

    @commands.command()
    async def help(self, ctx: Context, *args):
        """
        Description: "Help command."
        Usage: "`{prefix}help` for a list of all commands,
        `{prefix}help command name` for help for the  specific command."
        """
        prefix = get_prefix(self.bot, ctx.message)
        name = ' '.join(args)
        doc = get_doc(self.bot, name)
        if doc:
            res = cmd_help_embed(
                name, doc, self.bot.user.avatar_url,
                prefix, self.bot.config.colour
            )
        else:
            res = general_help(self.bot, prefix)
        await ctx.send(embed=res)

    @commands.command()
    async def ping(self, ctx: Context):
        """
        Description: "Command to check network ping."
        Usage: "`{prefix}ping`"
        """
        start = time()
        msg: Message = await ctx.send('Loading... :hourglass:')
        end = time()
        diff = end - start
        await msg.edit(content=f':ping_pong: Pong! | {round(diff*1000)}ms')

