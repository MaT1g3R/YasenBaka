from discord import DiscordException, Forbidden, HTTPException
from discord.ext import commands
from discord.ext.commands import Context

from bot import Yasen
from scripts.checks import has_manage_message, is_admin, no_pm
from scripts.discord_utils import leading_members
from scripts.helpers import parse_number


class Moderation:
    """
    Moderation commands.
    """
    __slots__ = ('bot',)

    def __init__(self, bot: Yasen):
        self.bot = bot

    def __local_check(self, ctx: Context):
        return no_pm(ctx)

    @commands.command()
    @commands.check(is_admin)
    async def masspm(self, ctx: Context, *, args: str = None):
        """
        Description: Send pm to all mentioned members.
        Restriction: Cannot be used in private message.
        Permission Required: Administrator
        Usage: "`{prefix}masspm @mention0 @mention1 my message`"
        """
        if not args:
            await ctx.send(
                'Please mention at least one member and include '
                'a message to send.'
            )
            return
        members, msg = leading_members(ctx, args)
        if not members:
            await ctx.send('Please mention at least one member.')
            return
        if not msg:
            await ctx.send('Please enter a message for me to send.')
            return
        sent = []
        failed = []
        for m in members:
            try:
                await m.send(msg)
                sent.append(m.display_name)
            except DiscordException as e:
                self.bot.logger.warn(str(e))
                failed.append(m.display_name)
        success_msg = (f'PM sent to the following members:'
                       f'\n```\n{", ".join(sent)}\n```') if sent else ''
        failed_msg = (f'Failed to send PMs to the following members:'
                      f'\n```\n{", ".join(failed)}\n```') if failed else ''
        if success_msg or failed_msg:
            await ctx.send(f'{success_msg}{failed_msg}')

    @commands.command()
    @commands.check(has_manage_message)
    async def purge(self, ctx: Context, num=None):
        """
        Description: Purge up to 99 messages in the current channel.
        Restriction: |
            Cannot be used in private message.
            Can only purge from 1 to 99 (inclusive) messages at once.
        Permission Required: Manage Messages
        Usage: "`{prefix}purge num` where num is a number between 1 and 99."
        """
        num = parse_number(num, int) or 0
        if not 1 <= num <= 99:
            await ctx.send(
                'Please enter a number between 1 and 99.', delete_after=3
            )
            return
        try:
            deleted = await ctx.channel.purge(limit=num + 1)
        except Forbidden:
            await ctx.send('I do not have the permissions to purge messages.')
        except HTTPException:
            await ctx.send(':no_entry_sign: Purging messages failed.')
        else:
            deleted_num = len(deleted) - 1
            msg_str = (f'{deleted_num} message' if num == 1
                       else f'{deleted_num} messages')
            await ctx.send(f':recycle: Purged {msg_str}.', delete_after=3)
