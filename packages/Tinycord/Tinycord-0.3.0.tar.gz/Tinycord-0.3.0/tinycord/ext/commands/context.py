import typing

if typing.TYPE_CHECKING:
    from .command_client import CommandClient
    from ...models import Message, All, Role, User

class Context:
    def __init__(
        self, 
        bot: "CommandClient",
        message: "Message",
        prefix: str,
        command: str,

        mentions: typing.List["User"],
        channels: typing.List["All"],
        roles: typing.List["Role"],
    ):
        self.bot: "CommandClient" = bot
        """The bot of the context."""

        self.message: "Message" = message
        """The message of the context."""

        self.prefix: str = prefix
        """The prefix of the context."""

        self.command: str = command
        """The command of the context."""

        self.mentions: typing.List["User"] = mentions
        """The mentions of the context."""

        self.channels: typing.List["All"] = channels
        """The channels of the context."""

        self.roles: typing.List["Role"] = roles
        """The roles of the context."""

    @property
    def user(self):
        """The user of the message."""

        return self.message.user

    @property
    def author(self):
        """The author of the message."""
            
        return self.message.author

    @property
    def channel(self):
        """The channel of the message."""
            
        return self.message.channel

    @property
    def guild(self):
        """The guild of the message."""

        return self.message.guild

    @property
    def content(self):
        """The content of the message."""

        return self.message.content

    @property
    def first_mention(self):
        """The first mention of the message."""

        return self.mentions[0] if self.mentions else None

    @property
    def last_mention(self):
        """The last mention of the message."""

        return self.mentions[-1] if self.mentions else None

    @property
    def first_channel(self):
        """The first channel of the message."""

        return self.channels[0] if self.channels else None

    @property
    def last_channel(self):
        """The last channel of the message."""

        return self.channels[-1] if self.channels else None

    @property
    def first_role(self):
        """The first role of the message."""

        return self.roles[0] if self.roles else None

    @property
    def last_role(self):
        """The last role of the message."""

        return self.roles[-1] if self.roles else None

    async def send(self, content: str, **kwargs):
        """
            This function is used to send a message.
            It will replace the ctx.message.channel.send and make it easier to use.

            Parameters
            ----------
            content: `str`
                The content of the message.
            kwargs: `typing.Any`
                The keyword arguments of the message.
        """

        return await self.message.channel.send(content, **kwargs)