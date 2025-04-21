from typing import Annotated, Literal

from pydantic import BaseModel, Field

from walacor_sdk.base.model.base_response_model import BaseResponse
from walacor_sdk.file_request.models.models import (
    DuplicateData,
    FileInfoWrapper,
    FileMetadata,
    StoreFileData,
)


class VerifySuccessResponse(BaseResponse[FileInfoWrapper]):
    success: Literal[True] = True
    message: str


class VerifyDuplicateResponse(BaseModel):
    success: Literal[False] = False
    duplicateData: DuplicateData


class StoreFileResponse(BaseResponse[StoreFileData]):
    pass


class ListFilesResponse(BaseResponse[list[FileMetadata]]):
    total: int


VerifyResponse = Annotated[
    VerifySuccessResponse | VerifyDuplicateResponse,
    Field(discriminator="success"),
]
