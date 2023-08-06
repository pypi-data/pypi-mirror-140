import typing

import dataclasses

if typing.TYPE_CHECKING:
    from ....client import Client

from .activity import Activity
from ....utils import Snowflake
from ..user import User

@dataclasses.dataclass(repr=False)
class Presence:
    def __init__(
        self, client: "Client", **data
    ) -> None:
        self.client = client
        """The main client."""

        self.user = User(
            client, **data.get('user'))
        """The user."""

        self.guild_id: Snowflake = Snowflake(
            data.get('guild_id'))
        """The guild id."""

        self.status: str = data.get('status')
        """The status."""

        self.activities: "Activity" = [
            Activity(client, **activity) for activity in data.get('activities')]
        """The activities."""

        self.client_status: typing.Dict[str, str] = data.get('client_status')
        """The client status."""

    def __repr__(self) -> str:
        return f"<Presence user_id={self.user.id}>"
        """The representation of the presence."""