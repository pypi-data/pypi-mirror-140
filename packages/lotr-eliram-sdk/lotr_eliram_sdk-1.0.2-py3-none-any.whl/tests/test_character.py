import pytest
import os
import theoneapi_sdk
from theoneapi_sdk.client import _DEFUALT_URL
from theoneapi_sdk.character.character_dataclass import CharacterDataList


@pytest.fixture
def client():
    token = os.environ.get('THE_ONE_TOKEN')
    return theoneapi_sdk.Client(token)


def test_get_list(requests_mock, client):
    response_dict = {
        "docs": [
            {
                "_id": "5cd99d4bde30eff6ebccfbbe",
                "height": "",
                "race": "Human",
                "gender": "Female",
                "birth": "",
                "spouse": "Belemir",
                "death": "",
                "realm": "",
                "hair": "",
                "name": "Adanel",
                "wikiUrl": "http://lotr.wikia.com//wiki/Adanel"
            },
            {
                "_id": "5cd99d4bde30eff6ebccfbbf",
                "height": "",
                "race": "Human",
                "gender": "Male",
                "birth": "Before ,TA 1944",
                "spouse": "",
                "death": "Late ,Third Age",
                "realm": "",
                "hair": "",
                "name": "Adrahil I",
                "wikiUrl": "http://lotr.wikia.com//wiki/Adrahil_I"
            },
            {
                "_id": "5cd99d4bde30eff6ebccfbc0",
                "height": "",
                "race": "Human",
                "gender": "Male",
                "birth": "TA 2917",
                "spouse": "Unnamed wife",
                "death": "TA 3010",
                "realm": "",
                "hair": "",
                "name": "Adrahil II",
                "wikiUrl": "http://lotr.wikia.com//wiki/Adrahil_II"
            },
            {
                "_id": "5cd99d4bde30eff6ebccfbc1",
                "height": "",
                "race": "Elf",
                "gender": "Male",
                "birth": "YT during the ,Noontide of Valinor",
                "spouse": "Loved ,Andreth but remained unmarried",
                "death": "FA 455",
                "realm": "",
                "hair": "Golden",
                "name": "Aegnor",
                "wikiUrl": "http://lotr.wikia.com//wiki/Aegnor"
            },
            {
                "_id": "5cd99d4bde30eff6ebccfbc2",
                "height": "",
                "race": "Human",
                "gender": "Female",
                "birth": "Mid ,First Age",
                "spouse": "Brodda",
                "death": "FA 495",
                "realm": "",
                "hair": "",
                "name": "Aerin",
                "wikiUrl": "http://lotr.wikia.com//wiki/Aerin"
            }
        ],
        "total": 933,
        "limit": 5,
        "page": 1,
        "pages": 187
    }

    expected_response = CharacterDataList(response_dict)

    requests_mock.get(f"{_DEFUALT_URL}character?page=1&limit=5", json=response_dict)

    characters = client.character.list(limit=5, page=1)

    assert len(characters.characters) == 5
    assert characters.total == 933
    assert characters.limit == 5
    assert characters.page == 1
    assert characters.pages == 187
    assert expected_response == characters
