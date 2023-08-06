"""Handle the movie endpoint."""
from typing import TYPE_CHECKING, List
from theoneapi_sdk.movie.movie_dataclass import MovieData, MovieList
from theoneapi_sdk.quote.quote_dataclass import QuotesList

if TYPE_CHECKING:
    from theoneapi_sdk.request_handler import RequestHandler
    from theoneapi_sdk.filter import Filter


class Movie:
    """Handle the movie endpoint."""

    def __init__(self, request_handler: "RequestHandler"):
        self._request_handler = request_handler

    def list(self, page: int = 1, limit: int = 100, filters: List["Filter"] = [], **kwargs) -> "MovieList":
        """Get a list of quotes.
        """
        return MovieList(self._request_handler._get(f"movie?page={page}&limit={limit}", filters=filters, **kwargs))
    
    def movie(self, movie_id: int) -> MovieData:
        """Get a movie by id.
        """
        return MovieData(self._request_handler._get(f"movie/{movie_id}")["docs"][0])

    def movie_quotes(self, movie_id: int, page: int = 1, limit: int = 100, filters: List["Filter"] = [], **kwargs) -> "QuotesList":
        """Get a list of quotes for a movie.
        """
        return QuotesList(self._request_handler._get(f"movie/{movie_id}/quote?page={page}&limit={limit}", filters=filters, **kwargs))
