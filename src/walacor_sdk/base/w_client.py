from typing import Any

import requests

from walacor_sdk.utils.exceptions import APIConnectionError
from walacor_sdk.utils.global_exception_handler import global_exception_handler


class AuthenticationError(Exception):
    """Raised when authentication fails or token is invalid."""


class W_Client:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self._base_url: str = base_url
        self._username: str = username
        self._password: str = password
        self._token: str | None = None

    @property
    def base_url(self) -> str:
        """Return the current base URL (read-only)."""
        return self._base_url

    @base_url.setter
    def base_url(self, new_url: str) -> None:
        """Update the base URL."""
        self._base_url = new_url

    @global_exception_handler
    def authenticate(self) -> None:
        response = requests.post(
            f"{self._base_url}/auth/login",
            json={"userName": self._username, "password": self._password},
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        response.raise_for_status()
        self._token = response.json().get("api_token")
        if not self._token:
            raise APIConnectionError("Authentication succeeded but no token returned.")

    @global_exception_handler
    def request(
        self,
        method: str,
        endpoint: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Any:
        if not self._token:
            self.authenticate()

        is_file_upload = "files" in kwargs and kwargs["files"] is not None
        content_type = None if is_file_upload else "application/json"

        request_headers = self.get_default_headers(content_type)

        if headers:
            request_headers.update(headers)

        response = requests.request(
            method,
            f"{self._base_url}/{endpoint}",
            headers=request_headers,
            **kwargs,
        )

        if response.status_code == 401:
            self.authenticate()

            if self._token is None:
                raise APIConnectionError(
                    "No token available for authenticated request."
                )
            request_headers["Authorization"] = self._token

            response = requests.request(
                method,
                f"{self._base_url}/{endpoint}",
                headers=request_headers,
                **kwargs,
            )

        if response.status_code == 422:
            return response

        response.raise_for_status()
        return response

    def get_default_headers(
        self, content_type: str | None = "application/json"
    ) -> dict[str, str]:
        headers = {}
        if content_type is not None:
            headers["Content-Type"] = content_type
        if self._token:
            headers["Authorization"] = self._token
        return headers

    @property
    def token(self) -> str | None:
        """Read-only property for the token, if needed externally."""
        return self._token
