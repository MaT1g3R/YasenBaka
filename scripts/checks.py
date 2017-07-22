"""
Checks for commands
"""

from discord import DMChannel, TextChannel
from discord.ext.commands import CommandError, Context, NoPrivateMessage

from scripts.discord_utils import try_get_member

_generic = ':no_entry_sign: Sorry, you need {} premission to use this command.'


class NsfwError(CommandError):
    pass


class ManageRoleError(CommandError):
    pass


class AdminError(CommandError):
    pass


class ManageMessageError(CommandError):
    pass


def is_nsfw(ctx: Context):
    """
    Detiremine if nsfw is enabled for this channel
    :param ctx: the context
    :return: if nsfw is enabled in this channel
    """
    channel = ctx.channel
    if isinstance(channel, DMChannel):
        return True
    if (isinstance(channel, TextChannel) and
            channel.name.lower().startswith('nsfw')):
        return True
    raise NsfwError('NSFW commands must be used in DM or a channel with a '
                    'name that is equal to or starts with `nsfw` '
                    '(case insensitive)')


def has_manage_role(ctx: Context):
    """
    Check if an user has the manage_roles permissions
    :param ctx: the context
    :return: True if the user has the manage_roles permissions
    :rtype: bool
    """
    member = try_get_member(ctx, ManageRoleError)
    if member.guild_permissions.manage_roles:
        return True
    raise ManageRoleError(_generic.format('Manage Roles'))


def is_admin(ctx):
    """
    Check if the user has admin permissions
    :param ctx: the discord context
    :return: True if the user has admin permissions
    """
    member = try_get_member(ctx, AdminError)
    if member.guild_permissions.administrator:
        return True
    raise AdminError(_generic.format('Administrator'))


def has_manage_message(ctx):
    """
    Check if the user has manage message permissions
    :param ctx: the discord context
    :return: True if the user has manage message permissions
    """
    member = try_get_member(ctx, ManageMessageError)
    if member.guild_permissions.manage_messages:
        return True
    raise ManageMessageError(_generic.format('Manage Message'))


def no_pm(ctx):
    """A :func:`.check` that indicates this command must only be used in a
    guild context only. Basically, no private messages are allowed when
    using the command.

    This check raises a special exception, :exc:`.NoPrivateMessage`
    that is derived from :exc:`.CheckFailure`.
    """
    if ctx.guild:
        return True
    raise NoPrivateMessage('This command cannot be used in private messages.')
