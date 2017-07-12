from json import dump, load
from pathlib import Path
from typing import List, Optional


class Config:
    """
    Class to hold bot configs.
    """

    def __init__(self, beta=False):
        """
        Initialize the instance.
        :param beta: True to use the beta_config.json for the config file.
        """
        name = 'beta_config.json' if beta else 'config.json'
        self.path = Path(Path(__file__).parent.joinpath(name))
        with self.path.open() as f:
            self.__content = load(f)

    def __str__(self):
        return self.__content.__str__()

    def __write(self, key: str, val):
        """
        Write self.__content to self.path if the value is different than
        self.__content[key]
        :param key: the key.
        :param val: the value.
        """
        if self.__content[key] != val:
            self.__content[key] = val
            with self.path.open('w') as f:
                dump(self.__content, f)

    @property
    def token(self):
        return self.__content['Discord']

    @property
    def stack_exchange(self):
        return self.__content['StackExchange']

    @property
    def wows(self):
        return self.__content['WoWs']

    @property
    def currency(self):
        return self.__content['Currency']

    @property
    def osu(self):
        return self.__content['Osu']

    @property
    def danbooru(self):
        return self.__content['Danbooru']

    @property
    def botsorgapi(self):
        return self.__content['Botsorgapi']

    @property
    def default_prefix(self):
        return self.__content['default_prefix']

    @default_prefix.setter
    def default_prefix(self, value: str):
        self.__write('default_prefix', value)

    @property
    def console_logging(self):
        return self.__content['enable_console_logging']

    @console_logging.setter
    def console_logging(self, value: bool):
        self.__write('enable_console_logging', value)

    @property
    def error_log(self):
        return self.__content['error_log']

    @error_log.setter
    def error_log(self, value: Optional[int]):
        self.__write('error_log', value)

    @property
    def owners(self) -> List[int]:
        return self.__content['owners']

    @property
    def wolke_api(self):
        return self.__content['wolke_api']

    @property
    def colour(self):
        return int(self.__content['colour'], base=16)

    @property
    def colour_str(self):
        return self.__content['colour']

    @property
    def support(self):
        return self.__content['support']
