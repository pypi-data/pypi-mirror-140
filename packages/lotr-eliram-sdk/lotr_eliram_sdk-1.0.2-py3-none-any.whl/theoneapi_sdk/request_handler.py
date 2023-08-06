"""Handle the request to the OneAPI server."""

from typing import Dict, List, TYPE_CHECKING
import requests
from theoneapi_sdk.filter import get_filters_string

if TYPE_CHECKING:
    from theoneapi_sdk.filter import Filter

class RequestHandler:
    """Handle the request to the OneAPI server."""

    def __init__(self, api_url: str, token: str):
        """Initialize the RequestHandler object."""
        self.api_url = api_url
        self.token = token
        self.session = requests.Session()
        # TODO eliram: add support for timeout

    def _get_headers(self) -> Dict[str, str]:
        """Get the headers for the request."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        return headers

    def _request(self, method: str = "", endpoint: str = "", params: Dict[str,str] = {}, filters: List["Filter"] = [], data: Dict[str, str] = None) -> Dict[str, str]:
        """Make a request to the API."""

        if data is None:
            data = {}
        if not method:
            raise ValueError("Method is required.")
        if not endpoint:
            raise ValueError("Endpoint is required.")

        try:
            if method.lower() == "get":
                response = self.session.get(f"{self.api_url}{endpoint}{self._build_params(params, filters)}", headers=self._get_headers(), params=data)
            elif method.lower() == "post":
                response = self.session.post(f"{self.api_url}{endpoint}", headers=self._get_headers(), json=data)
            elif method.lower() == "put":
                response = self.session.put(f"{self.api_url}{endpoint}", headers=self._get_headers(), json=data)
            elif method.lower() == "delete":
                response = self.session.delete(f"{self.api_url}{endpoint}", headers=self._get_headers(), json=data)
            else:
                raise ValueError("Method is not supported.")

            if response.status_code == 200:
                return response.json()
            else:
                raise ValueError(f"Request failed with status code {response.status_code}")
        #TODO eliram: move to own package error and exception
        except requests.exceptions.Timeout:
            raise ValueError("Request timed out.")
        except Exception as e:
            raise e

    def _get(self, endpoint: str = "", data: Dict[str, str] = {}, **kwargs ) -> Dict[str, str]:
        """Make a GET request to the API."""
        return self._request("get", endpoint, data, **kwargs)

    def _build_params(self, params: Dict[str, str] = {}, filters: List["Filter"] = []) -> str:
        """Build the params for the request."""
        attributes = ""
        if params or filters:
            attributes = "?"
        if params:
            attributes =  "&".join([f"{key}={value}" for key, value in params.items()])
        if filters:
            attributes += "&" + get_filters_string(filters)
        return attributes
