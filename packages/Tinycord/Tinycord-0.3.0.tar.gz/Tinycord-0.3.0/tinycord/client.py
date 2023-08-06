# Tinycord is a discord wrapper for python built on top of asyncio and aiohttp.
# LICENSE: MIT
# AUTHOR: xArty, H A Z E M

from __future__ import annotations

import typing
import logging
import asyncio
import logging
import collections
import functools

if typing.TYPE_CHECKING:
    from .intents import Intents
    from .models import *
    from .plugin import Plugin

from .core import Gateway, HTTPClient, Router, GatewayDispatch
from .middleware import get_middlewares
from .utils import Snowflake
from .api import APIClient

logger: logging.Logger = logging.Logger("tinycord")
events: typing.Dict[str, typing.List[str, typing.Union[typing.Callable, typing.Awaitable]]] = collections.defaultdict(list)

def middleware_event(event: str):
    """
        This function is used to register a middleware event.
        This is used to register events that are called before the event is called.
        
        Usage: 
        ```py
        @middleware_event("ready")
        def my_middleware(gatway, event):
            return "on_ready", [
                event
            ]

        @client.event
        def on_ready(event):
            print("Ready!")
        ```
            
    """
    def decorator(func: typing.Awaitable):
        
        async def warpper(cls, *args, **kwargs):
            return await func(cls, *args, **kwargs)
        
        events[event] = warpper
        return warpper
    return decorator

for event, ware in get_middlewares().items():
    """
        This function is used to register a middleware event.
        This is used to register middlewares before anything happens.
    """
    middleware_event(event)(ware)

class Client:
    """
        The bridge between Python and Discord API.
        This is the main class that is used to connect to Discord.

        Example:
        ```py
        client = Client()

        @client.event
        async def on_ready(shard):
            print("Ready!")

        client.run(token)
        ```
    """
    def __init__(
        self,
        token: str,
        *,
        bot: bool = True,
        intents: typing.List[Intents],
        reconnect: bool = True,
        disabled_events: typing.List[str] = [],

        ws_options: typing.Dict[str, typing.Any] = {},
        http_options: typing.Dict[str, typing.Any] = {},

        loop: asyncio.AbstractEventLoop = None,
    ) -> None:
        self.token = f'Bot {token}' if bot is True else token
        """ The token of the bot. """

        self.intents = sum([int(i) for i in intents]) if intents is list else intents
        """ The intents of the bot. """

        self.bot = bot
        """ Whether the bot is a bot or not. """

        self.reconnect = reconnect
        """ Whether the bot should reconnect or not. """

        self.is_ready = False
        """ Whether the bot is ready or not. """

        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop() if loop is None else loop
        """ The event loop of the bot. """

        self.http: "HTTPClient" = HTTPClient(self, options = http_options)
        """ The HTTP client of the bot. """

        self.api: "APIClient" = APIClient(self)
        """ The API client of the bot. """

        self.user: "User" = None
        """ The user of the bot. """

        self.messages: typing.Dict[str, "Message"] = {}
        """ The messages of the bot. """

        self.guilds: typing.Dict[str, "Guild"] = {}
        """ The guilds of the bot. """

        self.channels: typing.Dict[str, "All"] = {}
        """ The channels of the bot. """

        self.threads: typing.Dict[str, "ThreadChannel"] = {}
        """ The threads of the bot. """

        self.users: typing.Dict[str, "User"] = {}
        """ The users of the bot. """

        self.roles: typing.Dict[str, "Role"] = {}
        """ The roles of the bot. """

        self.plugins: typing.Dict[str, "Plugin"] = {}
        """ The plugins of the bot. """

        async def warrper():
            self.url = (await self.http.request(
                Router('/gateway', 'GET'))).get('url')

        self.loop.run_until_complete(warrper())
        """ The url of the gateway. """

        self.shards: typing.Dict[int, "Gateway"] = {}
        """ The shards of the bot. """

        self.disabled_events: typing.List[str] = disabled_events
        """ The disabled events of the bot. """

        self.ws_options: typing.Dict = ws_options
        """ The websocket options of the bot. """

        self.http_options: typing.Dict = http_options
        """ The HTTP options of the bot. """

    @classmethod
    def event(cls, func: typing.Callable = None) -> typing.Union[typing.Callable, typing.Awaitable]:
        """
            This function is used to register an event.
            This is used to register events that are called after the event is called.
            
            Parameters
            ----------
            func : `typing.Callable`
                The function to register.
        """

        events[func.__name__].append(func)

        return func

    @classmethod
    def listen(cls, event: str, exist: bool = False) -> typing.Union[typing.Callable, typing.Awaitable]:
        """
            This function is used to register an event.
            This is used to register events that are called after the event is called.

            Parameters
            ----------
            event : `str`
                The event to listen for.
        """
        def decorator(func: typing.Callable):
            if exist is False:
                events[event].append(func)
            else:
                events[event] = func

            return func

        return decorator

    async def wait_for(self, event: str, timeout: int) -> typing.Awaitable:
        """
            This function is used to wait for an event.

            Parameters
            ----------
            event : `str`
                The event to wait for.
            timeout : `int`
                The timeout of the event.
        """
        future = self.loop.create_future()

        self.listen(event)(future)

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            pass

    def add_plugin(self, plugin: "Plugin") -> None:
        """
            This function is used to add a plugin to the bot.

            Parameters
            ----------
            plugin : `Plugin`
                The plugin to add.
        """
        plugin.client = self

        for event, func in plugin.events.items():
            for callback in func:
                self.listen(event)(callback)

        self.plugins[plugin.name] = plugin

        return plugin

    def remove_plugin(self, plugin_name: str) -> None:
        """
            This function is used to remove a plugin from the bot.

            Parameters
            ----------
            plugin : `Plugin`
                The plugin to remove.
        """
        plugin = self.plugins.get(plugin_name, None)

        if plugin == None:
            return

        for event, func in plugin.events.items():
            for callback in func:
                del events[event][events[event].index(callback)]

        del self.plugins[plugin.name]
            
    def connect(self) -> None:
        """
            This function is used to connect to Discord.
        """
        asyncio.ensure_future(self.start_shard(0, 1), loop = self.loop)

        logger.info("Connecting to Discord...")

        self.loop.run_forever()

    def connect_autosharded(self) -> None:
        """
            This function is used to connect to Discord with autosharding.
        """
        self.info = self.loop.run_until_complete(self.http.request(Router("/gateway/bot", "GET")))

        for shard in range(self.info['shards']):

            asyncio.ensure_future(
                self.start_shard(shard, self.info['shards']),
                loop = self.loop,
            )
            
            self.loop.run_forever()

    async def start_shard(
        self,
        shard_id: int,
        shard_count: int,
    ) -> None:
        """
            This function is used to start a shard.
        """
        
        gateway = Gateway(
            token = self.token,
            intents = self.intents,
            url = self.url,
            shard_id = shard_id,
            shard_count = shard_count,
            options = self.ws_options,
        )

        self.shards[shard_id] = gateway

        gateway.append_handler({
            0: functools.partial(self.handle_event, gateway),
        })

        asyncio.create_task(gateway.start_connection())

    async def handle_middleware(self, payload: "GatewayDispatch", gateway: "Gateway") -> None:
        """
            This function is used to handle middleware events.
            It's called before the event is called. Which means that you can modify the event.
            It's very useful for thing like event handling and event praseing.
        """
        event = payload.event.lower()
        ware = events.get(event,None)

        if ware is not None:

            extractable = await ware(self, gateway, payload)
   
            logger.debug(f"Middleware {event} has been called.")

            if not isinstance(extractable, tuple):
                raise RuntimeError(
                    f"Return type from `{event}` middleware must be tuple. "
                )

            event = extractable[0]
            args = extractable[1]

            callback = events.get(event, None)

            return (event, args, callback)

        return (None, None, None)

    async def handle_event(self, payload: "GatewayDispatch", gateway: "Gateway") -> None:
        """
            This function is used to handle an event.
            It's called after the middleware is called.
        """

        await self.dispatch('on_socket_raw', payload, gateway)

        event, args, callback = await self.handle_middleware(gateway , payload)

        logger.debug(f"Event {event} has been called.")
        
        if callback is not None:
            if self.is_ready:
                for event_callback in callback:
                    if event not in self.disabled_events:
                        if asyncio.isfuture(event_callback):
                            event_callback.set_result(*args)

                            events[event].remove(event_callback)
                        else:
                            await event_callback(*args)

    async def dispatch(self, event: str, / ,*args: typing.Tuple) -> typing.Any:
        """
            To disaptch an event

            Parameters
            ----------
            event : `str`
                The event to dispatch.
            args : `typing.Tuple`
                The arguments of the event.
        """
        
        for callback in events.get(event, []):
            if event not in self.disabled_events:
                await callback(*args)
                    

    def get_guild(self, id: str) -> "Guild":
        """Get a guild from the cache.

        Parameters
        ----------
        id : `Snowflake`
            The ID of the guild.

        """

        return self.guilds.get(str(id), None)

    def get_user(self, id: Snowflake) -> typing.Union["User", None]:
        """Get a user from the cache.

        Parameters
        ----------
        id : `Snowflake`
            The ID of the user.

        """

        return self.users.get(str(id), None)

    def get_channel(self, id: Snowflake) -> typing.Union["All", None]:
        """Get a channel from the cache

        Parameters
        ----------
        id : `Snowflake`
            The ID of the channel.

        """

        return self.channels.get(str(id), None)

    def get_thread(self, id: Snowflake) -> typing.Union["ThreadChannel", None]:
        """Get a thread from the cache.

        Parameters
        ----------
        id : `Snowflake`
            The ID of the thread.

        """

        return self.threads.get(str(id), None)

    def get_message(self, id: Snowflake) -> typing.Union["Message", None]:
        """Get a message from the cache.

        Parameters
        ----------
        id : `Snowflake`
            The ID of the message.


        """

        return self.messages.get(str(id), None)

    def get_shard(self, guild: "Guild") -> typing.Union[None, "Gateway"]:
        """Get a shard from the cache.

        Parameters
        ----------
        guild : `Guild`
            The guild to get the shard from.

        """

        return self.shards.get(int(guild.hash % len(self.shards)), None)

    def get_role(self, id: Snowflake) -> typing.Union["Role", None]:
        """Get a role from the cache.

        Parameters
        ----------
        id : `Snowflake`
            The ID of the role.
        """

        return self.roles.get(str(id), None)

    @property
    def shards_latency(self) -> typing.List[float]:
        """
            Get the latency of all shards.
        """

        return [shard.latency for shard in self.shards.values()]