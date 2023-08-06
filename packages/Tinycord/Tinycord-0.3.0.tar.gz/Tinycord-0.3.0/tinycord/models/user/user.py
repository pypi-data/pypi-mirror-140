import typing
import dataclasses

if typing.TYPE_CHECKING:
    from ...client import Client
    from .presence import Presence

from ..mixins import Hashable
from ...utils import Snowflake

@dataclasses.dataclass(repr=False)
class User(Hashable):
    """
        This is the User it used to represent a user.

        Parameters
        ----------
        client : `Client`
            The main client.
        **data : `typing.Dict`
            The data that is used to create the user.
            
        Attributes
        ----------
        client : `Client`
            The main client.
        id : `Snowflake`
            The ID of the user.
        username : `str`
            The username of the user.
        discriminator : `str`
            The discriminator of the user.
        avatar : `str`
            The avatar of the user.
        banner : `str`
            The banner of the user.
        bot : `bool`
            Whether the user is a bot or not.
        system : `bool`
            Whether the user is a system user or not.
        locale : `str`
            The locale of the user.
        mfa_enabled : `bool`
            Whether the user has MFA enabled or not.
        verified : `bool`
            Whether the user is verified or not.
        premium_type : `int`
            The premium type of the user.
        public_flags : `int`
            The public flags of the user.
    """
    def __init__(self, client: "Client", **data) -> None:
        self.client = client
        """The main client."""

        self.id: Snowflake = Snowflake(
            data.get('id'))
        """The ID of the user."""

        self.username: str = data.get('username')
        """The username of the user."""

        self.discriminator: str = data.get('discriminator')
        """The discriminator of the user."""

        self.avatar: typing.Union[str,None] = data.get('avatar')
        """The avatar of the user."""

        self.banner: typing.Union[str,None] = data.get('banner')
        """The banner of the user."""

        self.bot: bool = data.get('bot', False)
        """Whether the user is a bot or not."""

        self.system: bool = data.get('system', False)
        """Whether the user is a system user or not."""

        self.locale: typing.Union[str,None] = data.get('locale')
        """The locale of the user."""

        self.mfa_enabled: bool = data.get('mfa_enabled', False)
        """Whether the user has MFA enabled or not."""

        self.verified: bool = data.get('verified', False)
        """Whether the user is verified or not."""

        self.premium_type: typing.Union[int,None] = data.get('premium_type', None)
        """The premium type of the user."""

        self.public_flags: typing.Union[int,None] = data.get('public_flags', None)
        """The public flags of the user."""
        
        self.presence: typing.Union["Presence", None] = Presence(
            self.client, data.get('presence')) if data.get('presence') else None
        """The presence of the user."""

        self.clinet_status: typing.Union[str, None] = None
        """The client status of the user."""

    @property
    def icon_url(self) -> typing.Union[str, None]:
        """The icon URL of the User."""

        return (
            f'https://cdn.discordapp.com/icons/{self.id}/{self.icon}.png' if not self.icon.startswith('a_') else 
                f'https://cdn.discordapp.com/icons/{self.id}/{self.icon}.gif')

    @property
    def banner_url(self) -> typing.Union[None, str]:
        """
        The banner URL of the User.

        """

        return (
            f'https://cdn.discordapp.com/banners/{self.id}/{self.banner}.jpg' if not self.banner.startswith('a_') else 
                f'https://cdn.discordapp.com/banners/{self.id}/{self.banner}.gif')