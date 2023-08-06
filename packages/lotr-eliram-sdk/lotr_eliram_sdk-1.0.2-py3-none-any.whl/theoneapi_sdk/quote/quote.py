"""Handle the quote endpoint."""
from typing import TYPE_CHECKING, List
from theoneapi_sdk.quote.quote_dataclass import QuoteData, QuotesList

if TYPE_CHECKING:
    from theoneapi_sdk.request_handler import RequestHandler
    from theoneapi_sdk.filter import Filter


class Quote:
    """Handle the quote endpoint."""

    def __init__(self, request_handler: 'RequestHandler'):
        """Initialize the quote endpoint."""
        self._request_handler = request_handler

    def list(self, page: int = 1, limit: int = 100, filters: List["Filter"] = [], **kwargs) -> "QuotesList":
        """Get a list of quotes.
        """
        return QuotesList(self._request_handler._get(f"quote?page={page}&limit={limit}", filters=filters, **kwargs))

    def quote(self, quote_id: str) -> QuoteData:
        """Get a quote.
        """
        return QuoteData(self._request_handler._get(f"quote/{quote_id}")['docs'][0])
