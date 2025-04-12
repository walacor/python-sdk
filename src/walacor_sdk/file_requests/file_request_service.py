from walacor_sdk.base.base_service import BaseService
from walacor_sdk.base.w_client import W_Client
from walacor_sdk.utils.logger import get_logger

logger = get_logger(__name__)


class FileRequestService(BaseService):
    def __init__(self, client: W_Client) -> None:
        super().__init__(client)

    def verify(self) -> None:
        pass

    def store(self) -> None:
        pass

    def download(self) -> None:
        pass

    def file_list(self) -> None:
        pass
