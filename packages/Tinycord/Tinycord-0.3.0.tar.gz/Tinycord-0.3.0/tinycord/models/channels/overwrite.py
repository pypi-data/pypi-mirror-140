import typing

from ...utils import Snowflake, Permission

class Overwrite:
    def __init__(self) -> None:
        self.id: int = None
        """The ID of the overwrite."""

        self.type: str = None
        """The type of the overwrite."""

        self.allow: int = None
        """The allow permissions of the overwrite."""

        self.deny: int = None
        """The deny permissions of the overwrite."""

    @classmethod
    def read(cls, **data) -> None:
        """
        Reads the data from the given data.
        """

        cls.id = Snowflake(data.get('id'))

        cls.type = data.get('type')

        cls.allow = Permission.compute(
            data.get('allow'))

        cls.deny = Permission.compute(
            data.get('deny'))

        cls.raw = data

        return cls

    @classmethod
    def write(cls, id: int, type: int, allow: typing.List[str], deny: typing.List[str] = 0 ) -> None:
        """
        Writes the data to the given data.
        """

        return {
            'id': id,
            'type': type,
            'allow': Permission.convert(allow),
            'deny': Permission.convert(deny)
        }

    @classmethod
    def form_dict(cls) -> typing.Dict[str, typing.Union[typing.List, str]]:
        """
        Returns the form dict of the object.
        """

        return {
            'id': cls.id,
            'type': cls.type,
            'allow': Permission.convert(cls.allow),
            'deny': Permission.convert(cls.deny)
        }

    def __repr__(self) -> str:
        """
            Returns the representation of the object.
        """
        return f'<Overwrite id={self.id} >'