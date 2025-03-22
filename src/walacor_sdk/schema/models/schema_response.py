from pydantic import Field

from walacor_sdk.base.model.base_response_model import BaseResponse
from walacor_sdk.schema.models.models import (
    AutoGenField,
    IndexEntry,
    SchemaDetail,
    SchemaEntry,
    SchemaMetadata,
    SchemaSummary,
    SchemaType,
    SchemaVersionEntry,
)


class SchemaResponse(BaseResponse[list[SchemaType]]):
    pass


class AutoGenFieldsResponse(BaseResponse[dict[str, AutoGenField]]):
    pass


class SchemaListResponse(BaseResponse[list[SchemaEntry]]):
    pass


class SchemaVersionsResponse(BaseResponse[list[SchemaVersionEntry]]):
    pass


class SchemaListVersionsResponse(BaseResponse[list[int]]):
    pass


class SchemaIndexResponse(BaseResponse[list[IndexEntry]]):
    pass


class IndexesByTableNameResponse(BaseResponse[list[IndexEntry]]):
    pass


class CreateSchemaResponse(BaseResponse[SchemaMetadata]):
    pass


class GetSchemaDetailResponse(BaseResponse[SchemaDetail]):
    pass


class GetEnvelopeTypesResponse(BaseResponse[list[int]]):
    pass


class SchemaQueryListResponse(BaseResponse[list[SchemaSummary]]):
    total: int = Field(..., alias="total")
