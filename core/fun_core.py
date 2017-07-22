from random import randint


def generate_dice_rolls(s: str):
    """
    Generate dice rolls based on input string
    :param s: the input string
    :return: a list of dice rolls
    """
    try:
        rolls, limit = [int(s) for s in s.split('d')]
        return (f':game_die: '
                f'{", ".join(str(randint(1, limit)) for _ in range(rolls))}')
    except ValueError:
        return 'Format must to be in NdN!'


def parse_salt(trials: str, prob: str) -> tuple:
    """
    Return the number of trials and the probaility from the user intput
    arguments.
    :param trials: the number of trials
    :param prob: the probability of the event happeneing
    :return: (trials, prob, is_percent) if the numbers are valid
    """
    if trials is None or prob is None:
        return None, None, None
    try:
        n = int(trials)
        if n <= 0:
            return None, None
        if '%' in prob:
            is_percent = True
            prob = prob.replace('%', '')
            p = float(prob) / 100
        else:
            is_percent = False
            p = float(prob)
    except ValueError:
        return None, None, None
    return n, p, is_percent


def parse_repeat(n, msg) -> tuple:
    """
    Parse the argument for the repeat command.
    :param n: the number of times of repeat.
    :param msg: the message to be repeated.
    :return: (number of times of repeat, message to be repeated)
    :raises ValueError:
        if n is not an integre between 1 and 5, or msg is None,
        or len(msg) > 2000.
    """
    try:
        n = int(n)
        if not 1 <= n <= 5:
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError('Please enter a number between 1 and 5.')
    if not msg or len(msg) > 2000:
        raise ValueError('Please enter a message with length less than 2000 '
                         'for me to repeat.')
    return n, msg
