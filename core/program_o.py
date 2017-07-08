from bot import HTTPStatusError, SessionManager


async def chat_resp(msg: str, convo_id: str, session_manager: SessionManager):
    """
    Get api response from Program O api.
    :param msg: the message to send.
    :param convo_id: the conversation id.
    :param session_manager: the session manager.
    :return: the api response string.
    """
    msg = msg.replace(' ', '%20')
    url = 'http://api.program-o.com/v2/chatbot/?'
    params = {
        'bot_id': '6',
        'say': msg,
        'convo_id': convo_id,
        'format': 'json'
    }
    try:
        js = await session_manager.get_json(url, params)
    except HTTPStatusError as e:
        return f'Sorry, something went wrong with the Program O api.\n{e}'
    else:
        return js['botsay']
