"""Handle the charater endpoint."""
from typing import TYPE_CHECKING, List
from theoneapi_sdk.character.character_dataclass import CharacterData, CharacterDataList
from theoneapi_sdk.quote.quote_dataclass import QuotesList

if TYPE_CHECKING:
    from theoneapi_sdk.request_handler import RequestHandler
    from theoneapi_sdk.filter import Filter


class Character:
    """Handle the charater endpoint."""

    def __init__(self, request_handler: "RequestHandler"):
        self._request_handler = request_handler

    def list(self, page: int = 1, limit: int = 100, filters: List["Filter"] = [], **kwargs) -> "CharacterDataList":
        """Get a list of charaters.
        """
        return CharacterDataList(self._request_handler._get(f"character?page={page}&limit={limit}", filters=filters, **kwargs))
    
    def charater(self, charater_id: int) -> CharacterData:
        """Get a charater by id.
        """
        return CharacterData(self._request_handler._get(f"character/{charater_id}")["docs"][0])

    def charater_quotes(self, charater_id: int, page: int = 1, limit: int = 100, filters: List["Filter"] = [], **kwargs) -> "QuotesList":
        """Get a list of quotes for a charater.
        """
        return QuotesList(self._request_handler._get(f"character/{charater_id}/quote?page={page}&limit={limit}", filters=filters, **kwargs))

