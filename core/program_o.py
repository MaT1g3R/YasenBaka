from json import loads

from requests import get


def chat_response(message: str, convo_id: str):
    message = message.replace(' ', '%20')
    url = 'http://api.program-o.com/v2/chatbot/?bot_id=6&say={}' \
          '&convo_id={}&format=json'.format(message, convo_id)
    try:
        return loads(get(url).content)['botsay']
    except:
        return 'Oh no! Something went wrong with the Program O api! Please ' \
               'contact my creator or await a fix.'
