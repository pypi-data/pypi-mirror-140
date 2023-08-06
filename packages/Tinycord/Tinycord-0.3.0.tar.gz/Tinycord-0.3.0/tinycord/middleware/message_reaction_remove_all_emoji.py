import typing

if typing.TYPE_CHECKING:
    from ..client import Client
    from ..core import Gateway, GatewayDispatch

from ..models import Emoji
    
async def message_reaction_remove_all_emoji(client: "Client", gateway: "Gateway", event: "GatewayDispatch") -> typing.List[typing.Awaitable]:
    """
        |coro|
        This event called when a emoji been removed from the message.
        It does provide the channel, message and the emoji.

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

    message = client.get_message(event.data["message_id"])
    """ The message that the reaction was removed from. """

    emoji = Emoji(client, **event.data["emoji"])
    """ The emoji that the reaction was removed from. """

    del message.reactions[f'{emoji.name}:{emoji.id}']
    """ The count of the reaction that was removed. """

    return "on_message_reaction_remove_all_emoji", [
        channel, message, emoji
    ]

def export():
    """ Exports the function. """
    return message_reaction_remove_all_emoji