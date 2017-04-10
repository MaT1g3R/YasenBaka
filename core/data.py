"""
A data class to hold all the data the bot will use
"""
import time


class Data:
    """
    A data class to hold all the data the bot will use
    """
    def __init__(self, kanna_files, lewds, so, help_message, shame_list,
                 sheet_data, coefficients, expected, ship_dict, ship_list):
        self.kanna_files = kanna_files
        self.lewds = lewds
        self.start_time = time.time()
        self.so = so
        self.help_message = help_message
        self.shame_list = shame_list
        self.sheet_data = sheet_data
        self.coefficients = coefficients
        self.expected = expected
        self.ship_dict = ship_dict
        self.ship_list = ship_list
