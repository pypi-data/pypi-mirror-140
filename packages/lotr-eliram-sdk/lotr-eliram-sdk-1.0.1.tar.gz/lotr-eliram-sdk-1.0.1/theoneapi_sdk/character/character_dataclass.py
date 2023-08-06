from dataclasses import dataclass
from typing import Dict, List

@dataclass
class CharacterData:
    """
    Character Data Class
    """
    id: str
    height: str
    race: str
    gender: str
    birth: str
    spouse: str
    death: str
    realm: str
    hair: str
    name: str
    wikiUrl: str

    def __init__(self, character_dict: Dict[str, str]):
        "Get Character from dict"
        self.id = character_dict['_id']
        self.height = character_dict['height']
        self.race = character_dict['race']
        self.gender = character_dict['gender']
        self.birth = character_dict['birth']
        self.spouse = character_dict['spouse']
        self.death = character_dict['death']
        self.realm = character_dict['realm']
        self.hair = character_dict['hair']
        self.name = character_dict['name']
        self.wikiUrl = character_dict['wikiUrl']

@dataclass
class CharacterDataList:
    """
    Character Data List Class
    """
    characters: List[CharacterData]
    total: int
    limit: int
    page: int
    pages: int
    has_more: bool

    def __init__(self, character_list_dict: Dict[str, str]):
        "Get Character List from dict"
        self.characters = [CharacterData(character_dict) for character_dict in character_list_dict['docs']]
        self.total = int(character_list_dict['total'])
        self.limit = int(character_list_dict['limit'])
        self.page = int(character_list_dict['page'])
        self.pages = int(character_list_dict['pages'])
        self.has_more=int(character_list_dict['page']) < int(character_list_dict['pages'])
