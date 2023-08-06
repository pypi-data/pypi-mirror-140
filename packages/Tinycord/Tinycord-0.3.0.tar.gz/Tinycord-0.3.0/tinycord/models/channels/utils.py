from .channel import BaseChannel
from .dm import DMChannel
from .news import NewsChannel
from .text import TextChannel
from .voice import VoiceChannel
from ...utils import Snowflake
from .thread import ThreadChannel

def deserialize_channel(client, guild_id , **data):
    """
    This is the deserialize_channel function.
    
    Parameters
    ----------
    client : `Client`
        The main client.
    guild_id : `Snowflake`
        The guild id.
    data : `typing.Dict`
        The data that is used to create the channel.
    
    Returns
    -------
        Channel
    """
    
    data['guild_id'] =  Snowflake(guild_id)

    if data['type'] == 0:
        return TextChannel(client, **data)
    elif data['type'] == 2:
        return VoiceChannel(client, **data)
    elif data['type'] == 4:
        return NewsChannel(client, **data)
    # elif data['type'] == 5:
    #     return DMChannel(client, **data)
    elif data['type'] == 11:
        return ThreadChannel(client, **data)
    else:
        return BaseChannel(client, **data)