import random


def generate_dice_rolls(s: str):
    """
    Generate dice rolls based on input string
    :param s: the input string
    :return: a list of dice rolls
    """
    try:
        rolls, limit = map(int, s.split('d'))
        return ', '.join(str(random.randint(1, limit)) for _ in range(rolls))
    except ValueError:
        return 'Format has to be in NdN!'


def event_probability(prob: str, tries: int):
    """
    Return the probability of something happeneing in x number of tries
    :param prob: the probability of the event happeneing
    :param tries: the number of tries
    :return: the probability of the event happeneing
    """
    try:
        prob = float(prob.replace('%', '')) / 100 if '%' in prob else float(
            prob)
        return round((1 - (1 - prob) ** tries), 4)
    except ValueError:
        return


def random_kanna(kanna_files: list, kanna_resp) -> tuple:
    """
    Returns a tuple of kanna picture and if it's a file.
    :param kanna_resp: the json response from safebooru.
    :param kanna_files: list of local kanna files.
    :return: (kanna, is_file)
    """
    kanna_urls = [('https://safebooru.org//'
                   'images/{}/{}').format(d['directory'], d['image'])
                  for d in kanna_resp] if isinstance(kanna_resp, list) else []
    kanna_total = kanna_urls + kanna_files
    res = random.choice(kanna_total)
    return res, res in kanna_files


def cspost_meme():
    """
    Cspost memes
    :return: a random cspost meme
    """
    lmao = [
        "It's a definite maybe.",
        "83%",
        "You need to get an 80+ in advanced algorithms.. "
        "I heard it's pretty hard.",
        "70% is the bare minimum.",
        "No, you're gonna fail.",
        "25% of the time, you get in 100% of the time.",
        "It’s 50/50, you either get in, or you don’t."
    ]
    return random.choice(lmao)


def place_url(is_clean: bool):
    """
    Return place url based on is_clean bool
    :param is_clean: state if it's the clean version or not
    :return: place url
    """
    return 'https://i.imgur.com/7E3bAnE.png' if is_clean \
        else 'https://i.imgur.com/ajWiAYi.png'
