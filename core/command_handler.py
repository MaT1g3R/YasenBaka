import discord
from core.data_controller import get_prefix as gf


def get_prefix(bot, message: discord.Message):
    """
    the the prefix of commands for a channel
    :param bot: the discord bot object
    :param message: the message
    :return: the prefix for the server
    """
    if message.server is None:
        return bot.default_prefix
    id_ = int(message.server.id)
    res = gf(bot.cursor, id_)
    return res if res is not None else bot.default_prefix
