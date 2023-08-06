import typing

import dataclasses

if typing.TYPE_CHECKING:
    from ....client import Client

from ....utils import Snowflake

@dataclasses.dataclass(repr=False)
class Activity:
    def __init__(
        self, client: "Client", **data
    ) -> None:
        self.client = client
        """The main client."""

        self.name: str = data.get('name')
        """The name of the activity."""

        self.type: int = data.get('type')
        """The type of the activity."""

        self.url: typing.Union[None, str] = data.get('url')
        """The url of the activity."""

        self.timestamps: typing.Dict[str, int] = data.get('timestamps')
        """The timestamps of the activity."""

        self.application_id: "Snowflake" = Snowflake(
            data.get('application_id', None))
        """The application id of the activity."""

        self.details: typing.Union[None, str] = data.get('details')
        """The details of the activity."""

        self.state: typing.Union[None, str] = data.get('state')
        """The state of the activity."""

        self.emoji = data.get('emoji')
        """The emoji of the activity."""

        self.party: typing.Union[None, typing.Dict[str, str]] = data.get('party')
        """The party of the activity."""

        self.assets: typing.Union[None, typing.Dict[str, str]] = data.get('assets')
        """The assets of the activity."""

        self.secrets: typing.Union[None, typing.Dict[str, str]] = data.get('secrets')
        """The secrets of the activity."""

        self.instance: bool = data.get('instance')
        """The instance of the activity."""

        self.flags: int = data.get('flags')
        """The flags of the activity."""
        
        self.buttons: typing.List[typing.Dict[str, str]] = data.get('buttons')
        """The buttons of the activity."""

    def __repr__(self) -> str:
        return f"<Activity type={self.type}>"
        """The representation of the activity."""