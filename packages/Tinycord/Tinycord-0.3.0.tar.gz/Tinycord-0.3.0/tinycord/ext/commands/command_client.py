# 2022/2/27
import asyncio
import typing

from ...client import Client
from ...intents import Intents
from .utils import arg_parser
from .exceptions import CommandNotFound, CommandError
from .context import Context
from .base import CommandBase

if typing.TYPE_CHECKING:
    from ...models import Message
    from .plugin import CommandPlugin

class CommandClient(Client, CommandBase):
    """
        This Client are for command client is kinda like TCommand but inside a single client.
    """
    def __init__(
        self,
        token: str,
        *,
        prefix: typing.Union[str, typing.Awaitable] = 'tinycord!',
        bot: bool = True,
        intents: typing.List[Intents],
        reconnect: bool = True,
        disabled_events: typing.List[str] = [],

        ws_options: typing.Dict[str, typing.Any] = {},
        http_options: typing.Dict[str, typing.Any] = {},

        loop: asyncio.AbstractEventLoop = None,
    ):

        self.prefix: str = prefix
        """ The prefix that is used to trigger the command. """

        super().__init__(  
            token,
            bot=bot,
            intents=intents,
            reconnect=reconnect,
            disabled_events=disabled_events,
            ws_options=ws_options,
            http_options=http_options,
            loop=loop,
        )

    def get_prefix(self, message: str):
        """
            This function is used to get the prefix of the message.

            Parameters
            ----------
            message: `str`
                The message that is used to get the prefix.
        """
            
        if callable(self.prefix):
            return self.prefix(self, message)

        return self.prefix

    def process_args(self, message: str):
        """
            This function is used to process the arguments of the message.
        """

        parsed_args, channels, users, roles = arg_parser(self, message)
        """ The arguments of the message. """
        
        return parsed_args, channels, users, roles

    async def process_command(self, message: "Message"):
        """
            This function is used to process the command of the message.

            Parameters
            ----------
            message: `tinycord.Message`
                The message that is used to process the command.
        """
        
        prefix = self.get_prefix(message.content)
        """ The prefix of the message. """

        if not message.content.startswith(prefix):
            return

        parsed_args, channels, users, roles = self.process_args(message.content)
        """ The arguments of the message. """

        command = message.content[len(prefix):].split(' ')[0].lower()
        """ The command of the message. """

        ctx: "Context" = Context(
            self, 
            message, 
            prefix, 
            command,

            users,
            channels,
            roles,
        )
        """ The context of the message. """

        if command not in self.commands:
            await self.dispatch('command_not_found', CommandNotFound(
                command, 'The command was not found.'))

            return

        await self.dispatch('command_dispatch', ctx, parsed_args)
        """ The event that is called when a command dispatch. """

        callback = self.get_command(command).get('callback')

        try:
            await callback(ctx, parsed_args)
        except Exception as e:
            await self.dispatch('command_error', ctx, CommandError(command=command, error=e))

    def add_plugin(self, plugin: "CommandPlugin") -> None:
        """
            This function is used to add a plugin to the client.
        """
        return super().add_plugin(plugin)

    def remove_plugin(self, plugin: "CommandPlugin") -> None:
        """
            This function is used to remove a plugin from the client.
        """
        for command in plugin.commands:
            self.remove_command(command)

        return super().remove_plugin(plugin)