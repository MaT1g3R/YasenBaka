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
    if len(search) > 2:
        return 'You cannot search for more than 2 tags at a time'
    res = api.post_list(tags=' '.join(search), random=True, limit=1)
    base = 'https://danbooru.donmai.us'
    return base+res[0]['large_file_url'] \
        if len(res) > 0 and 'large_file_url' in res[0] \
        else 'Sorry! nothing found'


def sankaku(search):
    """
    Search sankaku for lewds
    :param search: the search term
    :return: lewds
    """
    pass


def gelbooru(search):
    """
    Search gelbooru for lewds
    :param search: the search term 
    :return: lewds
    """
    pass


if __name__ == '__main__':
    danbooru = db()
    # r =danbooru.tag_list(name='ass,haruna_(kantai_collection)')
    # r = danbooru.post_list(tags='ass haruna_(kantai_collection)', random=True, limit=1)[0]['large_file_url']
    # print('https://danbooru.donmai.us'+r)
    # print(r)