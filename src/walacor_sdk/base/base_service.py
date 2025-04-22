from abc import ABC
from typing import Any

from walacor_sdk.base.w_client import W_Client
from walacor_sdk.utils.enums import RequestType
from walacor_sdk.utils.global_exception_handler import global_exception_handler


class BaseService(ABC):
    def __init__(self, client: W_Client) -> None:
        self.client = client

    @global_exception_handler
    def _request(
        self,
        method: str,
        endpoint: str,
        headers: dict[str, str] | None = None,
        parse_json: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Internal method to send API requests with optional custom headers."""
        response = self.client.request(method, endpoint, headers=headers, **kwargs)

        if parse_json:
            return response.json()
        return response

    def _get(
        self, endpoint: str, headers: dict[str, str] | None = None, **kwargs: Any
    ) -> Any:
        """Send a GET request with optional custom headers."""
        return self._request(RequestType.GET, endpoint, headers=headers, **kwargs)

    def _post(
        self,
        endpoint: str,
        headers: dict[str, str] | None = None,
        parse_json: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Send a POST request with optional custom headers."""
        return self._request(
            RequestType.POST, endpoint, headers=headers, parse_json=parse_json, **kwargs
        )

    def _put(
        self, endpoint: str, headers: dict[str, str] | None = None, **kwargs: Any
    ) -> Any:
        """Send a PUT request with optional custom headers."""
        return self._request(RequestType.PUT, endpoint, headers=headers, **kwargs)

    def _delete(
        self, endpoint: str, headers: dict[str, str] | None = None, **kwargs: Any
    ) -> Any:
        """Send a DELETE request with optional custom headers."""
        return self._request(RequestType.DELETE, endpoint, headers=headers, **kwargs)
