import typing
import asyncio
import time

class RateLimiter:
    def __init__(self) -> None:
        self.buckets: typing.Dict[str, typing.Dict] = {}
        """The buckets."""
        self.map: typing.Dict[str, str] = {}

    def save_bucket(self, endpoint: str, method: str, headers: typing.Dict) -> None:
        """
            The method to save the bucket.

            Parameters
            ----------
            endpoint : `str`
                The endpoint.
            method : `str`
                The method.
            headers : `typing.Dict`
                The headers.
        """
        bucket_id = headers.get("X-RateLimit-Bucket")

        if not bucket_id:
            return 

        self.map[(endpoint, method)] = bucket_id
            
        self.buckets[bucket_id] = {
            "limit": int(headers.get("X-RateLimit-Limit")),
            "remaining": int(headers.get("X-RateLimit-Remaining")),
            "reset": float(headers.get("X-RateLimit-Reset")),
            "reset_after": float(headers.get("X-RateLimit-Reset")) - time.time()
        }

    async def rest_bucket(self, endpoint: str, method:str) -> None:
        """
            The method to rest the bucket.

            Parameters
            ----------
            endpoint : `str`
                The endpoint.
            method : `str`
                The method.
        """
        bucket = self.map.get((endpoint, method))

        if not bucket:
            return

        bucket_data = self.buckets[bucket]

        if bucket_data["remaining"] == 0:
            await asyncio.sleep(bucket_data["remaining"])
            
            self.buckets[bucket]["remaining"] = bucket_data["limit"]
