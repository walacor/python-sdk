import logging

from typing import cast

from pydantic import ValidationError

from walacor_sdk.base.base_service import BaseService
from walacor_sdk.base.w_client import W_Client
from walacor_sdk.schema.models.models import (
    AutoGenField,
    IndexEntry,
    SchemaDetail,
    SchemaEntry,
    SchemaItem,
    SchemaMetadata,
    SchemaSummary,
    SchemaType,
    SchemaVersionEntry,
)
from walacor_sdk.schema.models.schema_request import (
    CreateSchemaRequest,
    SchemaQueryListRequest,
)
from walacor_sdk.schema.models.schema_response import (
    AutoGenFieldsResponse,
    CreateSchemaResponse,
    GetEnvelopeTypesResponse,
    GetSchemaDetailResponse,
    IndexesByTableNameResponse,
    SchemaIndexResponse,
    SchemaListResponse,
    SchemaListVersionsResponse,
    SchemaQueryListResponse,
    SchemaResponse,
    SchemaVersionsResponse,
)
from walacor_sdk.utils.enums import SystemEnvelopeType


class SchemaService(BaseService):
    def __init__(self, client: W_Client) -> None:
        super().__init__(client)

    # region Schema Fields
    def get_data_types(self) -> list[SchemaType]:
        logging.info("Fetching data types...")
        response = self.get("schemas/dataTypes")
        if not response or not response.get("success"):
            logging.error("Failed to fetch data")
            return []

        try:
            parsed_response = SchemaResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("Schema Validation Error: %s", e)
            return []

    def get_platform_auto_generation_fields(self) -> dict[str, AutoGenField]:
        logging.info("Fetching platform auto-generation fields...")
        response = self.get("schemas/systemFields")
        if not response or not response.get("success"):
            logging.error("Failed to fetch platform auto-generation fields")
            return {}

        try:
            parsed_response = AutoGenFieldsResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("AutoGenFields Validation Error: %s", e)
            return {}

        # endregion

    # region Schema UI - Data
    def get_list_with_latest_version(self) -> list[SchemaEntry]:
        response = self.get("schemas/versions/latest")
        if not response or not response.get("success"):
            logging.error("Failed to fetch latest schema versions")
            return []

        try:
            parsed_response = SchemaListResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return []

    def get_versions(self) -> list[SchemaVersionEntry]:
        response = self.get("schemas/versions")
        if not response or not response.get("success"):
            # logging.error()
            return []

        try:
            parsed_response = SchemaVersionsResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return []

    def get_versions_for_ETId(self, ETId: int) -> list[int]:
        response = self.get(f"schemas/envelopeTypes/{ETId}/versions")
        if not response or not response.get("success"):
            # logging.error()
            return []
        try:
            parsed_response = SchemaListVersionsResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return []

    # endregion

    # region Schema UI - Index

    def get_indexes(self, ETId: SystemEnvelopeType | int | str) -> list[IndexEntry]:

        if isinstance(ETId, SystemEnvelopeType):
            etid_value = str(ETId.value)
        else:
            etid_value = str(ETId)

        header = {"ETId": etid_value}
        response = self.get("schemas/envelopeTypes/15/indexes", header)

        try:
            parsed_response = SchemaIndexResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return []

    def get_indexes_by_table_name(self, tableName: str) -> list[IndexEntry]:
        response = self.get(
            f"schemas/envelopeTypes/15/indexesByTableName?tableName={tableName}"
        )

        try:
            parsed_response = IndexesByTableNameResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return []

    # endregion

    # region Add Schema
    def create_schema(self, request: CreateSchemaRequest) -> SchemaMetadata | None:
        headers = {"ETId": "50", "SV": "1"}
        response = self.post("schemas/", json=request.dict(), headers=headers)

        try:
            parsed_response = CreateSchemaResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return None

    # endregion

    # region Schema Details

    def get_schema_details_with_ETId(self, ETId: int) -> SchemaDetail | None:
        headers = {"ETId": f"{ETId}"}
        response = self.get(f"schemas/envelopeTypes/{ETId}/details", headers=headers)

        try:
            response = GetSchemaDetailResponse(**response)
            return cast(SchemaDetail, response.data)
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return None

    def get_envelope_types(self) -> list[int] | None:
        response = self.get("schemas/envelopeTypes")

        try:
            response = GetEnvelopeTypesResponse(**response)
            return cast(list[int], response.data)
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return None

    def get_details_by_id(self, Id: str) -> SchemaDetail | None:
        response = self.get(f"schemas/{Id}")

        try:
            response = GetSchemaDetailResponse(**response)
            return cast(SchemaDetail, response.data)
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return None

    def get_list(self) -> list[SchemaItem] | None:
        response = self.get("schemas")

        try:
            response = SchemaListResponse(**response)
            return cast(list[SchemaItem], response.data)
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return None

    def get_schema_list(
        self, schemaQueryListRequest: SchemaQueryListRequest
    ) -> list[SchemaSummary] | None:
        response = self.get(
            "schemas/schemaList",
            params=schemaQueryListRequest.model_dump(exclude_none=True),
        )

        try:
            parsed_response = SchemaQueryListResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return None

    # endregion
