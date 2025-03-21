from walacor_sdk.base.base_service import BaseService
from walacor_sdk.base.w_client import W_Client


class AuthService(BaseService):
    def __init__(self, client: W_Client) -> None:
        super().__init__(client)

    def login(self) -> None:
        self.client.authenticate()
