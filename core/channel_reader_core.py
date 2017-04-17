from core.helpers import clense_prefix


def check_message(bot, message, expected):
    """
    A helper method to check if a message's content matches with expected 
    result and the author isn't the bot.
    :param bot: the bot
    :param message: the message to be checked
    :param expected: the expected result
    :return: true if the message's content equals the expected result and 
    the author isn't the bot
    """
    return \
        message.content == expected and \
        message.author.id != bot.user.id and \
        not message.author.bot


def check_message_startwith(bot, message, expected):
    """
    A helper method to check if a message's content start with expected 
    result and the author isn't the bot.
    :param bot: the bot
    :param message: the message to be checked
    :param expected: the expected result
    :return: true if the message's content equals the expected result and 
    the author isn't the bot
    """
    return \
        message.content.startswith(expected) and \
        message.author.id != bot.user.id and \
        not message.author.bot


def clean_message(message, prefix):
    """
    Clean a message mentioning the bot
    :param message: the raw message 
    :param prefix: the message without the mention
    :return: cleaned message
    """
    res = clense_prefix(message.content, prefix)
    while res.startswith(' '):
        res = res[1:]
    return res


def linux_meme(text: str):
    """
    I'd just like to interject for a moment.
    :param text: the text to be checked
    :return: if the text needs a linux meme
    """
    return 'linux' in text.lower() and 'gnu' not in text.lower()


def interject():
    a = "\"I'd just like to interject for a moment. What you're referring " \
        "to as Linux, is in fact, GNU/Linux, or as I've recently taken to " \
        "calling it, GNU plus Linux. Linux is not an operating system " \
        "unto itself, but rather another free component of a fully " \
        "functioning GNU system made useful by the GNU corelibs, " \
        "shell utilities and vital system components comprising a " \
        "full OS as defined by POSIX."

    b = "Many computer users run a modified version of the GNU system every " \
        "day, without realizing it. Through a peculiar turn of events, " \
        "the version of GNU which is widely used today is often called Linux" \
        ", and many of its users are not aware that it is basically the " \
        "GNU system, developed by the GNU Project."

    c = "There really is a Linux, and these people are using it, but it is " \
        "just a part of the system they use. Linux is the kernel: the " \
        "program in the system that allocates the machine's resources to the " \
        "other programs that you run. The kernel is an essential part of an " \
        "operating system, but useless by itself; it can only function in " \
        "the context of a complete operating system. Linux is normally used " \
        "in combination with the GNU operating system: the whole system is " \
        "basically GNU with Linux added, or GNU/Linux. All the so-called " \
        "Linux distributions are really distributions of GNU/Linux.\""

    return '{}\n\n{}\n\n{}'.format(a, b, c)
