from typing import Union

from discord import File

from bot import HTTPStatusError, SessionManager
from config import Config


class APIConsumer:
    """
    Class to consume various web APIs.
    """
    __slots__ = ['session_manager', 'config', 'sorry', 'urls', 'headers']

    def __init__(self, session_manager: SessionManager, config: Config):
        """
        Initialize the instance of this class.
        :param session_manager: the session manager.
        :param config: the config class.
        """
        self.session_manager = session_manager
        self.config = config
        self.sorry = 'Sorry, nothing found.'
        self.urls = {
            'program_o': 'http://api.program-o.com/v2/chatbot/?',
            'wolke_image': 'https://staging-api.ram.moe/images/random?',
            'safebooru': 'https://safebooru.org//index.php?'
        }
        self.headers = {
            'wolke_image': {'Authorization': self.config.wolke_api}
        }

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

    async def program_o(self, msg: str, convo_id):
        """
        Get api response from Program O api.
        :param msg: the message to send.
        :param convo_id: the conversation id.
        :return: the api response string.
        """
        params = {
            'bot_id': '6',
            'say': msg.replace(' ', '%20'),
            'convo_id': str(convo_id),
            'format': 'json'
        }
        js = await self.get_json('Program O', self.urls['program_o'], params)
        if isinstance(js, dict):
            return js.get('botsay', self.sorry)
        return js

    async def wolke_image(self, type_: str) -> Union[str, File]:
        """
        Get a random image by type from wolke api.
        :param type_: the type of the image.
        :return: the url to the image.
        """
        params = {'type': type_}
        js = await self.get_json(
            'Wolke', self.urls['wolke_image'], params,
            headers=self.headers['wolke_image']
        )
        if isinstance(js, dict):
            url = js.get('url', None)
            if not url:
                return self.sorry
            return url
        return js
