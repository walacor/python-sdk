from walacor_sdk.authentication.auth_service import AuthService
from walacor_sdk.base.w_client import W_Client


class Facade:
    def __init__(
        self, client: W_Client, auth_service_cls: type[AuthService] = AuthService
    ) -> None:
        self._auth: AuthService | None = None
        self._client: W_Client = client
        self.auth_service_cls: type[AuthService] = auth_service_cls

    @property
    def auth(self) -> AuthService:
        if self._auth is None:
            self._auth = self.auth_service_cls(self._client)
        return self._auth
