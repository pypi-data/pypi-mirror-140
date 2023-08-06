import typing

if typing.TYPE_CHECKING:
    from .command_client import CommandClient
    from ...models import All, Role, User

def setup_callback(callback: typing.Callable):
    """
        This function is used to setup a callback.

        Parameters
        ----------
        callback: `typing.Callable`
    """

    callback.is_owner = False
    """ The is_owner of the command. """
    
    callback.is_guild = False
    """ The is_guild of the command. """

    callback.is_dm = False
    """ The is_dm of the command. """

    callback.has_permissions = []
    """ The has_permissions of the command. """

    callback.has_roles = []
    """ The has_roles of the command. """

    callback.check_any = False
    """ The check_any of the command. """

    callback.checks = []
    """ The checks of the command. """

    return callback

def arg_parser(client: "CommandClient", message: str, int_check: bool = False):
    """
        This function is used to parse arguments.
    """

    args = message.split(' ')
    """ The arguments of the message. """

    parsed_args: typing.List[typing.Any] = []
    """ The object of the arguments. """

    channels: typing.List["All"] = []
    """ The channels of the arguments. """

    users: typing.List["User"] = []
    """ The users of the arguments. """

    roles: typing.List["Role"] = []
    """ The roles of the arguments. """

    for arg in args:
        if arg.startswith(('<@', '<@!')):
            user = client.get_user(
                arg[2:-1].replace('!', ''))

            parsed_args.append(user)
            users.append(user)

        elif arg.startswith('<#'):
            channel = client.get_channel(arg[2:-1])

            parsed_args.append(channel)
            channels.append(channel)

        elif arg.startswith('<@&'):
            role = client.get_role(arg[3:-1])

            parsed_args.append(role)
            roles.append(role)
        elif arg.isdigit():
            if int_check:
                parsed_args.append(int(arg))
            else:
                parsed_args.append(arg)

        parsed_args.append(arg)

    return parsed_args, channels, users, roles