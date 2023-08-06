import typing

if typing.TYPE_CHECKING:
    from ..client import Client
    from ..core import Gateway, GatewayDispatch

from ..models import Presence
    
async def presence_update(client: "Client", gateway: "Gateway", event: "GatewayDispatch") -> typing.List[typing.Awaitable]:
    """
        |Coro|
        This event called when the user presence update
        It does prase it and provide the Presence model and the user that updated their presence.
    
        Parameters
        ----------
        client : `Client`
            The main client.
        gateway : `Gateway`
            The gateway that dispatched the event.
        event : `GatewayDispatch`
            The event that was dispatched.
    """
    presence = Presence(client, **event.data)
    """ The presence that was updated. """

    user = client.get_user(presence.user.id)
    """ The user that updated their presence. """

    if user is None:
        user = presence.user
        """ The user that updated their presence. """

        client.users[str(user.id)] = user

    user.presence = presence
    """ The presence that was updated. """
    
    user.clinet_status = presence.client_status
    """ The client_status that was updated. """

    return "on_presence_update", [
        user, presence
    ]


def export():
    """ Exports the function. """
    return presence_update