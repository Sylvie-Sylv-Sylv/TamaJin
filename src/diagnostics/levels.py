from __future__ import annotations
from enum import Enum


class Level(Enum):
    """
    Log level enum with string values representing the level name.
    Extendable - add more levels by subclassing or extending.
    """

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"
    ASSERT = "ASSERT"

    def __int__(self) -> int:
        """Return numeric priority for filtering."""
        return _LEVEL_PRIORITY.get(self.value, 0)

    @classmethod
    def from_string(cls, name: str) -> Level | None:
        """Get level from string name."""
        try:
            return cls[name.upper()]
        except KeyError:
            return None


# Level priority mapping (higher = more severe)
_LEVEL_PRIORITY = {
    "TRACE": 0,
    "DEBUG": 1,
    "INFO": 2,
    "WARN": 3,
    "ERROR": 4,
    "FATAL": 5,
    "ASSERT": 4,
}
