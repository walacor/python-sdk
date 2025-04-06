import json

from typing import Any

from pydantic import ValidationError

from walacor_sdk.base.base_service import BaseService
from walacor_sdk.base.w_client import W_Client
from walacor_sdk.data_requests.models.data_request_response import (
    GetAllRecordsResponse,
    GetComplexQMLQueryResponse,
    GetComplexQueryResponse,
    GetSingleRecordResponse,
    QueryApiAggregateResponse,
    QueryApiResponse,
    SingleDataRequestResponse,
)
from walacor_sdk.data_requests.models.models import (
    ComplexQMLQueryRecords,
    ComplexQueryRecords,
    QueryApiAggregate,
    SubmissionResult,
)
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
        self, listOfJsonRecords: list[dict[str, Any]], ETId: int
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

    # region Update

    def update_single_record_with_UID(
        self, record: dict[str, Any], ETId: int
    ) -> SubmissionResult | None:

        if "UID" not in record:
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

    # region Read
    def get_all(
        self,
        ETId: int,
        pageNumber: int = 0,
        pageSize: int = 0,
        fromSummary: bool = False,
    ) -> list[dict[str, Any]] | None:
        header = {"ETId": str(ETId)}
        query = f"query/get?pageNo={pageNumber}&pageSize={pageSize}&fromSummary={'true' if fromSummary else 'false'}"
        response = self.post(query, headers=header)

        if not response or not response.get("success"):
            logging.error("Failed to fetch all records.")
            return None

        try:
            parsed_response = GetAllRecordsResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("GetAllRecordsResponse Validation Error: %s", e)
            return None

    def get_single_record_by_record_id(
        self, record_id: dict[str, str], ETId: int, fromSummary: bool = False
    ) -> list[dict[str, Any]] | None:
        header = {"ETId": str(ETId)}
        query = f"query/get?fromSummary={'true' if fromSummary else 'false'}"
        response = self.post(query, headers=header, json=record_id)

        if not response or not response.get("success"):
            logging.error("Failed to fetch single record.")
            return None

        try:
            parsed_response = GetSingleRecordResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("GetSingleRecordResponse Validation Error: %s", e)
            return None

    def post_complex_query(
        self, ETId: int, pipeline: list[dict[str, Any]]
    ) -> ComplexQueryRecords | None:
        header = {"ETId": str(ETId)}
        response = self.post("query/getcomplex", headers=header, json=pipeline)

        if not response or not response.get("success"):
            logging.error("Failed to fetch complex query results.")
            return None

        try:
            parsed_response = GetComplexQueryResponse(**response)
            return ComplexQueryRecords(
                Records=parsed_response.data, Total=parsed_response.Total
            )
        except ValidationError as e:
            logging.error("Complex Query Parsing Error: %s", e)
            return None

    def post_query_api(
        self,
        ETId: int,
        payload: dict[str, Any],
        schemaVersion: int = 1,
        pageNumber: int = 1,
        pageSize: int = 0,
    ) -> list[str] | None:
        headers = {"ETId": str(ETId), "SV": str(schemaVersion)}
        query = f"query/get?pageNo={pageNumber}&pageSize={pageSize}"
        response = self.post(query, headers=headers, json=payload)

        if not response or not response.get("success"):
            logging.error("Failed to fetch query results.")
            return None

        try:
            parsed_response = QueryApiResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logging.error("QueryApiResponse Validation Error: %s", e)
            return None

    def post_query_api_aggregate(
        self,
        payload: list[dict[str, Any]],
        ETId: int = 10,
        schemaVersion: int = 1,
        dataVersion: int = 1,
    ) -> QueryApiAggregate | None:
        headers = {
            "ETId": str(ETId),
            "SV": str(schemaVersion),
            "DV": str(dataVersion),
        }
        response = self.post("query/getComplex", headers=headers, json=payload)

        if not response or not response.get("success"):
            logging.error("Failed to fetch query aggregate results.")
            return None

        try:
            parsed_response = QueryApiAggregateResponse(**response)
            return QueryApiAggregate(
                Records=parsed_response.data, Total=parsed_response.Total
            )
        except ValidationError as e:
            logging.error("QueryApiAggregateResponse Validation Error: %s", e)
            return None

    def post_complex_MQL_queries(
        self,
        pipeline: list[dict[str, Any]],
        ETId: int,
    ) -> ComplexQMLQueryRecords | None:
        header = {"ETId": str(ETId)}
        response = self.post("query/getcomplex", headers=header, json=pipeline)

        if not response or not response.get("success"):
            logging.error("Failed to fetch complex MQL query results.")
            return None

        try:
            parsed_response = GetComplexQMLQueryResponse(**response)
            return ComplexQMLQueryRecords(
                Records=parsed_response.data, Total=parsed_response.Total
            )
        except ValidationError as e:
            logging.error("GetComplexQMLQueryResponse Validation Error: %s", e)
            return None


# endregion
