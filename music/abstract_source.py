from discord.ext.commands import Context


class AbstractSource:
    """
    An abstract class for an audio source.
    """
    __slots__ = ()

    def __str__(self):
        raise NotImplementedError

    def __del__(self):
        raise NotImplementedError

    async def play(self, ctx: Context):
        """
        Play the audio source in ctx.
        :param ctx: discord `Context` object
        """
        raise NotImplementedError

    def detail(self) -> str:
        """
        A detailed string representation of the audio source.
        """
        raise NotImplementedError
