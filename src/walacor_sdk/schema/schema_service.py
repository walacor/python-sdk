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
    SchemaQueryList,
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
    GetSchemaListResponse,
    IndexesByTableNameResponse,
    SchemaIndexResponse,
    SchemaListResponse,
    SchemaListVersionsResponse,
    SchemaQueryListResponse,
    SchemaResponse,
    SchemaVersionsResponse,
)
from walacor_sdk.utils.enums import SystemEnvelopeType
from walacor_sdk.utils.logger import get_logger

logging = get_logger(__name__)


class SchemaService(BaseService):
    def __init__(self, client: W_Client) -> None:
        super().__init__(client)

    # region Schema Fields
    def get_data_types(self) -> list[SchemaType]:
        """Fetch list of platform-wide supported data types.

        Returns:
            List of SchemaType objects or an empty list on failure.
        """
        logging.info("Fetching data types...")
        response = self._get("schemas/dataTypes")
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
        """Fetch auto-generated system fields used by the platform.

        Returns:
            Dictionary mapping field names to AutoGenField metadata.
        """
        logging.info("Fetching platform auto-generation fields...")
        response = self._get("schemas/systemFields")
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
        """Get latest versioned schema entries.

        Returns:
            List of SchemaEntry objects representing the latest schema version.
        """
        response = self._get("schemas/versions/latest")
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
        """Retrieve all schema version entries.

        Returns:
            List of SchemaVersionEntry records.
        """
        response = self._get("schemas/versions")
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
        """Fetch all available version numbers for a given ETId.

        Args:
            ETId: Envelope-type ID for the schema.

        Returns:
            List of version numbers.
        """

        response = self._get(f"schemas/envelopeTypes/{ETId}/versions")
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
        """Retrieve index metadata for a given ETId.

        Args:
            ETId: Can be a SystemEnvelopeType enum, string, or int.

        Returns:
            List of IndexEntry definitions.
        """
        if isinstance(ETId, SystemEnvelopeType):
            etid_value = str(ETId.value)
        else:
            etid_value = str(ETId)

        header = {"ETId": etid_value}
        response = self._get("schemas/envelopeTypes/15/indexes", header)

        if not response or not response.get("success"):
            logging.error("Failed to fetch schema indexes")
            return []
        try:
            parsed_response = SchemaIndexResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return []

    def get_indexes_by_table_name(self, tableName: str) -> list[IndexEntry]:
        """Retrieve index metadata using a table name.

        Args:
            tableName: Logical name of the database table.

        Returns:
            List of IndexEntry objects or empty list on error.
        """
        response = self._get(
            f"schemas/envelopeTypes/15/indexesByTableName?tableName={tableName}"
        )
        if not response or not response.get("success"):
            logging.error("Failed to fetch indexes by table name")
            return []

        try:
            parsed_response = IndexesByTableNameResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return []

    # endregion

    # region Add Schema
    def create_schema(self, request: CreateSchemaRequest) -> SchemaMetadata | None:
        """Submit a new schema creation request.

        Args:
            request: Payload for schema creation.

        Returns:
            SchemaMetadata object if creation is successful, otherwise None.
        """
        headers = {"ETId": "50", "SV": "1"}
        response = self._post("schemas/", json=request.model_dump(), headers=headers)
        if not response or not response.get("success"):
            logging.error("Failed to create schema")
            return None
        try:
            parsed_response = CreateSchemaResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return None

    # endregion

    # region Schema Details
    def get_schema_details_with_ETId(self, ETId: int) -> SchemaDetail | None:
        """Fetch full schema details for a given ETId.

        Args:
            ETId: Envelope-type ID.

        Returns:
            SchemaDetail object or None if not found or invalid.
        """
        headers = {"ETId": f"{ETId}"}
        response = self._get(f"schemas/envelopeTypes/{ETId}/details", headers=headers)

        if not response or not response.get("success"):
            logging.error("Failed to fetch schema details")
            return None

        try:
            response = GetSchemaDetailResponse(**response)
            return cast(SchemaDetail, response.data)
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return None

    def get_envelope_types(self) -> list[int] | None:
        """List all available envelope-type identifiers.

        Returns:
            List of ETId integers or None on failure.
        """
        response = self._get("schemas/envelopeTypes")

        if not response or not response.get("success"):
            logging.error("Failed to fetch schema details")
            return None

        try:
            response = GetEnvelopeTypesResponse(**response)
            return cast(list[int], response.data)
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return None

    def get_details_by_id(self, Id: str) -> SchemaDetail | None:
        """Get schema detail by unique schema ID.

        Args:
            Id: Unique schema identifier (UUID).

        Returns:
            SchemaDetail or None.
        """
        response = self._get(f"schemas/{Id}")

        if not response or not response.get("success"):
            logging.error("Failed to fetch schema details")
            return None

        try:
            response = GetSchemaDetailResponse(**response)
            return cast(SchemaDetail, response.data)
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return None

    def get_list_schema_items(self) -> list[SchemaItem] | None:
        """Retrieve a flat list of all schemas (minimal summary).

        Returns:
            List of SchemaItem objects or None.
        """
        response = self._get("schemas")

        if not response or not response.get("success"):
            logging.error("Failed to fetch schema details")
            return None

        try:
            response = GetSchemaListResponse(**response)
            return cast(list[SchemaItem], response.data)
        except ValidationError as e:
            logging.error("SchemaListResponse Validation Error: %s", e)
            return None

    def get_schema_query_schema_items(
        self, schemaQueryListRequest: SchemaQueryListRequest
    ) -> SchemaQueryList | None:
        """Query for schemas using advanced filters.

        Args:
            schemaQueryListRequest: Filter request object with optional params.

        Returns:
            SchemaQueryList containing data and total count, or None.
        """
        response = self._get(
            "schemas/schemaList",
            params=schemaQueryListRequest.model_dump(exclude_none=True),
        )

        if not response or not response.get("success"):
            logging.error("Failed to fetch schema details")
            return None

        try:
            parsed_response = SchemaQueryListResponse(**response)
            data = parsed_response.data
            total = parsed_response.total
            return SchemaQueryList(data=data, total=total)
        except ValidationError as e:
            logging.error("SchemaQueryList Validation Error: %s", e)
            return None

    # endregion
