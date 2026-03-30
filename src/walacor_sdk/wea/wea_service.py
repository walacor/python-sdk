from pydantic import ValidationError

from walacor_sdk.base.base_service import BaseService
from walacor_sdk.base.w_client import W_Client
from walacor_sdk.utils.logger import get_logger
from walacor_sdk.wea.models.models import (
    BlockchainInfo,
    BlockInfoByHeight,
    BlockTransactionsDetailed,
    BlockTransactionsRangeData,
)
from walacor_sdk.wea.models.wea_response import (
    BlockchainInfoResponse,
    BlockInfoByHeightResponse,
    BlockTransactionsDetailedResponse,
    BlockTransactionsRangeResponse,
)

logger = get_logger(__name__)


class WeaService(BaseService):
    def __init__(self, client: W_Client) -> None:
        super().__init__(client)

    def get_blockchain_info(self) -> BlockchainInfo | None:
        logger.info("Fetching blockchain info...")
        raw = self._get("blockchain/chain")

        response = self._handle_response(raw, action="get_blockchain_info")
        if response is None:
            return None

        try:
            parsed_response = BlockchainInfoResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logger.error(
                "BlockchainInfoResponse Validation Error: %s; raw=%s",
                e,
                response,
            )
            return None

    def get_block_info_by_height(self, height: int) -> BlockInfoByHeight | None:
        logger.info("Fetching block info by height...")
        query_params = {"height": height}
        raw = self._get("blockchain/block", params=query_params)

        response = self._handle_response(raw, action="get_block_info_by_height")
        if response is None:
            return None

        try:
            parsed_response = BlockInfoByHeightResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logger.error(
                "BlockInfoByHeightResponse Validation Error: %s; raw=%s",
                e,
                response,
            )
            return None

    def get_block_transaction_by_height(
        self, height: int
    ) -> BlockTransactionsDetailed | None:
        logger.info("Fetching block transaction by height...")
        query_params = {"height": height}
        raw = self._get("blockchain/block/transactions", params=query_params)

        response = self._handle_response(raw, action="get_block_transaction_by_height")
        if response is None:
            return None

        try:
            parsed_response = BlockTransactionsDetailedResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logger.error(
                "BlockTransactionsDetailedResponse Validation Error: %s; raw=%s",
                e,
                response,
            )
            return None

    def get_block_transaction_by_range(
        self, start_height: int, end_height: int
    ) -> BlockTransactionsRangeData | None:
        logger.info("Fetching block transaction by range...")
        query_params = {"fromHeight": start_height, "toHeight": end_height}
        raw = self._get("blockchain/blocks/transactions/range", params=query_params)

        response = self._handle_response(raw, action="get_block_transaction_by_range")
        if response is None:
            return None

        try:
            parsed_response = BlockTransactionsRangeResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logger.error(
                "BlockTransactionsRangeResponse Validation Error: %s; raw=%s",
                e,
                response,
            )
            return None
