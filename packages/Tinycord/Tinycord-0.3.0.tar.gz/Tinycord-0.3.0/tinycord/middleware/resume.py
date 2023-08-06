import typing

if typing.TYPE_CHECKING:
    from ..client import Client
    from ..core import Gateway, GatewayDispatch
    
async def resume(client: "Client", gateway: "Gateway", event: "GatewayDispatch") -> typing.List[typing.Awaitable]:
    """
        |coro|
        This event called when the shard is resumed

        Parameters
        ----------
        client : `Client`
            The main client.
        gateway : `Gateway`
            The gateway that dispatched the event.
        event : `GatewayDispatch`
            The event that was dispatched.
    """

    gateway.heartbeat_task.cancel()

    gateway.session_id = event.data['session_id']
    gateway.sequence = event.data['sequence']

    return "on_resume", [
        gateway
    ]

def export():
    """ Exports the function. """
    return resume