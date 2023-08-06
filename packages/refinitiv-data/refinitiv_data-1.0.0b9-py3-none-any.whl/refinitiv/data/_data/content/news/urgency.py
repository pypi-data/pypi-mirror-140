__all__ = ["Urgency"]

from enum import Enum, unique


@unique
class Urgency(Enum):
    Hot = 1
    Exceptional = 2
    Regular = 3
    Unknown = 4

    @staticmethod
    def convert_to_enum(s):
        if isinstance(s, str):
            pass
