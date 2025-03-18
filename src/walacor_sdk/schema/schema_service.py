import logging

from pydantic import ValidationError

from walacor_sdk.base.base_service import BaseService
from walacor_sdk.base.w_client import W_Client
from walacor_sdk.schema.models.field_models import SchemaType
from walacor_sdk.schema.models.schema_response import SchemaResponse


class SchemaService(BaseService):
    def __init__(self, client: W_Client) -> None:
        super().__init__(client)

    # region Schema Fields
    def getDataTypes(self) -> list[SchemaType]:
        logging.info("Fetching data types...")
        response = self.client.request("GET", "schemas/dataTypes")

        if not response or not response.get("success"):
            logging.error("Failed to fetch data")
            return []

        try:
            schema_response = SchemaResponse(**response)
            return schema_response.data
        except ValidationError as e:
            logging.error("Schema Validation Error: %c", e)

            return []

    # endregion
