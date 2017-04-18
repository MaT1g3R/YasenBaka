from discord import ChannelType
from pybooru import Danbooru
from temp import db


def is_nsfw(ctx):
    """
    Detiremine if nsfw is enabled for this channel
    :param ctx: the context
    :return: if nsfw is enabled in this channel
    """
    return \
        ctx.message.channel.type == ChannelType.private \
        or ctx.message.channel.name.lower() == 'nsfw'


def danbooru(search, api: Danbooru):
    """
    Search danbooru for lewds
    :param search: the search term
    :param api: the danbooru api object
    :return: the lewd link
    """
    tag_list = api.tag_list()
    api.post_list()
    pass


def sankaku(search):
    pass


def gelbooru(search):
    pass


if __name__ == '__main__':
    danbooru = db()

    res = danbooru.post_list(tags=['k-on!', 'from_behind'])
    print(res)