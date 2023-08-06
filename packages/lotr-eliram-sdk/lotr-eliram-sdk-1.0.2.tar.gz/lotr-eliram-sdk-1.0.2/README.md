# LotR-Eliram-SDK - Python Client for The One API

## Description
Using Python and you want to access [The One API], your in luck.

The python client for the-one-api provides access to the following endpoints
- book
- chapter
- character
- movie
- quote

## Requirements
- Python 3.8 or higher
- the-one-api access key

## Installation

> pip install lotr-eliram-sdk

## Usage
this example uses the Book API with an access key (token)

``` python
 import theoneapi_sdk;
 client = theoneapi_sdk.Client(token="<YourToken>");
 books = client.book.list()

```

this example uses the character API with a filter
``` python
 import theoneapi_sdk;
 client = theoneapi_sdk.Client(token="<YourToken>");
 from theoneapi_sdk.enums import FilterType
 filter = theoneapi_sdk.Filter("race", "Hobbit", FilterType.MATCH)
 hobbits = client.character.list(filters=[filter])

```

## Testing the project

``` bash
# Install nox
$ pip install nox

# run tests
$ export THE_ONE_TOKEN="<YourToken>"
$ nox
```


## Open Issues and Missing Code:
- Tests tests tests...
- Dedicated Exceptions
- Request Timeout and Retry
- More robust filters and filters validation
- Get next page easier implementation
- Docs and auto generated docs
- Auto increment version on build
- Support more python versions


[The One API]:  https://the-one-api
