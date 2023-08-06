"""Core client provides access to all the API endpoints."""

from theoneapi_sdk.request_handler import RequestHandler
from theoneapi_sdk.book.book import Book
from theoneapi_sdk.quote.quote import Quote
from theoneapi_sdk.movie.movie import Movie
from theoneapi_sdk.character.character import Character
from theoneapi_sdk.chapter.chapter import Chapter


_DEFUALT_URL: str = "https://the-one-api.dev/v2/"


class Client:
    """Provides access to all of "TheOne" API endpoints."""

    def __init__(self, token: str = None, api_url: str=_DEFUALT_URL):
        """Initialize the client."""

        if not token:
            raise ValueError("Token is required.")

        self.token = token
        self.api_url = api_url
        request_handler = RequestHandler(self.api_url, self.token)
        self._books_api = Book(request_handler)
        self._quotes_api = Quote(request_handler)
        self._movies_api = Movie(request_handler)
        self._characters_api = Character(request_handler)
        self._chapters_api = Chapter(request_handler)

    @property
    def book(self) -> "Book":
        """Provides access to the Books API."""
        return self._books_api


    @property
    def quote(self) -> "Quote":
        """Provides access to the Quotes API."""
        return self._quotes_api

    @property
    def movie(self) -> "Movie":
        """Provides access to the Movies API."""
        return self._movies_api

    @property
    def character(self) -> "Character":
        """Provides access to the Characters API."""
        return self._characters_api

    @property
    def chapter(self) -> "Chapter":
        """Provides access to the Chapters API."""
        return self._chapters_api
