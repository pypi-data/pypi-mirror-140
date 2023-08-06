"""Handle the chapter of the API."""

from typing import TYPE_CHECKING, List
from theoneapi_sdk.chapter.chapter_dataclass import ChapterData, ChapterListData

if TYPE_CHECKING:
    from theoneapi_sdk.request_handler import RequestHandler
    from theoneapi_sdk.filter import Filter


class Chapter:
    """Handle the chapter endpoints."""

    def __init__(self, request_handler: 'RequestHandler'):
        """Initialize the class."""
        self._request_handler = request_handler

    def list(self, page: int = 1, limit: int = 100, filters: List["Filter"] = [], **kwargs) -> "ChapterListData":
        """Get a list of chapters.
        """
        return ChapterListData(self._request_handler._get(f"chapter?page={page}&limit={limit}", filters=filters, **kwargs))

    def chapter(self, chapter_id: str) -> ChapterData:
        """Get a chapter.
        """
        return ChapterData(self._request_handler._get(f"chapter/{chapter_id}")['docs'][0])
