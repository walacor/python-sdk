import json

from pydantic import ValidationError

from walacor_sdk.base.base_service import BaseService
from walacor_sdk.base.w_client import W_Client
from walacor_sdk.data_requests.models.data_request_response import (
    SingleDataRequestResponse,
)
from walacor_sdk.data_requests.models.models import SubmissionResult
from walacor_sdk.utils.logger import get_logger

logging = get_logger(__name__)


class DataRequestsService(BaseService):
    def __init__(self, client: W_Client) -> None:
        super().__init__(client)

    # region Insert

    def insert_single_record(
        self, jsonRecord: str, ETId: int
    ) -> SubmissionResult | None:
        record = {"Data": [jsonRecord]}
        header = {"ETId": str(ETId)}
        response = self.post("envelopes/submit", json=record, headers=header)

        if not response or not response.get("success"):
            logging.error("Failed to insert record")
            return None

        try:
            parsed_response = SingleDataRequestResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SingleDataRequestResponse Validation Error: %s", e)
            return None

    def insert_multiple_records(
        self, listOfJsonRecords: list[str], ETId: int
    ) -> SubmissionResult | None:
        records = {"Data": listOfJsonRecords}
        header = {"ETId": str(ETId)}
        response = self.post("envelopes/submit", json=records, headers=header)

        if not response or not response.get("success"):
            logging.error("Failed to insert record")
            return None

        try:
            parsed_response = SingleDataRequestResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SingleDataRequestResponse Validation Error: %s", e)
            return None

    # endregion

    # region Insert

    def update_single_record(self, record: str, ETId: int) -> SubmissionResult | None:
        try:
            parsed_record = json.loads(record)
        except json.JSONDecodeError as e:
            logging.error("Invalid JSON format: %s", e)
            return None

        if "UID" not in parsed_record:
            logging.error("UID is required to update a record")
            return None

        header = {"ETId": str(ETId)}
        response = self.post(
            "envelopes/submit", json={"Data": [record]}, headers=header
        )

        if not response or not response.get("success"):
            logging.error("Failed to insert record")
            return None

        try:
            parsed_response = SingleDataRequestResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SingleDataRequestResponse Validation Error: %s", e)
            return None

    def update_multiple_record(
        self, records: list[str], ETId: int
    ) -> SubmissionResult | None:
        try:
            for record in records:
                parsed_record = json.loads(record)
                if "UID" not in parsed_record:
                    logging.error("UID is required in all records for update")
                    return None
        except json.JSONDecodeError as e:
            logging.error("Invalid JSON in records: %s", e)
            return None

        header = {"ETId": str(ETId)}
        response = self.post("envelopes/submit", json={"Data": records}, headers=header)

        if not response or not response.get("success"):
            logging.error("Failed to insert record")
            return None

        try:
            parsed_response = SingleDataRequestResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("SingleDataRequestResponse Validation Error: %s", e)
            return None

    # endregion
