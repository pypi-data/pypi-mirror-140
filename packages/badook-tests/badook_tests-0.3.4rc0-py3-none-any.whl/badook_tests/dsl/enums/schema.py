from enum import Enum


class NameMatch(Enum):
    EXACT = 0
    IGNORE_EXTRA_FEATURES = 1
    IGNORE_MISSING_FEATURES = 2
    IGNORE_MISSING_AND_EXTRA = 3


class TypeMatch(Enum):
    EXACT = 0
    IGNORE_TYPES = 1
