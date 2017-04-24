"""
A data class to hold all the data the bot will use
"""
import time


class Data:
    """
    A data class to hold all the data the bot will use
    """

    def __init__(self, api_keys, kanna_files, so,
                 coefficients, expected,
                 ship_dict, wows_api, avatar, danbooru):
        self.api_keys = api_keys
        self.kanna_files = kanna_files
        self.lewds = [
            'https://gfycat.com/JadedBriskGalapagosmockingbird',
            'https://gfycat.com/HonorableDampGrasshopper',
            'https://gfycat.com/VillainousGlaringGazelle',
            'https://gfycat.com/AnguishedSerpentineGar',
            'http://i.imgur.com/KEU40LM.gif',
            'http://i.imgur.com/u0nZuHR.png',
            'http://i.imgur.com/kvxFxGn.png',
            'http://i.imgur.com/aNkOKIl.gif',
            'http://i.imgur.com/9tkf5mY.gif',
            'https://i.imgur.com/8Noy9TH.png',
            'https://cdn.discordapp.com/attachments/'
            '99545692908818432/293912399826780160/FLdfhYU.png',
            '( ͡° ͜ʖ ͡°)'
        ]
        self.start_time = time.time()
        self.so = so
        self.so.be_inclusive()
        self.coefficients = coefficients
        self.expected = expected
        self.ship_dict = ship_dict
        self.wows_api = wows_api
        self.avatar = avatar
        self.danbooru = danbooru
