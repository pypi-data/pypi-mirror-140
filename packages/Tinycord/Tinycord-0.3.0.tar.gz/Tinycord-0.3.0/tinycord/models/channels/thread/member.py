import typing
import dataclasses

if typing.TYPE_CHECKING:
    from ....client import Client

from ...mixins import Hashable
from ....utils import Snowflake

@dataclasses.dataclass(repr=False)
class ThreadMember(Hashable):
    """
        This is the Thread it used to represent a text channel.

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
        user_id : `Snowflake`
            The ID of the user.
        join_timestamp : `int`
            The join timestamp.
        flags : `typing.List[str]`
            The flags.
    """
    def __init__(self, client: "Client", **data) -> None:
        self.id: int = Snowflake(
            data.get('id'))
        """ The ID of the thread """

        self.user_id: int = Snowflake(
            data.get('user_id'))
        """ The ID of the user """
        
        self.join_timestamp: int = data.get('join_timestamp')
        """ The join timestamp """
        
        self.flags: typing.List[str] = data.get('flags')
        """ The flags """