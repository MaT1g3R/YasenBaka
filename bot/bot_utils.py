from discord.ext.commands import BadArgument, CommandOnCooldown, Context, \
    NoPrivateMessage

from scripts.checks import AdminError, ManageMessageError, \
    ManageRoleError, NsfwError, OwnerError


def command_error_handler(exception):
    """
    A function that handles command errors
    :param exception: the exception raised
    :return: the message to be sent based on the exception type
    """
    checked = (CommandOnCooldown, NsfwError, ManageMessageError,
               ManageRoleError, AdminError, OwnerError, NoPrivateMessage,
               BadArgument)
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
