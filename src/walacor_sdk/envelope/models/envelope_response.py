from typing import Any

from walacor_sdk.base.model.base_response_model import BaseResponse
from walacor_sdk.envelope.models.models import ReplayHistoryDetailed


class GetReplayHistoryResponse(BaseResponse[dict[str, Any] | None]):
    pass


class GetReplayHistoryDetailedResponse(BaseResponse[ReplayHistoryDetailed]):
    pass


class PostEnvelopeQueryResponse(BaseResponse[list[dict[str, Any]]]):
    total: int | None = None
    pageNo: int | None = None
    pageSize: int | None = None
    totalPage: int | None = None
