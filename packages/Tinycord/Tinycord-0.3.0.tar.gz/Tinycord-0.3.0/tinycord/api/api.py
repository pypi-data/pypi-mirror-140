import typing

from tinycord.models.channels.webhook import Webhook

if typing.TYPE_CHECKING:
    from ..client import Client

from .webhook import WebhookAPI
from .channel import ChannelAPI
from .guild import GuildAPI
from .user import UserAPI

class APIClient(ChannelAPI, GuildAPI, UserAPI, WebhookAPI):
    def __init__(self, client: "Client") -> None:
        self.client = client
        """The client."""

        ChannelAPI.__init__(self, client)
        """The channel api."""

        GuildAPI.__init__(self, self.client)
        """The guild apis."""

        UserAPI.__init__(self, self.client)
        """The user api."""

        WebhookAPI.__init__(self, self.client)
        """The webhook api."""