from walacor_sdk.authentication.auth_service import AuthService
from walacor_sdk.base.facade import Facade
from walacor_sdk.base.w_client import W_Client
from walacor_sdk.data_requests.data_requests_service import DataRequestsService
from walacor_sdk.file_request.file_request_service import FileRequestService
from walacor_sdk.schema.schema_service import SchemaService


class WalacorService:
    """
    A high-level entry point for users to interact with Walacor.
    """

    def __init__(
        self,
        server: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self._client: W_Client | None = None
        self._facade: Facade | None = None

        if server and username and password:
            self.setup(server, username, password)

    def setup(self, server: str, username: str, password: str) -> None:
        """Initial setup or re-setup if credentials / server change."""
        self._client = W_Client(server, username, password)
        self._facade = Facade(self._client)

    def changeServer(self, new_server: str) -> None:
        """Change only the server URL, keep the same credentials."""
        if not self._client:
            raise ValueError("Client not initialized. Call setup() first.")
        self._client.base_url = new_server
        self._facade = Facade(self._client)

    def changeCred(self, new_username: str, new_password: str) -> None:
        """Change only the username/password, keep the same server."""
        if not self._client:
            raise ValueError("Client not initialized. Call setup() first.")
        self._client._username = new_username
        self._client._password = new_password
        self._facade = Facade(self._client)

    def changeAll(self, server: str, username: str, password: str) -> None:
        """Change both server and credentials in one call."""
        self.setup(server, username, password)

    @property
    def auth(self) -> AuthService:
        """Expose AuthService under WalacorService.auth"""
        if not self._facade:
            raise ValueError("Service not set up. Call setup() first.")
        return self._facade.auth

    @property
    def schema(self) -> SchemaService:
        """Expose SchemaService under WalacorService.schema_service"""
        if not self._facade:
            raise ValueError("Service not set up. Call setup() first.")
        return self._facade.schema

    @property
    def file_request(self) -> FileRequestService:
        """Expose FileRequestService under WalacorService.file_request"""
        if not self._facade:
            raise ValueError("Service not set up. Call setup() first.")
        return self._facade.file_request

    @property
    def data_requests(self) -> DataRequestsService:
        """Expose DataRequestsService under WalacorService.data_requests"""
        if not self._facade:
            raise ValueError("Service not set up. Call setup() first.")
        return self._facade.data_requests
