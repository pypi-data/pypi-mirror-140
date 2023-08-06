from enum import Enum


class KeySetType(Enum):
    """Describes the 4 types of KeySets."""

    ALL = "ALL"
    ALL_EXCEPT_SOME = "ALL_EXCEPT_SOME"
    NONE = "NONE"
    SOME = "SOME"
