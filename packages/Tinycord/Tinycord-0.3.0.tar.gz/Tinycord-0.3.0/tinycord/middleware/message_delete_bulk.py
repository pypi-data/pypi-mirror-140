import typing

if typing.TYPE_CHECKING:
    from ..client import Client
    from ..core import Gateway, GatewayDispatch
    
async def message_delete_bulk(client: "Client", gateway: "Gateway", event: "GatewayDispatch") -> typing.List[typing.Awaitable]:
    """
        |coro|
        This event called when a message deleted at once.
        It does provide the ids of the message, channel and the guild

        Parameters
        ----------
        client : `Client`
            The main client.
        gateway : `Gateway`
            The gateway that dispatched the event.
        event : `GatewayDispatch`
            The event that was dispatched.
    """

    channel = client.get_channel(event.data["channel_id"])
    """ The channel that the message was deleted in. """

    guild = client.get_guild(event.data["guild_id"])
    """ The guild that the message was deleted in. """

    return "on_message_delete_bulk", [
        channel, guild, event.data["ids"]
    ]

def export():
    """ Exports the function. """
    return message_delete_bulk