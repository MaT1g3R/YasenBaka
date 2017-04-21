from discord.embeds import Embed


def get_server_id(ctx):
    """
    Get the server id of a context
    :param ctx: the context
    :type ctx: context
    :return: the server id
    :rtype: str
    """
    try:
        return ctx.message.server.id
    except AttributeError:
        return None


def build_embed(k_v_pairs: list, colour, **kwargs):
    """
    Build a discord embed object 
    :param k_v_pairs: list of key value pairs for the content of the embed
    :param colour: the colour of the embed
    :param kwargs: extra options
    :return: a discord embed object
    """
    res = Embed(colour=colour)
    if 'author' in kwargs:
        author = kwargs['author']
        name = author['name'] if 'name' in author else None
        url = author['icon_url'] if 'icon_url' in author else None
        if url is not None:
            res.set_author(name=name, icon_url=url)
        else:
            res.set_author(name=name)
    for t in k_v_pairs:
        k = t[0]
        v = t[1]
        inline = len(t) != 3 or t[2]
        res.add_field(name=k, value=v, inline=inline)
    if 'footer' in kwargs:
        res.set_footer(text=kwargs['footer'])
    return res


async def message_sender(bot, channel, msg):
    """
    A helper function to send a message 
    :param bot: the bot
    :param channel: the channel to send the messsage to
    :param msg: the message to send
    """
    await bot.send_message(channel, msg)
