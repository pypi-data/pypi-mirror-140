"""Handles all the books related requests."""

from typing import TYPE_CHECKING, Dict, List
from theoneapi_sdk.book.book_dataclass import BookData, BookList

if TYPE_CHECKING:
    from theoneapi_sdk.request_handler import RequestHandler
    from theoneapi_sdk.filter import Filter

class Book:
    """Handles all the books related requests."""

    def __init__(self, request_handler: 'RequestHandler'):
        """Initializes the Books class."""
        self._request_handler = request_handler

    def list(self, page: int = 1, limit: int = 100, filters: List["Filter"] = [], **kwargs) -> "BookList":
        """Gets a list of books."""
        return BookList(self._request_handler._get(f"/book?page={page}&limit={limit}", filters=filters, **kwargs))

    def book(self, book_id: str, **kwargs) -> BookData:
        """Gets a book by its ID."""
        return BookData(self._request_handler._get(f"/book/{book_id}", **kwargs)['docs'][0])

    def book_chapters(self, book_id: str, **kwargs) -> Dict[str, str]:
        """Gets a list of chapters for a book."""
        return self._request_handler._get('/book/{}/chapter'.format(book_id), **kwargs)
