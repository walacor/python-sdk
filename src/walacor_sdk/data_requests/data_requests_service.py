from walacor_sdk.base.base_service import BaseService
from walacor_sdk.base.w_client import W_Client


class DataRequestsService(BaseService):
    def __init__(self, client: W_Client) -> None:
        super().__init__(client)

    # region Insert

    def insert_single_record(self, record: str, ETId: int) -> None:
        return

    def insert_multiple_records(self) -> None:
        return

    # endregion
