from walacor_sdk.base.model.base_response_model import BaseResponse
from walacor_sdk.wea.models.models import (
    BlockchainInfo,
    BlockInfoByHeight,
    BlockTransactionsDetailed,
    BlockTransactionsInfo,
    BlockTransactionsRangeData,
)


class BlockchainInfoResponse(BaseResponse[BlockchainInfo]):
    pass


class BlockInfoByHeightResponse(BaseResponse[BlockInfoByHeight]):
    pass


class BlockChainRangeTransactionResponse(BaseResponse[list[BlockTransactionsInfo]]):
    pass


class BlockTransactionsDetailedResponse(BaseResponse[BlockTransactionsDetailed]):
    pass


class BlockTransactionsRangeResponse(BaseResponse[BlockTransactionsRangeData]):
    pass
