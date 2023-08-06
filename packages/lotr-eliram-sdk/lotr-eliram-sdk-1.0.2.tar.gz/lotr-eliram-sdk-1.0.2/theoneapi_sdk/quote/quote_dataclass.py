
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class QuoteData:
    """Single quote data class"""
    id: str
    dialog: str
    movie_id: str
    character_id: str

    def __init__(self, quote_dict: Dict[str, str]):
        """Get quote from dict"""
        self.id=quote_dict['_id']
        self.dialog=quote_dict['dialog']
        self.movie_id=quote_dict['movie']
        self.character_id=quote_dict['character']

@dataclass
class QuotesList:
    """List of quotes data class"""
    quotes: List[QuoteData]
    total: int
    limit: int
    page: int
    pages: int
    has_more: bool


    def __init__(self, quotes_list_dict: Dict[str, str]):
        """Get quotes list from dict"""
        self.quotes=[QuoteData(quote_dict) for quote_dict in quotes_list_dict['docs']]
        self.total=int(quotes_list_dict['total'])
        self.limit=int(quotes_list_dict['limit'])
        self.page=int(quotes_list_dict['page'])
        self.pages=int(quotes_list_dict['pages'])
        self.has_more=int(quotes_list_dict['page']) < int(quotes_list_dict['pages'])
