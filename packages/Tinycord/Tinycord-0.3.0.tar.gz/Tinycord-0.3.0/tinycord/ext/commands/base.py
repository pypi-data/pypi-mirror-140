import typing

from .exceptions import CommandNotFound
from .utils import setup_callback

class CommandBase:
    """
        This is the base class of the CommandClient.
    """
    commands: typing.Dict[str, typing.Dict[str, typing.Any]] = {}

    def add_command(self, name: str, description: str, usage: str, callback: typing.Callable):
        """
            This function is used to add a command to the client.

            Parameters
            ----------
            name: `str`
                The name of the command.
            description: `str`
                The description of the command.
            usage: `str` 
                The usage of the command.
            callback: `typing.Callable`
                The callback of the command.
        """

        callback = setup_callback(callback)
        """ The callback of the command. """

        self.commands[name] = {
            'name': name,
            'description': description,
            'usage': usage,
            'callback': callback,
        }
        """ The commands that are available. """

        return self.commands[name]

    def remove_command(self, name: str):
        """
            This function is used to remove a command from the client.

            Parameters
            ----------
            name: `str`
                The name of the command.
        """

        if name in self.commands:
            del self.commands[name]

        raise CommandNotFound(name, 'The command was not found.')

    def get_command(self, name: str):
        """
            This function is used to get the command of the name.
                
            Parameters
            ----------
            name: `str`
                The name of the command.
        """

        if name in self.commands:
            return self.commands[name]

    def command(self, name: str, description: str = None, usage: str = None):
        """
            Decorator for adding a command.

            Parameters
            ----------
            name: `str`
                The name of the command.
            description: `str`
                The description of the command.
            usage: `str`
                The usage of the command.
        """    

        def decorator(callback: typing.Callable):
            """
                This function is used to decorate a callback.
            """

            self.add_command(name, description, usage, callback)

            return callback

        return decorator