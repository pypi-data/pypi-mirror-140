from __future__ import annotations

import itertools
import typing
import aiohttp
import asyncio
import logging
import zlib
import time

from .dispatch import GatewayDispatch
from ..exceptions import GatewayError

logger: logging.Logger = logging.getLogger("tinycord")
ZLIB_SUFFIX = b'\x00\x00\xff\xff'
inflator = zlib.decompressobj()

class GatewayRatelimit:
    def __init__(self, limit=120, per=60):
        self.limit = limit
        self.per = per
        self.init_time = time.time()

    async def handle_ratelimit(self):
        if time.time() - self.init_time >= self.per:
            self.init_time = time.time()
            self.limit = 120
        else:
            self.limit -= 1
            if self.limit <= 0:
                await asyncio.sleep(self.per - (time.time() - self.init_time))
                self.init_time = time.time()
                self.limit = 120


class Gateway:
    """
        The gateway is the handler for all the events and opcodes coming from the `Discord Gateway`
    """
    def __init__(
        self,
        token: str,
        *,
        intents: typing.List[str],
        url: str,
        shard_id: int,
        shard_count: int,

        version: int = 9,
        max_retries: int = 5,
        reconnect: bool = True,
        options: typing.Dict = {}
    ) -> None:
        self.token = token
        """ The token of the bot """

        self.intents = intents
        """ The intents of the bot """

        self.url = url
        """ The url of the gateway """

        self.id = shard_id
        """ The shard id of the bot """

        self.shard_count = shard_count
        """ The shard count of the bot """

        self.version = version
        """ The version of the gateway """

        self.max_retries = max_retries
        """ The max retries of the gateway """

        self.reconnect = reconnect
        """ The reconnect of the gateway """

        self.__handler: typing.Dict[str, typing.Callable] = {
            7: self.handle_reconnect,
            9: self.handle_invalid_session,
            10: self.handle_hello,
            11: self.handle_heartbeat_ack,
        }
        """ The handler for the opcodes """

        self.__errors: typing.Dict[int, typing.Callable] = {
            4000: GatewayError("Unknown Error"),
            4001: GatewayError("Unknown Opcode"),
            4002: GatewayError("Decode Error"),
            4003: GatewayError("Not Authenticated"),
            4004: GatewayError("Authentication Failed"),
            4005: GatewayError("Already Authenticated"),
            4007: GatewayError("Invalid Sequence"),
            4008: GatewayError("Rate Limited"),
            4009: GatewayError("Session Timeout"),
            4010: GatewayError("Invalid Shard"),
            4011: GatewayError("Sharding Required"),
            4012: GatewayError("Invalid API Version"),
            4013: GatewayError("Invalid Intents"),
            4014: GatewayError("Disallowed Intents"),
        }
        """ The error handler for the opcodes """

        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        """ The session of the gateway """

        self.buffer: bytearray = bytearray()
        """ The buffer for the decompression """

        self.should_reconnect: bool = False
        """ The reconnect of the gateway """

        self.sequence: int = 0
        """ The sequence of the gateway """

        self.session_id: int = None
        """ The session id of the gateway """

        self.heartbeat_task: typing.Optional[asyncio.Task] = None
        """ The heartbeat task of the gateway """

        self.heartbeat_interval: int = None
        """ The heartbeat interval of the gateway """

        self.heartbeat_ack: bool = False
        """ The heartbeat ack of the gateway """

        self.last_heartbeat_ack: float = 0
        """ The last heartbeat ack of the gateway """

        self.ratelimit = GatewayRatelimit()
        """ The ratelimiter for the gatway """

        self.__latency: float = 0
        """ The latency of the gateway """
        
        self.options = options
        """ The options of the gateway """

    def append_handler(self, handlers: typing.Dict[int, typing.Callable]) -> None:
        """
            This function is used to append a handler to the gateway.

            Parameters
            ----------
            handlers: `typing.Dict[int, typing.Callable]`
                A dictionary of opcodes and their handlers.
        """
        self.__handler.update(handlers)

    def append_error(self, errors: typing.Dict[int, typing.Callable]) -> None:
        """
            This function is used to append a error handler to the gateway.

            Parameters
            ----------
            errors: `typing.Dict[int, typing.Callable]`
                A dictionary of opcodes and their handlers.
        """
        self.__errors.update(errors)

    def decompress(self, data: bytes) -> bytes:
        """
            This function is used to decompress the data.

            Parameters
            ----------
            data: `bytes`
                The data to decompress.
        """

        self.buffer.extend(data)
        
        if len(self.buffer) < 4 or self.buffer[-4:] != ZLIB_SUFFIX:
            return None
        
        msg = inflator.decompress(self.buffer)
        self.buffer.clear()

        return msg

    def make_url(self) -> str:
        """
            This function is used to make the url for the gateway.
        """
        return f"{self.url}?v={self.version}&encoding=json&compress=zlib-stream"

    async def send(self, op: int, payload: typing.Dict[str,typing.Any]):
        """
            |coro|
            This function is the handler for the hello opcode.
        """
        await self.ratelimit.handle_ratelimit()

        if op == 6 and self.heartbeat_task is not None:
            await asyncio.sleep(6)
        
        await self.websocket.send_json({
            "op": op,
            "d": payload,
        })

    async def voice_connect(self, self_mute: bool, self_deaf: bool, channel_id: int, guild_id: int) -> None:
        """
            |coro|
            This function is used to connect to a voice.

            Parameters
            ----------
            self_mute: `bool`
                The self mute of the voice.
            self_deaf: `bool`
                The self deaf of the voice.
            channel_id: `int`
                The channel id of the voice.
            guild_id: `int`
                The guild id of the voice.
        """
        await self.send(4,{
            "guild_id": guild_id,
            "channel_id": channel_id,
            "self_mute": self_mute,
            "self_deaf": self_deaf,
        })

    async def voice_disconnect(self, guild_id: int) -> None:
        """
            |coro|
            This function is used to disconnect from a voice.

            Parameters
            ----------
            guild_id: `int`
                The guild id of the voice.
        """
        await self.send(4,{
            "guild_id": guild_id,
            "channel_id": None,
            "self_mute": False,
            "self_deaf": False,
        })

    async def send_identify(self, payload: GatewayDispatch) -> None:
        """
            |coro|
            This function is used to send the identify opcode.
        """
        if self.should_reconnect:
            logger.debug(
                f" {self.id} Reconnecting to gateway..."
            )

            await self.send(
                op=6,
                payload={
                    "token": self.token,
                    "session_id": self.session_id,
                    "seq": self.sequence,
                }
            )

            return None

        await self.send(
            op=2,
            payload={
                "token": self.token,
                "properties": {
                    "$os": "linux",
                    "$browser": "tinycord",
                    "$device": "tinycord",
                },
                "compress": True,
                "large_threshold": 250,
                "shard": [self.id, self.shard_count],
                "intents": self.intents,
            },
        )

        if not self.heartbeat_interval:

            self.heartbeat_interval = int(
                payload.data['heartbeat_interval'] / 1000
            )

        if not self.heartbeat_task or self.heartbeat_task.cancelled():
            self.heartbeat_task = asyncio.ensure_future(
                self.handle_heartbeat_task()
            )


    async def start_connection(self) -> None:
        """
            |coro|
            This function is used to start the connection.
            It do connect to the gateway and start the event handling.
        """
        for i in itertools.count():
            try:
                self.websocket = await self.session.ws_connect(
                    self.make_url(),
                    **self.options
                )
                break
            except aiohttp.ClientConnectorError:
                logger.warning(
                    f" {self.id} Failed to connect to gateway, retrying in 10 seconds..."
                )

                await asyncio.sleep(10)
                await self.start_connection()

        await self.start_event_handling()

    async def handle_message(self, message: aiohttp.ClientWebSocketResponse):
        """
            |coro|
            This is the handler for the message that come from the websocket
        """
        if message.type == aiohttp.WSMsgType.TEXT:
            await self.handle_data(message.data)

        elif message.type == aiohttp.WSMsgType.BINARY:

            data = self.decompress(message.data)
            if data is None:
                return None
            await self.handle_data(data)

        elif message.type == aiohttp.WSMsgType.ERROR:
            logger.warning(
                f" {self.id} Websocket error: {message.exception()}"
            )

        elif message.type == aiohttp.WSMsgType.CLOSE:
            await self.handle_close(message.close_code)

        await self.handle_error(self.websocket.close_code)

    async def handle_close(self, code: int):
        """
            |coro|
            This is the handler for the websocket close.
        """
        logger.warning(
            f" {self.id} Websocket closed: {self.websocket.close_code}"
        )

        self.buffer = bytearray()
        self.should_reconnect = True

        if self.heartbeat_task is not None:
            self.heartbeat_task.cancel()

        if code and 4000 <= code <= 4010:
            self.session_id = None
            
        await self.start_connection()

    async def handle_error(self, code: int):
        """
            |coro|
            This is the handler for the error that come from the websocket
        """

        error = self.__errors.get(code, None)

        if error is not None:
            raise error

    async def start_event_handling(self):
        """
            |coro|
            This function is the responsible of handling the event and praseing the data
        """
        async for message in self.websocket:
            await self.handle_message(message)

    async def handle_data(self, data: str):
        """
            |coro|
            This function is the handler for the data that come from the websocket.
        """
        payload = GatewayDispatch.form(data)

        if payload.seq is not None:
            self.sequence = payload.seq

        asyncio.ensure_future(
            self.__handler.get(payload.op)(payload)
        )

    async def handle_hello(self, payload: GatewayDispatch):
        """
            |coro|
            This function is the handler for the hello opcode.
        """

        logger.info(
            f" {self.id} Connected to gateway"
        )

        await self.send_identify(payload)

    async def handle_reconnect(self, payload: GatewayDispatch):
        """
            |coro|
            This function is the handler for the reconnect opcode.
        """
        logger.debug(
            f" {self.id} Reconnecting to gateway..."
        )

        self.should_reconnect = True

        await self.start_connection()

    async def handle_invalid_session(self, payload: GatewayDispatch):
        """
            |coro|
            This function is the handler for the invalid session opcode.
        """
        logger.warning(
            f" {self.id} Invalid session, reconnecting..."
        )

        self.session_id = None
        self.sequence = 0
        """ Just to be sure """

        await asyncio.sleep(5)
        """ SLEEP! """

        await self.send_identify(payload)

    async def handle_heartbeat_ack(self, payload: GatewayDispatch):
        """
            |coro|
            This function is the handler for the heartbeat opcode.
        """
        if not self.heartbeat_ack:
            logger.debug(
                f" {self.id} Received heartbeat ack"
            )
            

            self.__latency = (time.time() - self.last_heartbeat_ack) * 1000

            self.heartbeat_ack = True

    async def handle_heartbeat_task(self):
        """
            |coro|
            This function is the handler for the heartbeat task.
        """
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            
            await self.send(1, self.sequence)

            self.last_heartbeat_ack = time.time()

            logger.debug(
                f" {self.id} Heartbeat sent to gateway..."
            )

    async def update_status(self, **kwargs) -> None:
        """
            |coro|
            This function is used to update the status of the bot.
        """

        await self.send(
            op=3,
            payload=kwargs
        )

    @property
    def latency(self) -> float:
        return self.__latency if self.__latency != 0 else float('nan')
        

    def __repr__(self) -> str:
        return f'<GatewayShard {self.id}>'