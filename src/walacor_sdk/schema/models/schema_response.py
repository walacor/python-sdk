from walacor_sdk.base.model.base_response_model import BaseResponse
from walacor_sdk.schema.models.models import (
    AutoGenField,
    IndexEntry,
    SchemaEntry,
    SchemaMetadata,
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
