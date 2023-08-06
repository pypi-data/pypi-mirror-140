from ...mixins import EnumMixin
from enum import Enum

class PresenceType(EnumMixin, Enum):
    """
    Enum for the presence type.
    """
    ONLINE = 0
    IDLE = 1
    DND = 2
    OFFLINE = 3

    def __str__(self):
        return self.name
    
    def __int__(self):
        return self.value

class ActivityTypes(EnumMixin, Enum):
    """
    Enum for the activity type.
    """
    PLAYING = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    CUSTOM = 4
    COMPETING = 5

    def __str__(self):
        return self.name
    
    def __int__(self):
        return self.value