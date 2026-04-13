from typing import Any

from pydantic import Field

from walacor_sdk.base.model.base_response_model import BaseResponse
from walacor_sdk.envelope.models.models import (
    ReplayHistoryDetailed,
)


class GetReplayHistoryResponse(BaseResponse[dict[str, Any] | None]):
    Total: int = Field(..., alias="total")


class GetReplayHistoryDetailedResponse(BaseResponse[ReplayHistoryDetailed]):
    Total: int = Field(..., alias="total")
