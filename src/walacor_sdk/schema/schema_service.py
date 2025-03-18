import logging

from pydantic import ValidationError

from walacor_sdk.base.base_service import BaseService
from walacor_sdk.base.w_client import W_Client
from walacor_sdk.schema.models.field_models import AutoGenField, SchemaType
from walacor_sdk.schema.models.schema_response import (
    AutoGenFieldsResponse,
    SchemaResponse,
)
from walacor_sdk.utils.enums import RequestTypeEnum


class SchemaService(BaseService):
    def __init__(self, client: W_Client) -> None:
        super().__init__(client)

    # region Schema Fields
    def getDataTypes(self) -> list[SchemaType]:
        logging.info("Fetching data types...")
        response = self.client.request(RequestTypeEnum.GET, "schemas/dataTypes")

        if not response or not response.get("success"):
            logging.error("Failed to fetch data")
            return []

        try:
            parsed_response = SchemaResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("Schema Validation Error: %c", e)
            return []

    def getPlatformAutoGenerationFields(self) -> dict[str, AutoGenField]:
        logging.info("Fetching platform auto-generation fields...")
        response = self.client.request(RequestTypeEnum.GET, "schemas/systemFields")

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
