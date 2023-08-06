from .client import Client, middleware_event
from .plugin import Plugin
from .intents import Intents

from .core import Gateway, GatewayDispatch, HTTPClient, Router

from . import models as discord
from .models import *

from .utils import Snowflake

from .ext import commands

__all__ = [
    *discord.guild.__all__,
    *discord.channels.__all__,
    *discord.user.__all__,
    *discord.message.__all__,

    'Gateway', 'GatewayDispatch', 'HTTPClient', 'Router',
    'Plugin', 'Intents', 'Snowflake', 'Client', 'middleware_event',
]

__name__ = 'TinyCord'
__creator__ = 'xArty4'
__version__ = '0.1'
__license__ = 'MIT'
__url__ = 'https://github.com/tinycord/Tinycord'