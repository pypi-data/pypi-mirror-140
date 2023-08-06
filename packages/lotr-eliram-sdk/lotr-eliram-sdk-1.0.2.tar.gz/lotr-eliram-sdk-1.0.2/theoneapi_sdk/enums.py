from enum import Enum


class FilterType(Enum):
    MATCH = "match"
    NOT_MATCH = "not_match"
    INCLUDE = "include"
    EXCLUDE = "exclude"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    REGEX = "regex"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_THAN_OR_EQUAL = "gte"
