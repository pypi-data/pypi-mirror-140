import typing

class File:
    """
        The file.

        Parameters
        ----------
        path : `str`
            The path of the file.

        Attributes
        ----------
        file : `file`
            The file.
        filename : `str`
            The filename.
        data : `bytes`
            The data.
    """
    def __init__(self, path: str) -> None:
        self.file: typing.IO = open(path, "rb")
        """The file."""

        self.filename: str = self.file.name
        """The filename."""

        self.data: str = self.file.read()
        """The data."""