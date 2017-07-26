from asyncio import sleep

from discord.ext.commands import Context


class AbstractSource:
    """
    An abstract class for an audio source.
    === Attributes ===
    :type detail: str
        A detailed description of the audio source.
    """
    __slots__ = ('__source', 'title', 'detail')

    def __init__(self, source, title: str, detail: str):
        self.__source = source
        self.detail = detail
        self.title = title

    def __str__(self):
        return self.title

    def __del__(self):
        del self.__source
        del self.detail
        del self.title

    async def play(self, ctx: Context):
        """
        Play the audio source in ctx.
        :param ctx: discord `Context` object
        """
        vc = ctx.voice_client
        if not vc:
            return
        vc.play(
            self.__source,
            after=lambda e: ctx.bot.logger.warn(str(e))
        )
        while True:
            if not vc.is_playing():
                return
            await sleep(5)
