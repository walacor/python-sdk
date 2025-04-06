from typing import Any

from pydantic import Field

from walacor_sdk.base.model.base_response_model import BaseResponse
from walacor_sdk.data_requests.models.models import (
    SubmissionResult,
)


class SingleDataRequestResponse(BaseResponse[SubmissionResult]):
    pass


class GetAllRecordsResponse(BaseResponse[list[dict[str, Any]]]):
    pass


class GetSingleRecordResponse(BaseResponse[list[dict[str, Any]]]):
    pass


class GetComplexQueryResponse(BaseResponse[list[dict[str, str]]]):
    Total: int = Field(..., alias="total")


class QueryApiResponse(BaseResponse[list[str]]):
    pass


class QueryApiAggregateResponse(BaseResponse[list[dict[str, str]]]):
    Total: int = Field(..., alias="total")


class GetComplexQMLQueryResponse(BaseResponse[list[dict[str, str]]]):
    Total: int = Field(..., alias="total")
