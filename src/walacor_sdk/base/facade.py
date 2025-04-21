from walacor_sdk.authentication.auth_service import AuthService
from walacor_sdk.base.w_client import W_Client
from walacor_sdk.data_requests.data_requests_service import DataRequestsService
from walacor_sdk.file_request.file_request_service import FileRequestService
from walacor_sdk.schema.schema_service import SchemaService


class Facade:
    def __init__(
        self,
        client: W_Client,
        auth_service_cls: type[AuthService] = AuthService,
        schema_service_cls: type[SchemaService] = SchemaService,
        file_request_service_cls: type[FileRequestService] = FileRequestService,
        data_requests_service_cls: type[DataRequestsService] = DataRequestsService,
    ) -> None:
        self._client: W_Client = client

        self._auth: AuthService | None = None
        self._schema: SchemaService | None = None
        self._file_request: FileRequestService | None = None

        self.auth_service_cls: type[AuthService] = auth_service_cls
        self.schema_service_cls: type[SchemaService] = schema_service_cls
        self.file_request_service_cls: type[FileRequestService] = (
            file_request_service_cls
        )

        self._data_requests: DataRequestsService | None = None
        self.data_requests_service_cls: type[DataRequestsService] = (
            data_requests_service_cls
        )

    @property
    def auth(self) -> AuthService:
        if self._auth is None:
            self._auth = self.auth_service_cls(self._client)
        return self._auth

    @property
    def schema(self) -> SchemaService:
        if self._schema is None:
            self._schema = self.schema_service_cls(self._client)
        return self._schema

    @property
    def file_request(self) -> FileRequestService:
        if self._file_request is None:
            self._file_request = self.file_request_service_cls(self._client)
        return self._file_request

    @property
    def data_requests(self) -> DataRequestsService:
        if self._data_requests is None:
            self._data_requests = self.data_requests_service_cls(self._client)
        return self._data_requests
