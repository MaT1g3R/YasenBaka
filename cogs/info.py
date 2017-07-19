from time import time

from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen
from core.help import cmd_help_embed, general_help, get_doc
from core.info_core import get_info_embed
from data_manager.data_utils import get_prefix
from scripts.checks import is_admin

class BotInfo:
    def __init__(self, bot: Yasen):
        self.bot = bot

    @commands.command()
    async def info(self, ctx: Context):
        """
        Description: Displays information about the bot.
        Usage: "`{prefix}info`"
        """
        await ctx.send(embed=get_info_embed(self.bot))

    @commands.command()
    async def help(self, ctx: Context, *args):
        """
        Description: Help command.
        Usage: "`{prefix}help` for a list of all commands,
        `{prefix}help command name` for help for the  specific command."
        """
        prefix = get_prefix(self.bot, ctx.message)
        name = ' '.join(args)
        doc = get_doc(self.bot, name)
        if doc:
            res = cmd_help_embed(
                name, doc, self.bot.user.avatar_url,
                prefix, self.bot.config.colour, self.bot.logger
            )
        else:
            res = general_help(self.bot, prefix)
        await ctx.send(embed=res)

    @commands.command()
    async def ping(self, ctx: Context):
        """
        Description: Check network ping.
        Usage: "`{prefix}ping`"
        """
        start = time()
        msg = await ctx.send('Loading... :hourglass:')
        end = time()
        diff = end - start
        await msg.edit(content=f':ping_pong: Pong! | {round(diff*1000)}ms')

    @commands.group()
    async def prefix(self, ctx: Context):
        """
        Description: Command to check prefix.
        Usage: |
            `{prefix}prefix` to check the prefix.
            `{prefix}prefix set` to set the prefix for the current guild.
            `{prefix}prefix reset` to reset the prefix for the current guild.
        """
        if ctx.invoked_subcommand:
            return
        prefix = get_prefix(self.bot, ctx.message)
        if ctx.guild:
            await ctx.send(
                f'The prefix for this guild is `{prefix}`\n'
                f'`{prefix}prefix set` to set the prefix for this guild.\n'
                f'`{prefix}prefix reset` to reset the prefix for this guild. '
                f'({self.bot.default_prefix})'
            )
        else:
            await ctx.send(f'The prefix for this bot is {prefix}')

    def __set_prefix(self, guild_id, old_prefix, new_prefix):
        """
        Method to set prefix for a given guild.
        :param guild_id: the guild id.
        :param old_prefix: the old guild prefix.
        :param new_prefix: the new prefix.
        :return: the message to send to the guild.
        """
        if not new_prefix:
            return 'Please enter a vaild prefix.'
        if '/' in new_prefix \
                or '\\' in new_prefix \
                or '#' in new_prefix \
                or '@' in new_prefix:
            return (f'Your prefix contains illegal characters. '
                    f'Please consult {old_prefix}help prefix set')
        self.bot.data_manager.set_prefix(guild_id, new_prefix)
        return f'The prefix for this guild has been set to `{new_prefix}`'

    @prefix.command()
    @commands.guild_only()
    @commands.check(is_admin)
    async def set(self, ctx, prefix: str = None):
        """
        Description: Set the prefix for this guild.
        Restrictions: |
            Cannot be used in private message.
            Prefix may not contain \, /, @, #, or mentions.
        Permission Required: Administrator
        Usage: "`{prefix}prefix set YOUR_PREFIX`"
        """
        old_prefix = get_prefix(self.bot, ctx.message)
        await ctx.send(self.__set_prefix(ctx.guild.id, old_prefix, prefix))

    @prefix.command()
    @commands.guild_only()
    @commands.check(is_admin)
    async def reset(self, ctx):
        """
        Description: Reset the prefix for this guild to default.
        Restrictions: Cannot be used in private message.
        Permission Required: Administrator
        Usage: "`{prefix}prefix reset`"
        """
        old_prefix = get_prefix(self.bot, ctx.message)
        await ctx.send(
            self.__set_prefix(ctx.guild.id, old_prefix, self.bot.default_prefix)
        )
