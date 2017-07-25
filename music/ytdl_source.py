from music.abstract_source import AbstractSource


class YTDLSource(AbstractSource):
    def __init__(self, query):
        pass

    def __str__(self):
        raise NotImplementedError

    async def play(self, ctx):
        raise NotImplementedError

    def detail(self):
        raise NotImplementedError

    def __del__(self):
        raise NotImplementedError
