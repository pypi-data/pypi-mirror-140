import typing
import aiohttp
import asyncio
import logging

if typing.TYPE_CHECKING:
    from ..client import Client

from .router import Router
from .ratelimit import RateLimiter

logger = logging.getLogger('tinycord')

class HTTPClient:
    """
        The following functions are used to make requests to the gateway.
        They handle ratelimits and other errors. The way this works is that
        The client will try to make a request. If it fails, it will check if
        the error is a ratelimit. If it is, it will wait for the ratelimit
        to expire and then try again.
        
        Parameters
        ----------
        client: `Client`
            The client that is making the request.
    """
    def __init__(self, client: "Client", options: typing.Dict) -> None:
        from .. import __version__
        
        self.client = client
        """ The client that is making the request. """

        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        """ The session that is used to make the request. """

        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        """ The event loop that is used to make the request. """

        self.options: typing.Dict = options
        """ The proxy that is used to make the request. """

        self.headers: typing.Dict[str, str] = {
            'Authorization': self.client.token,
            'User-Agent': f'Tinycord/{__version__} (https://github.com/tinycord/Tinycord, {__version__})',
        }
        """ The headers that are used to make the request. """

        self.lock: asyncio.Lock = asyncio.Lock()
        """ The LOCK """

        self.ratelimiter = RateLimiter()
        """ The ratelimiter """

    async def request(self, route: "Router", **kwargs):
        """
            This function is used to make a request to the gateway.

            Parameters
            ----------
            url: `str`
                The url to make the request to.
            method: `str`
                The method to use.
        """
        headers = self.headers
        
        headers.update(kwargs.get('headers', {}))
        """ The headers that are used to make the request. """
        kwargs.pop('headers', None)
        """ The headers that are used to make the request. """

        logger.debug(f"Making request to {route.path}")
        """ The url to make the request to. """

        await self.ratelimiter.rest_bucket(
            route.path,
            route.method)
        """ To check if the ratelimit has expired. """

        response = await self.session.request(
            url=route.path,
            method=route.method,
            
            headers=headers,

            **kwargs,
            **self.options,
        )
        """ The response from the request. """

        logger.debug(f"Request responed with {route.method} {route.path} {response.status}")
        """ Log the response. """

        self.ratelimiter.save_bucket(
            route.path,
            route.method,
            response.headers)
        """ To save the bucket  """

        if 500 <= response.status < 600:
            raise Exception(f"{response.status} {response.reason}")
            """ If the status is 500 or above, raise an exception. """

        if response.status == 429:
            rest = (
                await response.json()).get("retry_after", 40)
            """ To get the retry_after value. """

            logger.debug(f"Ratelimit exceeded, waiting {rest} seconds")
            """ To log the retry_after value. """
            
            await asyncio.sleep(rest)
            """ To wait for the retry_after value. """

            return await self.request(
                route, **kwargs)
            """ To try again. """

        if response.ok:

            if response.headers['content-type'] == 'application/json':

                return await response.json()
                """ To return the json. """

            return await response.text()
            """ To return the response. """
