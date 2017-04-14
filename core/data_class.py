"""
A data class to hold all the data the bot will use
"""
import time


class Data:
    """
    A data class to hold all the data the bot will use
    """
    def __init__(self, api_keys, kanna_files, lewds, so, help_message,
                 shame_list, na_ships, coefficients, expected,
                 ship_dict, wows_api):
        self.api_keys = api_keys
        self.kanna_files = kanna_files
        self.lewds = lewds
        self.start_time = time.time()
        self.so = so
        self.so.be_inclusive()
        self.help_message = help_message
        self.shame_list = shame_list
        self.na_ships = na_ships
        self.coefficients = coefficients
        self.expected = expected
        self.ship_dict = ship_dict
        self.wows_api = wows_api
