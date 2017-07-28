class AbstractSource:
    """
    An abstract class for an audio source.
    """
    __slots__ = ('__detail', '__get_detail')

    def __init__(self, __get_detail: callable):
        self.__detail = None
        self.__get_detail = __get_detail

    def __str__(self):
        raise NotImplementedError

    def clean_up(self):
        raise NotImplementedError

    @property
    def detail(self):
        if not self.__detail:
            self.__detail = self.__get_detail()
            del self.__get_detail
        return self.__detail

    async def true_name(self) -> str:
        """
        :return: Name used by `FFmpegPCMAudio`
        """
        raise NotImplementedError
