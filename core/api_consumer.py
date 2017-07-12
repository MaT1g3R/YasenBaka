from typing import Optional, Union

from discord import File
from osu_sig import Mode

from bot import HTTPStatusError, SessionManager
from config import Config


class APIConsumer:
    """
    Class to consume various web APIs.
    """
    __slots__ = ['session_manager', 'config', 'sorry']

    def __init__(self, session_manager: SessionManager, config: Config):
        """
        Initialize the instance of this class.
        :param session_manager: the session manager.
        :param config: the config class.
        """
        self.session_manager = session_manager
        self.config = config
        self.sorry = 'Sorry, nothing found.'

    async def get_json(self, name, url, params, **kwargs):
        """
        Try to get json resp from url.
        :param name: the name of the api.
        :param url: the url.
        :param params: the parameters.
        :param kwargs: optional kwargs.
        :return: the json response.
        """
        try:
            js = await self.session_manager.get_json(url, params, **kwargs)
            return js
        except HTTPStatusError as e:
            return f'Sorry, something went wrong with the {name} api.\n{e}'

    async def wolke_image(self, type_: str) -> Union[str, File]:
        """
        Get a random image by type from wolke api.
        :param type_: the type of the image.
        :return: the url to the image.
        """
        url = 'https://staging-api.ram.moe/images/random?'
        header = {'Authorization': self.config.wolke_api}
        params = {'type': type_}
        js = await self.get_json(
            'Wolke', url, params,
            headers=header
        )
        if isinstance(js, dict):
            url = js.get('url', None)
            if not url:
                return self.sorry
            return url
        return js

    async def osu_player(self, name: str,
                         mode: Optional[Mode] = Mode.osu) -> Union[str, list]:
        """
        Get a dict of stats of the osu! player.
        :param name: the player name.
        :param mode: the game mode, optional, defaults to Osu!.
        :return: the python dict of the api response.
        """
        url = 'https://osu.ppy.sh/api/get_user?'
        params = {
            'k': self.config.osu,
            'm': mode.value,
            'u': name,
            'event_days': 31,
            'type': 'string'
        }
        return await self.get_json('Osu!', url, params)
