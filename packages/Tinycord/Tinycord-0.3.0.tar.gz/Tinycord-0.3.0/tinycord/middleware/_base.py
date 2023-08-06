import typing

if typing.TYPE_CHECKING:
    from ..client import Client
    from ..core import Gateway, GatewayDispatch
    
async def event_name(client: "Client", gateway: "Gateway", event: "GatewayDispatch") -> typing.List[typing.Awaitable]:
    """
        |coro|

        Parameters
        ----------
        client : `Client`
            The main client.
        gateway : `Gateway`
            The gateway that dispatched the event.
        event : `GatewayDispatch`
            The event that was dispatched.
    """

def export():
    """ Exports the function. """
    return event_name