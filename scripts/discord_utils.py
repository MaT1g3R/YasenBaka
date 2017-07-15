import re

from discord import Member
from discord.ext.commands import Context
from discord.utils import get


def try_get_member(ctx: Context, ex=None) -> Member:
    """
    Try to get a member from the context.
    :param ctx: the context.
    :param ex: the exception to be raised if member cannot be found.
    :return: the member.
    :raises: ex, see :param ex
    """
    try:
        return get(ctx.guild.members, id=ctx.author.id)
    except Exception as e:
        raise ex or e


def leading_mentions(msg: str) -> tuple:
    """
    Extract all leading mentions from a message.
    :param msg: the message.
    :return: A tuple of (list of ids, the leftover message)
    >>> s = '<@1212> asd <@45642>'
    >>> leading_mentions(s)
    ([1212], 'asd <@45642>')
    >>> s1 = 'asd <@!454545> asd'
    >>> leading_mentions(s1)
    ([], 'asd <@!454545> asd')
    >>> s2 = '<@45><@!245><@8787>dsads<@154545>'
    >>> leading_mentions(s2)
    ([45, 245, 8787], 'dsads<@154545>')
    """
    regex = re.compile('<@!?([0-9]+)>')
    mentions = []
    while msg:
        match = regex.match(msg)
        if not match:
            break
        mentions.append(int(match.groups()[0]))
        msg = msg[match.end():].strip()
    return mentions, msg


def leading_members(ctx: Context, msg: str) -> tuple:
    """
    Get leading mentions as members from a message.
    :param ctx: the discord context.
    :param msg: the message.
    :return: A tuple of (a list of mentioned members, leftover message)
    """
    ids, left = leading_mentions(msg)
    guild = ctx.guild
    return [m for m in (get(guild.members, id=i) for i in set(ids)) if m], left
