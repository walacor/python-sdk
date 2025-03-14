from walacor_sdk.base_service import BaseService
from walacor_sdk.w_client import W_Client


class UserService(BaseService):
    def __init__(self, client: W_Client) -> None:
        super().__init__(client)

    def get_user(self) -> None:
        pass

    def add_user(self) -> None:
        pass

    def reset_password(self) -> None:
        pass
