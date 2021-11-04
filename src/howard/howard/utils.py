"""Utils that can be useful throughout howard app"""
from enum import Enum


class StrEnum(str, Enum):
    """String Enum."""

    def __str__(self):
        return f"{self.value}"
