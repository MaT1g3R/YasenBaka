from html import unescape

from aiohttp_wrapper import HTTPStatusError, SessionManager


async def search_answer(session_manager: SessionManager,
                        key: str, query: tuple) -> tuple:
    """
    Search Stack Overflow for an answer id of the question.
    :param session_manager: the SessionManager instance.
    :param key: the api key.
    :param query: the search query.
    :return: a tuple of (answer id, question tags)
    """
    url = 'https://api.stackexchange.com/2.2/search/advanced?'
    params = {
        'order': 'desc',
        'sort': 'relevance',
        'q': '%20'.join(query),
        'accepted': 'True',
        'site': 'stackoverflow',
        'filter': '!bA1dTO)NXLak3j',
        'pagesize': '1',
        'key': key
    }
    js = await session_manager.get_json(url, params)
    if not js:
        return None, None
    items = js.get('items')
    if not items:
        return None, None
    return items[0].get('accepted_answer_id', None), items[0].get('tags', None)


async def get_answer(session_manager: SessionManager,
                     key: str, answer_id: int) -> tuple:
    """
    Get the content of an answer by id.
    :param session_manager: the SessionManager instance.
    :param key: the api key.
    :param answer_id: the answer id.
    :return: a tuple of (answer content, title)
    """
    url = f'https://api.stackexchange.com/2.2/answers/{answer_id}?'
    params = {
        'key': key,
        'filter': '!)Q29lpdRHRpfMsqq*yMLc0KQ',
        'site': 'stackoverflow',
    }
    js = await session_manager.get_json(url, params)
    if not js:
        return None, None
    items = js.get('items', None)
    if not items:
        return None, None
    md = items[0].get('body_markdown', None)
    title = items[0].get('title', None)
    if not md:
        return None, None
    return unescape(md), title


async def stackoverflow(session_manager, key, query) -> tuple:
    """
    Search Stack Overflow for an answer.
    :param session_manager: the SessionManager.
    :param key: the api key.
    :param query: the search query.
    :return: a tuple of (answer content, title, tags, success)
    """
    if not query:
        return 'Please enter a search query', None, None, False
    try:
        q_id, tags = await search_answer(session_manager, key, query)
        if q_id is None:
            return 'Sorry, Nothing found.', None, None, False
        answer, title = await get_answer(session_manager, key, q_id)
        return (answer, title, tags, True) if answer else (
            'Sorry, Nothing found.', None, None, False)
    except HTTPStatusError as e:
        return (f'Something went wrong with the Stack Exchange API\n{e}',
                None, None, False)
