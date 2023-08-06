import typing
import datetime

def parse_time(iso: str) -> int:
    """
        Convert an ISO8601 string to a timestamp.
    """
    return datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()

def get(iterable: typing.Iterable, **kwargs) -> typing.Union[None, typing.Any]:
    """
        Get the first element that matches the given kwargs.
    """

    for element in iterable:
        if all(getattr(element, key) == value for key, value in kwargs.items()):
            return element