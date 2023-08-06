import typing

if typing.TYPE_CHECKING:
    from ..client import Client
    from ..core import Gateway, GatewayDispatch

from ..models import Role

async def guild_role_update(client: "Client", gateway: "Gateway", event: "GatewayDispatch") -> typing.List[typing.Awaitable]:
    """
        |coro|
        This event called when a role is updated.
        It does prase the role data and returns the event with the guild and the role.

        Parameters
        ----------
        client : `Client`
            The main client.
        gateway : `Gateway`
            The gateway that dispatched the event.
        event : `GatewayDispatch`
            The event that was dispatched.
    """
    guild = client.get_guild(event.data["guild_id"])
    """ The guild that the role was updated in. """

    before = guild.get_role(event.data["role_id"])
    """ The old role. """

    after = Role(client, event.data['guild_id'] , **event.data['role'])
    """ The role that was updated. """

    guild.roles[str(after.id)] = after
    """ Cache the role. """

    return "on_role_update", [
        guild, before, after
    ]
    """ The event that was dispatched. """

def export():
    """ Exports the function. """
    return guild_role_update