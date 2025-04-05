from walacor_sdk.base.model.base_response_model import BaseResponse
from walacor_sdk.data_requests.models.models import (
    SubmissionResult,
)


class SingleDataRequestResponse(BaseResponse[SubmissionResult]):
    pass


class GetAllRecordsResponse(BaseResponse[list[str]]):
    pass


class GetSingleRecordResponse(BaseResponse[list[str]]):
    pass


class GetComplexQueryResponse(BaseResponse[list[str]]):
    Total: int


class QueryApiResponse(BaseResponse[list[str]]):
    pass


class QueryApiAggregateResponse(BaseResponse[list[str]]):
    Total: int


class GetComplexQMLQueryResponse(BaseResponse[list[str]]):
    Total: int
