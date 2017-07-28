from discord.ext.commands import Context

from bot import Yasen
from scripts.checks import is_owner


class OnwerOnly:
    __slots__ = ('bot',)

    def __init__(self, bot: Yasen):
        self.bot = bot

    async def __local_check(self, ctx: Context):
        return await is_owner(ctx)
