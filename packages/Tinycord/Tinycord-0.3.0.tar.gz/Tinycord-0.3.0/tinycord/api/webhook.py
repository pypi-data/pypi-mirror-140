import aiohttp
import typing
import json

if typing.TYPE_CHECKING:
    from ..client import Client

from ..core import Router
from ..models import *

class WebhookAPI:
    def __init__(self, client: "Client") -> None:
        self.client = client
        """The client."""

    async def create_webhook(self, channel_id: int, name:str, avatar:str):
        """
            Create a webhook.

            Parameters
            ----------
            channel_id : `int`
                The id of the channel.
            name : `str`
                The name of the webhook.
            avatar : `str`
                The avatar of the webhook.
        """
        return await self.client.http.request(
            Router("POST", f"/channels/{channel_id}/webhooks",),
        )

    async def get_webhook(self, webhook_id: int):
        """
            Get a webhook.

            Parameters
            ----------
            webhook_id : `int`
                The id of the webhook.
        """
        res =  await self.client.http.request(
            Router("GET", f"/webhooks/{webhook_id}",),
        )

        return Webhook(self.client, **res)

    async def get_webhook_with_token(self, webhook_id: int, token: str):
        """
            Get a webhook with token.

            Parameters
            ----------
            webhook_id : `int`
                The id of the webhook.
            token : `str`
                The token of the webhook.
        """
        res =  await self.client.http.request(
            Router("GET", f"/webhooks/{webhook_id}/{token}",),
        )

        return Webhook(self.client, **res)

    async def webhook_edit(self, webhook_id: int, **data):
        """
            Edit a webhook.

            Parameters
            ----------
            webhook_id : `int`
                The id of the webhook.
            **data : `typing.Dict`
                The data that is used to edit the webhook.
        """
        res = await self.client.http.request(
            Router("PATCH", f"/webhooks/{webhook_id}",),
            json=data,
        )

        return Webhook(self.client, **res)

    async def wehbook_edit_with_token(self, webhook_id: int, token: str, **data):
        """
            Edit a webhook with token.

            Parameters
            ----------
            webhook_id : `int`
                The id of the webhook.
            token : `str`
                The token of the webhook.
            **data : `typing.Dict`
                The data that is used to edit the webhook.
        """
        res = await self.client.http.request(
            Router("PATCH", f"/webhooks/{webhook_id}/{token}",),
            json=data,
        )

        return Webhook(self.client, **res)

    async def webhook_delete(self, webhook_id: int):
        """
            Delete a webhook.

            Parameters
            ----------
            webhook_id : `int`
                The id of the webhook.
        """
        await self.client.http.request(
            Router("DELETE", f"/webhooks/{webhook_id}",),
        )

    async def webhook_delete_with_token(self, webhook_id: int, token: str):
        """
            Delete a webhook with token.

            Parameters
            ----------
            webhook_id : `int`
                The id of the webhook.
            token : `str`
                The token of the webhook.
        """
        await self.client.http.request(
            Router("DELETE", f"/webhooks/{webhook_id}/{token}",),
        )

    async def webhook_execute(self, webhook_id: int, token: str, **data):
        """
            Execute a webhook.

            Parameters
            ----------
            webhook_id : `int`
                The id of the webhook.
            token : `str`
                The token of the webhook.
            **data : `typing.Dict`
                The data that is used to execute the webhook.
        """

        res =  await self.client.http.request(
            Router("POST", f"/webhooks/{webhook_id}/{token}",),
            data=json.dumps({'payload_json': json.dumps(data),'files': data.get('files', [])}), 
            headers={'Content-Type': 'multipart/form-data'}
        )
        
        return Message(self.client, **res)

    async def webhook_get_message(self, webhook_id: int, token: str, message_id: int):
        """
            Get a message from a webhook.

            Parameters
            ----------
            webhook_id : `int`
                The id of the webhook.
            token : `str`
                The token of the webhook.
            message_id : `int`
                The id of the message.
        """
        res =  await self.client.http.request(
            Router("GET", f"/webhooks/{webhook_id}/{token}/{message_id}",),
        )

        return Message(self.client, **res)

    async def webhook_message_edit(self, webhook_id: int, token: str, message_id: int, **data):
        """
            Edit a webhook message.

            Parameters
            ----------
            webhook_id : `int`
                The id of the webhook.
            token : `str`
                The token of the webhook.
            **data : `typing.Dict`
                The data that is used to edit the webhook message.
        """

        form = aiohttp.FormData()

        if 'files' in data:
            for index, file in enumerate(data['files']):

                form.add_field(
                    name=f'file{index}',
                    value=file.data,
                    filename=file.filename,
                    content_type="application/octet-stream",
                )

            del data['files']

        form.add_field(
            name='payload_json',
            value=json.dumps(data),
            content_type="application/json",
        )

        res =  await self.client.http.request(
            Router("PATCH", f"/webhooks/{webhook_id}/{token}/messages/{message_id}",),
            data=form, 
        )
        
        return Message(self.client, **res)

    async def webhook_message_delete(self, webhook_id: int, token: str, message_id: int):
        """
            Delete a webhook message.

            Parameters
            ----------
            webhook_id : `int`
                The id of the webhook.
            token : `str`
                The token of the webhook.
            message_id : `int`
                The id of the message.
        """
        await self.client.http.request(
            Router("DELETE", f"/webhooks/{webhook_id}/{token}/messages/{message_id}",),
        )