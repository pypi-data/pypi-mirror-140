import typing

class Field:
    """
        The field.
    """
    def __init__(self, name: str, value: str, inline: bool = False) -> None:
        self.name: str = name
        """The name of the field."""

        self.value: str = value
        """The value of the field."""

        self.inline: bool = inline
        """Whether the field is inline or not."""

class Embed:
    """
        The embed that looks sweet and stuff.

        Parameters
        ----------
        title : `str`
            The title.
        description : `str`
            The description.
        url : `str`
            The url.
        timestamp : `str`
            The timestamp.
        color : `int`
            The color.

        footer : `dict`
            The footer.
        image : `dict`
            The image.
        thumbnail : `dict`
            The thumbnail.
        video : `dict`
            The video.
        provider : `dict`
            The provider.
        author : `dict`
            The author.
        fields : `list`
            The fields.
        
    """
    def __init__(
        self,
        title: str = None,
        type: str = None,
        description: str = None,
        url: str = None,
        timestamp: str = None,
        color: int = None,

        footer: typing.Dict[str, typing.Any] = {},
        image: typing.Dict[str, typing.Any] = {},
        thumbnail: typing.Dict[str, typing.Any] = {},
        video: typing.Dict[str, typing.Any] = {},
        provider: typing.Dict[str, typing.Any] = {},
        author: typing.Dict[str, typing.Any] = {},
        fields: typing.List[typing.Dict[str, typing.Any]] = []
    ) -> None:
        self.title: str = title
        """The title."""

        self.type: str = type
        """The type."""

        self.description: str = description
        """The description."""

        self.url: str = url
        """The url."""

        self.time_stamp: str = timestamp
        """The timestamp."""

        self.color: int = color
        """The color."""

        self.footer: typing.Dict[str, str] = footer 
        """The footer."""

        self.image: typing.Dict[str, str] = image
        """The image."""

        self.thumbnail: typing.Dict[str, str] = thumbnail
        """The thumbnail."""

        self.video: typing.Dict[str, str] = video
        """The video."""

        self.provider: typing.Dict[str, str] = provider
        """The provider."""

        self.author: typing.Dict[str, str] = author
        """The author."""

        self.fields: typing.List[typing.Dict[str, str]] = [Field(**field) for field in fields]
        """The fields."""


    def set_footer(self, text: str, icon_url: str = None, proxy_icon_url: str = None) -> None:
        """
            Set the footer.

            Parameters
            ----------
            text : `str`
                The text.
            icon_url : `str`
                The icon url.
            proxy_icon_url : `str`
                The proxy icon url.
        """
        self.footer = {
            "text": text,
            "icon_url": icon_url,
            "proxy_icon_url": proxy_icon_url
        }

    def set_image(self, url: str, proxy_url: str = None, height: int = None, width: int = None) -> None:
        """
            Set the image.

            Parameters
            ----------
            url : `str`
                The url.
            proxy_url : `str`
                The proxy url.
            height : `int`
                The height.
            width : `int`
                The width.
        """
        self.image = {
            "url": url,
            "proxy_url": proxy_url,
            "height": height,
            "width": width
        }

    def set_thumbnail(self, url: str, proxy_url: str = None, height: int = None, width: int = None) -> None:
        """
            Set the thumbnail.

            Parameters
            ----------
            url : `str`
                The url.
            proxy_url : `str`
                The proxy url.
            height : `int`
                The height.
            width : `int`
                The width.
        """
        self.thumbnail = {
            "url": url,
            "proxy_url": proxy_url,
            "height": height,
            "width": width
        }

    def set_video(self, url: str, height: int, width: int) -> None:
        """
            Set the video.

            Parameters
            ----------
            url : `str`
                The url.
            height : `int`
                The height.
            width : `int`
                The width.
        """
        self.video = {
            "url": url,
            "height": height,
            "width": width
        }

    def set_provider(self, name: str, url: str) -> None:
        """
            Set the provider.

            Parameters
            ----------
            name : `str`
                The name.
            url : `str`
                The url.
        """
        self.provider = {
            "name": name,
            "url": url
        }

    def set_author(self, name: str, url: str = None, icon_url: str = None, proxy_icon_url: str = None) -> None:
        """
            Set the author.

            Parameters
            ----------
            name : `str`
                The name.
            url : `str`
                The url.
            icon_url : `str`
                The icon url.
            proxy_icon_url : `str`
                The proxy icon url.
        """
        self.author = {
            "name": name,
            "url": url,
            "icon_url": icon_url,
            "proxy_icon_url": proxy_icon_url
        }

    def add_field(self, name: str, value: str, inline: bool = False) -> None:
        """
            Add a field.

            Parameters
            ----------
            name : `str`
                The name.
            value : `str`
                The value.
            inline : `bool`
                The inline.
        """
        self.fields.append({
            "name": name,
            "value": value,
            "inline": inline
        })

    def form_dict(self) -> typing.Dict[str, typing.Any]:
        """
            Form a dict.

            Returns
            -------
            `dict`
                The dict.
        """
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "timestamp": self.time_stamp,
            "color": self.color,
            "footer": self.footer,
            "image": self.image,
            "thumbnail": self.thumbnail,
            "video": self.video,
            "provider": self.provider,
            "author": self.author,
            "fields": self.fields
        }
    

    