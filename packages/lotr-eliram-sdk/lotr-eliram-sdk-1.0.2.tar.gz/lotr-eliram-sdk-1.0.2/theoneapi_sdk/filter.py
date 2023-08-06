"""Filters to use with the OneApi SDK."""

from typing import List, Union
from theoneapi_sdk.enums import FilterType


class Filter:
    """Filter by specific fields."""

    def __init__(self, field: str, value: Union[str, List[str]], type: FilterType):
        """Initialize filter."""
        self.field = field
        self.value = value
        self.type = type


    def get_filter_string(self) -> str:
        """Get filter string."""
        if self.type == FilterType.MATCH:
            return f"{self.field}={self.value}"
        elif self.type == FilterType.NOT_MATCH:
            return f"{self.field}!={self.value}"
        elif self.type == FilterType.EXISTS:
            return f"{self.field}"
        elif self.type == FilterType.NOT_EXISTS:
            return f"!{self.field}"
        elif self.type == FilterType.INCLUDE:
            if isinstance(self.value, list):
                return f"{self.field}={','.join(self.value)}"
            else:
                return f"{self.field}={self.value}"
        elif self.type == FilterType.EXCLUDE:
            if isinstance(self.value, list):
                return f"{self.field}!={','.join(self.value)}"
            else:
                return f"{self.field}!={self.value}"
        elif self.type == FilterType.GREATER_THAN:
            return f"{self.field}>{self.value}"
        elif self.type == FilterType.LESS_THAN:
            return f"{self.field}<{self.value}"
        elif self.type == FilterType.GREATER_THAN_OR_EQUAL:
            return f"{self.field}>={self.value}"
        else:
            raise ValueError("Invalid filter type")




def get_filters_string(filters: List[Filter]) -> str:
    """Get filter string."""
    if len(filters) == 0:
        return ""
    else:
        return "&".join([f.get_filter_string() for f in filters])
