from dataclasses import dataclass
from typing import Dict, List

@dataclass
class BookData:
    id: str
    name: str

    def __init__(self, book_dict: Dict[str, str]):
        self.id = book_dict['_id']
        self.name = book_dict['name']


@dataclass
class BookList:
    """List of books"""
    books: List[BookData]
    total: int
    limit: int
    page: int
    pages: int
    has_more: bool

    def __init__(self, book_list_dict: Dict[str, str]):
        self.books = [BookData(book_dict) for book_dict in book_list_dict['docs']]
        self.total = int(book_list_dict['total'])
        self.limit = int(book_list_dict['limit'])
        self.page = int(book_list_dict['page'])
        self.pages = int(book_list_dict['pages'])
        self.has_more = book_list_dict['pages'] > book_list_dict['page']
