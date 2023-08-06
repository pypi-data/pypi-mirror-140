import typing

if typing.TYPE_CHECKING:
    from ..client import Client
    from ..core import Gateway, GatewayDispatch
    
from ..models import Guild

async def guild_update(client: "Client", gateway: "Gateway", event: "GatewayDispatch") -> typing.List[typing.Awaitable]:
    """
        |coro|
        This event called when a guild has been updated.
        It does parse the channel data, update the data and update the cache and return the event with the args.
    
        Parameters
        ----------
        client : `Client`
            The main client.
        gateway : `Gateway`
            The gateway that dispatched the event.
        event : `GatewayDispatch`
            The event that was dispatched.
    """

    before = client.get_guild(event.data["guild_id"])
    """ The old guild from the cache. """

    for key, val in before.rawdata.items():
        if key not in event.data:
            event.data[key] = val

    after = Guild(client, **event.data)
    """ The new guild. """
    
    client.guilds[after.id] = after
    """ Update the cache. """

    return "on_guild_update", [
        before, after
    ]


def export():
    """ Exports the function. """
    return guild_update