from typing import Any

import requests


class W_Client:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url: str = base_url
        self.username: str = username
        self.password: str = password
        self.token: str | None = None

    def authenticate(self) -> None:
        """Authenticate and store token."""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"userName": self.username, "password": self.password},
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            self.token = response.json().get("api_token")
        else:
            raise Exception("Authentication failed")

    def request(self, method: str, endpoint: str, **kwargs: Any) -> requests.Response:
        """Make an API request, handling authentication manually."""
        if not self.token:
            self.authenticate()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        headers["Content-Type"] = "application/json"

        response = requests.request(
            method, f"{self.base_url}/{endpoint}", headers=headers, **kwargs
        )

        if response.status_code == 401:
            # Re-authenticate if the token has expired
            self.authenticate()
            headers["Authorization"] = f"Bearer {self.token}"
            response = requests.request(
                method, f"{self.base_url}/{endpoint}", headers=headers, **kwargs
            )

        return response
