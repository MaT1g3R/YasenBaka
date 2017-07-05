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
        raise e or ex
