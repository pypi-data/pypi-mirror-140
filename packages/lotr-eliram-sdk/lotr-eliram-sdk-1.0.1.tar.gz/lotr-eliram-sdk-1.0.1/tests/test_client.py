"""Test for the client module."""

import pytest
import theoneapi_sdk


def test_missing_token_client_init():
    """Test the client init."""
    with pytest.raises(ValueError) as excinfo:
        theoneapi_sdk.Client()
    assert str(excinfo.value) == "Token is required."
