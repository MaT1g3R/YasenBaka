"""
Checks for commands
"""

from discord import DMChannel, TextChannel
from discord.ext.commands import CommandError, Context

from scripts.discord_utils import try_get_member

_generic = ':no_entry_sign: Sorry, you need {} premission to use this command.'


class NsfwError(CommandError):
    def __str__(self):
        return ('NSFW commands must be used in DM or a channel with a name '
                'that is equal to or starts with `nsfw` (case insensitive)')


class ManageRoleError(CommandError):
    def __str__(self):
        return _generic.format('Manage Roles')


class AdminError(CommandError):
    def __str__(self):
        return _generic.format('Administrator')


class ManageMessageError(CommandError):
    def __str__(self):
        return _generic.format('Manage Message')


class OwnerError(CommandError):
    def __str__(self):
        return ':no_entry_sign: Only my owner can use this command.'


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
    raise NsfwError


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
    raise ManageRoleError


def is_admin(ctx):
    """
    Check if the user has admin permissions
    :param ctx: the discord context
    :return: True if the user has admin permissions
    """
    member = try_get_member(ctx, AdminError)
    if member.guild_permissions.administrator:
        return True
    raise AdminError


def has_manage_message(ctx):
    """
    Check if the user has manage message permissions
    :param ctx: the discord context
    :return: True if the user has manage message permissions
    """
    member = try_get_member(ctx, ManageMessageError)
    if member.guild_permissions.manage_messages:
        return True
    raise ManageMessageError


def is_owner(ctx: Context):
    """
    :param ctx: the discord context
    :return: True if the user is the bot owner
    """
    if ctx.author.id in ctx.bot.config.owners:
        return True
    raise OwnerError
