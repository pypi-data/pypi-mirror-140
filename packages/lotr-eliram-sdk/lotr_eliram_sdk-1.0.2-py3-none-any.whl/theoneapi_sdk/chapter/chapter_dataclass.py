
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ChapterData:
    """Single chapter data class"""
    id: str
    chapter_name: str
    book_id: str

    def __init__(self, chapter_dict: Dict[str, str]):
        """Get chapter from dict"""
        self.id=chapter_dict['_id']
        self.chapter_name=chapter_dict['chapterName']
        self.book_id=chapter_dict['book']

@dataclass
class ChapterListData:
    """List of chapters data class"""
    chapters: List[ChapterData]
    total: int
    limit: int
    page: int
    pages: int
    has_more: bool


    def __init__(self, chapters_list_dict: Dict[str, str]):
        """Get chapters list from dict"""
        self.chapters=[ChapterData(chapter_dict) for chapter_dict in chapters_list_dict['docs']]
        self.total=int(chapters_list_dict['total'])
        self.limit=int(chapters_list_dict['limit'])
        self.page=int(chapters_list_dict['page'])
        self.pages=int(chapters_list_dict['pages'])
        self.has_more=int(chapters_list_dict['page']) < int(chapters_list_dict['pages'])

