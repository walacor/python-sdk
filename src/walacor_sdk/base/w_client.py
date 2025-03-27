from typing import Any

import requests


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

    def authenticate(self) -> None:
        """Authenticate with the Walacor API and store the token internally."""
        response = requests.post(
            f"{self._base_url}/auth/login",
            json={"userName": self._username, "password": self._password},
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        if response.status_code == 200:
            self._token = response.json().get("api_token")
            if not self._token:
                raise AuthenticationError("No api_token in response")
        else:
            raise AuthenticationError(
                f"Authentication failed with status code {response.status_code}"
            )

    def request(
        self,
        method: str,
        endpoint: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Make an API request using stored token and optional custom headers."""
        if not self._token:
            self.authenticate()

        request_headers = self.get_default_headers()
        if headers:
            request_headers.update(headers)

        response = requests.request(
            method,
            f"{self._base_url}/{endpoint}",
            headers=request_headers,
            timeout=5,
            **kwargs,
        )

        if response.status_code == 401:
            self.authenticate()
            if self._token is not None:
                request_headers["Authorization"] = self._token
            response = requests.request(
                method,
                f"{self._base_url}/{endpoint}",
                headers=request_headers,
                timeout=5,
                **kwargs,
            )
        return response

    def get_default_headers(self) -> dict[str, str]:
        """Generate default headers with authentication token."""
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = self._token
        return headers

    @property
    def token(self) -> str | None:
        """Read-only property for the token, if needed externally."""
        return self._token
