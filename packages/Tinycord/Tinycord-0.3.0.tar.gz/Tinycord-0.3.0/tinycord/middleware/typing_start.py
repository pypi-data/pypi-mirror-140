import typing

if typing.TYPE_CHECKING:
    from ..client import Client
    from ..core import Gateway, GatewayDispatch
    
async def typing_start(client: "Client", gateway: "Gateway", event: "GatewayDispatch") -> typing.List[typing.Awaitable]:
    """
        |coro|
        This event called when a user start typing.
        It does prase the data and return the user and the channel.

        Parameters
        ----------
        client : `Client`
            The main client.
        gateway : `Gateway`
            The gateway that dispatched the event.
        event : `GatewayDispatch`
            The event that was dispatched.
    """

    user = client.get_user(event.data["user_id"])
    """ The user that started typing. """

    channel = client.get_channel(event.data["channel_id"])
    """ The channel that the user started typing in. """

    return "on_typing_start", [
        user, channel
    ]

def export():
    """ Exports the function. """
    return typing_start