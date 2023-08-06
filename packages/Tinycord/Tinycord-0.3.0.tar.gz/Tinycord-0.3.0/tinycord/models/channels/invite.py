import typing
import dataclasses

if typing.TYPE_CHECKING:
    from ...client import Client

from ...utils import Snowflake
from .stage import StageChannel
from ..user import User

@dataclasses.dataclass(repr=False)
class Invite:
    """
        This is the Invite it used to represent a invite object.

        Parameters
        ----------
        client : `Client`
            The main client.
        **data : `typing.Dict`
            The data that is used to create the channel.

        Attributes
        ----------
        code : `str`
            The code of the invite.
        guild_id : `typing.Union[typing.List[Snowflake], None]`
            The guild id of the invite.
        channel_id : `typing.Union[typing.List[Snowflake], None]`
            The channel id of the invite.
        inviter : `typing.Union[typing.List[Snowflake], None]`
            The inviter of the invite.
        target_type : `typing.Union[typing.List[Snowflake], None]`
            The target type of the invite.
        target_user : `typing.Union[typing.List[Snowflake], None]`
            The target user of the invite.
        target_application : `typing.Union[typing.List[Snowflake], None]`
            The target application of the invite.
        approximate_presence_count : `typing.Union[int, None]`
            The approximate amount of users that the invite is for.
        approximate_member_count : `typing.Union[int, None]`
            The approximate amount of users that the invite is for.
        expires_at : `typing.Union[int, None]`
            The time that the invite expires.
        stage_instance : `typing.Union[str, None]`
            The stage instance that the invite is for.
        guild_scheduled_event : `typing.Union[typing.List[Snowflake], None]`
            The guild scheduled event that the invite is for.
    """
    def __init__(self, client: "Client", **data) -> None:
        self.code: str = data.get('code')
        """The invite code."""
        
        self.guild_id: typing.Union[Snowflake, None] = data.get('guild', {'id': None})['id']
        """The guild that the invite is for."""

        self.channel: typing.Union[Snowflake, None] = data.get('channel', {'id': None})['id']
        """The channel that the invite is for."""

        self.inviter: typing.Union[Snowflake, None] = User(client, **data.get('inviter')) if data.get('inviter') else None
        """The user that created the invite."""
        
        self.target_type: typing.Union[str, None] = data.get('target_type', None)
        """The type of the channel that the invite is for."""
        
        self.target_user: typing.Union[Snowflake, None] = User(client, **data.get('target_user')) if data.get('target_user') else None
        """The user that the invite is for."""

        self.target_application: typing.Union[Snowflake, None] = data.get('target_application', None)
        """The application that the invite is for."""

        self.approximate_presence_count: typing.Union[int, None] = data.get('approximate_presence_count', None)
        """The approximate amount of users that the invite is for."""

        self.approximate_member_count: typing.Union[int, None] = data.get('approximate_member_count', None)
        """The approximate amount of users that the invite is for."""
        
        self.expires_at: typing.Union[int, None] = data.get('expires_at', None)
        """The time that the invite expires."""

        self.stage_instance: typing.Union[str, None] = StageChannel(client, None , **data.get('channel')) if data.get('channel') else None
        """The stage instance that the invite is for."""

        self.guild_scheduled_event = data.get('guild_scheduled_event', None)
        """The guild scheduled event that the invite is for."""


        