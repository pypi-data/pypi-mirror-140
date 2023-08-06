import typing

if typing.TYPE_CHECKING:
    from ..client import Client
    from ..core import Gateway, GatewayDispatch

async def guild_delete(client: "Client", gateway: "Gateway", event: "GatewayDispatch") -> typing.List[typing.Awaitable]:
    """
        |coro|
        This event called when a guild is deleted.
        It does prase the guild data and returns the event with the guild.

        Parameters
        ----------
        client : `Client`
            The main client.
        gateway : `Gateway`
            The gateway that dispatched the event.
        event : `GatewayDispatch`
            The event that was dispatched.
    """
    guild = client.get_guild(event.data["id"])
    """ The guild that was deleted. """

    try:
        for id, channel in guild.channels.items():
            del client.channels[str(id)]
            """ Try to delete the channel from the cache. """
        
        for id, user in guild.users.items():
            del client.users[str(id)]
            """ Try to delete the user from the cache. """

        for id, thread in guild.threads.items():
            del client.threads[str(id)]

        del client.guilds[str(guild.id)]
        """ Try to delete the guild from the cache. """
    except KeyError:
        pass

    return "on_guild_delete", [
        guild
    ]


def export():
    """ Exports the function. """
    return guild_delete