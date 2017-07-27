from discord import Message


def get_prefix(yasen, message: Message):
    """
    Get command prefix for a message.
    :param yasen: the bot instance.
    :param message: the message.
    :return: the prefix for that message.
    """
    guild = message.guild
    default = yasen.default_prefix
    if not guild:
        return default
    try:
        return yasen.data_manager.get_prefix(str(guild.id)) or default
    except AttributeError:
        return default
