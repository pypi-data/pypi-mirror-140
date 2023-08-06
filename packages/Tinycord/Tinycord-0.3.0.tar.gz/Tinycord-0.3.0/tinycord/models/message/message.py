from __future__ import annotations

import typing
import dataclasses

if typing.TYPE_CHECKING:
    from ...client import Client
    from ..guild import Guild, Member, Emoji
    from ..channels import All

from ..mixins import Hashable
from ...utils import Snowflake
from ..user import User
from .reaction import Reaction
from .embed import Embed

@dataclasses.dataclass(repr=False)
class Message(Hashable):
    """
        This is the User it used to represent a user.

        Parameters
        ----------
        client : `Client`
            The main client.
        **data : `typing.Dict`
            The data that is used to create the message.

        Attributes
        ----------
        id : `Snowflake`
            The ID of the message.
        channel_id : `Snowflake`
            The ID of the channel.
        guild_id : `Snowflake`
            The ID of the guild.
        user : `User`
            The user of the message.
        content : `str`
            The content of the message.
        timestamp : `str`
            The timestamp of the message.
        edited_timestamp : `str`
            The edited timestamp of the message.
        tts : `bool`
            Whether the message is TTS or not.
        mention_everyone : `bool`
            Whether the message mentions everyone or not.
        mentions : `typing.List[str]`
            The mentions of the message.
        mention_roles : `typing.List[str]`
            The mention roles of the message.
        mention_channels : `typing.List[str]`
            The mention channels of the message.
        attachments : `typing.List`
            The attachments of the message.
        embeds : `typing.List[Embed]`
            The embeds of the message.
        reactions : `typing.Dict[str, Reaction]`
            The reactions of the message.
        nonce : `typing.Union[int, str]`
            The nonce of the message.
        pinned : `bool`
            Whether the message is pinned or not.
        webhook_id : `Snowflake`
            The webhook ID of the message.
        type : `int`
            The type of the message.
        activity : `typing.Dict[str, str]`
            The activity of the message.
        application : `typing.Dict[str, str]`
            The application of the message.
        application_id : `Snowflake`
            The application ID of the message.
        message_reference : `typing.Dict[str, str]`
            The message reference of the message.
        flags : `typing.List`
            The flags of the message.
        interaction : `typing.Union[int, None]`
            The interaction of the message.
        thread : `typing.Dict[str, typing.Any]`
            The thread of the message.
        components : `typing.Dict[str, typing.Any]`
            The components of the message.
        sticker_items : `typing.Dict[str, typing.Any]`
            The sticker items of the message.
        stickers : `typing.Union[str, None]`
            The stickers of the message.
            
    """
    def __init__(self, client: "Client", **data) -> None:
        self.client = client
        """The main client."""

        self.id: Snowflake = Snowflake(
            data.get('id'))
        """The ID of the message."""

        self.channel_id: Snowflake = Snowflake(
            data.get('channel_id'))

        self.guild_id: typing.Union[Snowflake, None] = Snowflake(
            data.get('guild_id'))
        """The guild id."""

        self.user: "User" = User(client, 
            **data.get('author', {}))
        """The author of the message."""

        self.content: str = data.get('content')
        """The content of the message."""

        self.timestamp: str = data.get('timestamp')
        """The timestamp of the message."""

        self.edited_timestamp: str = data.get('edited_timestamp')
        """The edited timestamp of the message."""

        self.tts: bool = data.get('tts')
        """Whether the message is TTS or not."""

        self.mention_everyone: bool = data.get('mention_everyone')
        """Whether the message mentions everyone or not."""

        self.mentions: typing.Union[typing.List[str], None] = data.get('mentions', [])
        """The mentions of the message."""

        self.mention_roles: typing.List = data.get('mention_roles')
        """The mention roles of the message."""

        self.mention_channels: typing.Union[typing.List[str], None] = data.get('mention_channels', [])
        """The mention channels of the message."""

        self.attachments: typing.List = data.get('attachments')
        """The attachments of the message."""

        self.embeds: typing.List["Embed"] = [
            Embed(**embed) for embed in data.get('embeds', [])]
        """The embeds of the message."""

        self.reactions: typing.Dict[str, "Reaction"] = {
            f'{reaction["emoji"]["name"]}:{reaction["emoji"]["id"]}' : Reaction(client, **reaction) for reaction in data.get('reactions', {})}
        """The reactions of the message."""

        self.nonce: typing.Union[int, str] = data.get('nonce', [])
        """The nonce of the message."""

        self.pinned: bool = data.get('pinned')
        """Whether the message is pinned or not."""

        self.webhook_id: typing.Union[Snowflake, None] = Snowflake(
            data.get('webhook_id'))
        """The webhook ID of the message."""

        self.type: int = data.get('type')
        """The type of the message."""

        self.activity: typing.Union[typing.Dict[str,str], None] = data.get('activity', {})
        """The activity of the message."""

        self.application: typing.Union[typing.Dict[str,str], None] = data.get('application', {})
        """The application of the message."""

        self.application_id: typing.Union[Snowflake, None] = Snowflake(
            data.get('application_id'))
        """The application ID of the message."""

        self.message_reference: typing.Union[typing.Dict[str,str], None] = data.get('message_reference', {})        
        """The message reference of the message."""

        self.flags: typing.List = data.get('flags', [])
        """The flags of the message."""
        
        self.interaction: typing.Union[int, None] = data.get('interaction_count', [])
        """The interaction of the message."""

        self.thread: typing.Dict[str, typing.Any] = data.get('thread', {})
        """The thread of the message."""
        
        self.components: typing.Dict[str, typing.Any] = data.get('components', {})
        """The components of the message."""
        
        self.sticker_items: typing.Dict[str, typing.Any] = data.get('sticker_items', {})
        """The sticker items of the message."""
        
        self.stickers: typing.Union[str, None] = data.get('stickers', [])
        """The stickers of the message."""

    def get_reaction(self, emoji_id: Snowflake, emoji_name: str) -> typing.Union[None, "Reaction"]:
        """
            Get the reaction of the message.

            Parameters
            ----------
            emoji : `Snowflake`
                The id of the emoji.
            emoji_name: `str`
                The emoji name

        """
        return self.reactions.get(f'{emoji_name}:{emoji_id}', None)

    @property
    def guild(self) -> typing.Union["Guild", None]:
        """The guild of the message."""

        return self.client.get_guild(self.guild_id)
    
    @property
    def channel(self) -> typing.Union["All", None]:
        """The channel of the message."""

        return self.client.get_channel(self.channel_id)

    @property
    def author(self) -> typing.Union["Member", None]:
        """The author id of the message."""

        return self.guild.get_member(self.user.id)

    async def pin(self) -> None:
        """
            Pin the message.
        """
        await self.client.api.channel_messages_pin(self.channel_id, self.id)

    async def unpin(self) -> None:
        """
            Unpin the message.
        """
        await self.client.api.channel_messages_unpin(self.channel_id, self.id)

    async def delete(self, reason: str = None) -> None:
        """
            Delete the message.
        """
        await self.client.api.channel_messages_delete(self.channel_id, self.id, reason)

    async def add_reaction(self, emoji: "Emoji" | str) -> None:
        """
            Add a reaction to the message.

            Parameters
            ----------
            emoji : `str`
                The emoji of the reaction.
        """
        await self.client.api.channel_messages_reactions_create_me(self.channel_id, self.id, emoji)
        
    async def delete_reaction(self, emoji: "Emoji") -> None:
        """
            Delete a reaction from the message.

            Parameters
            ----------
            emoji : `str`
                The emoji of the reaction.
        """
        await self.client.api.channel_messages_reactions_delete(self.channel_id, self.id, emoji)

    async def remove_reactions(self) -> None:
        """
            Remove all reactions from the message.
        """
        await self.client.api.channel_message(self.channel_id, self.id)

    async def remove_reaction(self, user_id, emoji) -> None:
        """
            Remove a reaction from the message.

            Parameters
            ----------
            user_id : `str`
                The user id of the reaction.
            emoji : `str`
                The emoji of the reaction.
        """
        await self.client.api.channel_messages_reactions_delete(self.channel_id, self.id, emoji, user_id)
        
    def __str__(self) -> str:
        """ The string representation of the message. """
        return str(self.content)