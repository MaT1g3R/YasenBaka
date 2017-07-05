from textwrap import wrap

from discord.ext.commands import CommandOnCooldown, Context

from scripts.checks import AdminError, ManageMessageError, \
    ManageRoleError, NsfwError, OwnerError


def command_error_handler(exception):
    """
    A function that handles command errors
    :param exception: the exception raised
    :return: the message to be sent based on the exception type
    """
    checked = (CommandOnCooldown, NsfwError, ManageMessageError,
               ManageRoleError, AdminError, OwnerError)
    if isinstance(exception, checked):
        return str(exception)
    raise exception


def format_command_error(ex: Exception, context: Context) -> tuple:
    """
    Format a command error to display and log.
    :param ex: the exception raised.
    :param context: the context.
    :return: a message to be displayed and logged, and triggered message
    """
    triggered = context.message.content
    four_space = ' ' * 4
    ex_type = type(ex).__name__
    return (f'{four_space}Triggered message: {triggered}\n'
            f'{four_space}Type: {ex_type}\n'
            f'{four_space}Exception: {str(ex)}'), triggered


def format_traceback(tb: str):
    """
    Format a traceback to be able to display in discord.
    :param tb: the traceback.
    :return: the traceback divided up into sections of max 1800 chars.
    """
    res = wrap(tb, 1800, replace_whitespace=False)
    str_out = ['```py\n' + s.replace('`', chr(0x1fef)) + '\n```'
               for s in res]
    return str_out
