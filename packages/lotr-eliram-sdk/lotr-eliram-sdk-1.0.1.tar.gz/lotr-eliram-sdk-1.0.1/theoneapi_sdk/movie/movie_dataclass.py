from dataclasses import dataclass
from typing import Dict, List

@dataclass
class MovieData:
    """Single movie data class"""
    id: str
    runtime_in_minutes: int
    budget_in_millions: int
    box_office_in_millions: int
    academy_awards_wins: int
    academy_awards_nominated: int
    rotten_tomatoes_score: int

    def __init__(self, movie_dict: Dict[str, str]):
        """Get movie from dict"""
        self.id=movie_dict['_id']
        self.runtime_in_minutes=int(movie_dict['runtimeInMinutes'])
        self.budget_in_millions=int(movie_dict['budgetInMillions'])
        self.box_office_in_millions=int(movie_dict['boxOfficeRevenueInMillions'])
        self.academy_awards_wins=int(movie_dict['academyAwardWins'])
        self.academy_awards_nominated=int(movie_dict['academyAwardNominations'])
        self.rotten_tomatoes_score=int(movie_dict['rottenTomatoesScore'])

@dataclass
class MovieList:
    """List of movies data class"""
    movies: List[MovieData]
    total: int
    limit: int
    page: int
    pages: int
    has_more: bool


    def __init__(self, movies_list_dict: Dict[str, str]):
        """Get quotes list from dict"""
        self.movies=[MovieData(movie_dict) for movie_dict in movies_list_dict['docs']]
        self.total=int(movies_list_dict['total'])
        self.limit=int(movies_list_dict['limit'])
        self.page=int(movies_list_dict['page'])
        self.pages=int(movies_list_dict['pages'])
        self.has_more=int(movies_list_dict['page']) < int(movies_list_dict['pages'])
