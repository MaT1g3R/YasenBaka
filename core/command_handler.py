import discord


def get_prefix(bot, message: discord.Message):
    """
    the the prefix of commands for a channel
    :param bot: the discord bot object
    :param message: the message
    :return: the prefix for the server
    """
    prefix_dict = bot.data.prefix_dict
    default = bot.default_prefix
    if message.server is None:
        return default
    id_ = str(message.server.id)
    return default if id_ not in prefix_dict \
        else prefix_dict[id_]
