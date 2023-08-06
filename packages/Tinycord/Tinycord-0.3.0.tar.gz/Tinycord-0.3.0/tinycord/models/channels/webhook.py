import typing
import dataclasses

if typing.TYPE_CHECKING:
    from ...client import Client

from ..user import User
from ..mixins import Hashable
from ...utils import Snowflake

@dataclasses.dataclass(repr=False)
class Webhook(Hashable):
    """
        This is the VoiceChannel it used to represent a voice channel.

        Parameters
        ----------
        client : `Client`
            The main client.
        **data : `typing.Dict`
            The data that is used to create the channel.

        Attributes
        ----------
        id : `Snowflake`
            The ID of the channel.
        type : `str`
            The type of the channel.
        guild_id : `Snowflake`
            The ID of the guild.
        channel_id : `Snowflake`
            The ID of the channel.
        user : `typing.Union[typing.List[Snowflake], None]`
            The user of the channel.
        name : `str`
            The name of the channel.
        avatar : `typing.Union[typing.List[Snowflake], None]`
            The avatar of the channel.
        token : `typing.Union[typing.List[Snowflake], None]`
            The token of the channel.
    """
    
    def __init__(self, client: "Client", **data) -> None:
        self.client = client
        """The client."""

        self.id: int = Snowflake(
            data.get('id'))
        """The ID of the webhook."""

        self.type: int = data.get('type')
        """The type of the webhook."""

        self.guild_id: int = Snowflake(
            data.get('guild_id'))
        """The guild id of the webhook."""

        self.channel_id: int = Snowflake(
            data.get('channel_id'))
        """The channel id of the webhook."""

        self.user: typing.Union[None, 'User'] = (User(client, **data.get('user')) if 
            'user' in data else None)
        """The user of the webhook."""

        self.name: str = data.get('name')
        """The name of the webhook."""

        self.avatar: typing.Union[None, str] = data.get('avatar')
        """The avatar of the webhook."""

        self.token: typing.Union[None, str] = data.get('token')
        """The token of the webhook."""

    async def edit(self, **data) -> "Webhook":
        """
            Edit the webhook.

            Parameters
            ----------
            **data : `typing.Dict`
                The data that is used to edit the webhook.

        """
        return await self.client.api.wehbook_edit_with_token(self.id, self.token, **data)

    async def delete(self) -> None:
        """
            Delete the webhook.
        """
        await self.client.api.webhook_delete_with_token(self.id, self.token)

    async def execute(self, **data) -> None:
        """
            Execute the webhook.

            Parameters
            ----------
            payload : `typing.Dict`
                The payload that is used to execute the webhook.
        """
        await self.client.api.webhook_execute(self.id, self.token, data)