class CommandNotFound(Exception):
    """
        The command was not found. 
    """

    def __init__(self, command: str, message: str) -> None:
        self.message: str = message
        """The message of the error."""

        self.command: str = command
        """The command that was not found."""

        super().__init__(message)

class CommandError(Exception):
    """
        The command was not found.
    """
    def __init__(self, message: str, **kwargs) -> None:
        self.message: str = message
        """The message of the error."""

        for key, value in kwargs.items():
            setattr(self, key, value)

        super().__init__(message)