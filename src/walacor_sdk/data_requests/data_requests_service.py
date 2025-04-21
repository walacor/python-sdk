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

logger = get_logger(__name__)


class DataRequestsService(BaseService):
    def __init__(self, client: W_Client) -> None:
        super().__init__(client)

    # ------------------------------------------------------------------ INSERT

    def insert_single_record(
        self, jsonRecord: str, ETId: int
    ) -> SubmissionResult | None:
        """Insert a **single** row.

        Args:
            jsonRecord: Raw *JSON string* representing one record that matches the
                destination schema.
            ETId: Envelope‑type ID of the destination table.

        Returns:
            A :class:`~walacor_sdk.data_requests.models.models.SubmissionResult` if
            the backend confirms success; otherwise ``None``.
        """
        record = {"Data": [jsonRecord]}
        header = {"ETId": str(ETId)}
        response = self._post("envelopes/submit", json=record, headers=header)

        if not response or not response.get("success"):
            logger.error("Failed to insert record")
            return None

        try:
            parsed_response = SingleDataRequestResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logger.error("SingleDataRequestResponse Validation Error: %s", e)
            return None

    def insert_multiple_records(
        self, listOfJsonRecords: list[dict[str, Any]], ETId: int
    ) -> SubmissionResult | None:
        """Bulk‑insert *many* fully‑decoded records.

        Args:
            listOfJsonRecords: List of dictionaries already parsed from JSON.
            ETId: Target envelope‑type ID.

        Returns:
            :class:`SubmissionResult` or ``None`` on failure.
        """
        records = {"Data": listOfJsonRecords}
        header = {"ETId": str(ETId)}
        response = self._post("envelopes/submit", json=records, headers=header)

        if not response or not response.get("success"):
            logger.error("Failed to insert record")
            return None

        try:
            parsed_response = SingleDataRequestResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logger.error("SingleDataRequestResponse Validation Error: %s", e)
            return None

    # ------------------------------------------------------------------ UPDATE

    def update_single_record_with_UID(
        self, record: dict[str, Any], ETId: int
    ) -> SubmissionResult | None:
        """Replace **one** existing row.

        ``record`` **must** contain its immutable ``UID`` otherwise the backend
        will reject the update.

        Args:
            record: Row with a ``UID`` field plus updated columns.
            ETId: Envelope‑type ID of the table being updated.

        Returns:
            :class:`SubmissionResult` when successful, ``None`` otherwise.
        """

        if "UID" not in record:
            logger.error("UID is required to update a record")
            return None

        header = {"ETId": str(ETId)}
        response = self._post(
            "envelopes/submit", json={"Data": [record]}, headers=header
        )

        if not response or not response.get("success"):
            logger.error("Failed to update record")
            return None

        try:
            parsed_response = SingleDataRequestResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logger.error("SingleDataRequestResponse Validation Error: %s", e)
            return None

    def update_multiple_record(
        self, records: list[str], ETId: int
    ) -> SubmissionResult | None:
        """Bulk update – each element is a JSON *string* containing a ``UID``.

        Args:
            records: List of JSON strings. Each must include a ``UID`` key.
            ETId: Envelope‑type ID for the target table.

        Returns:
            :class:`SubmissionResult` if the batch succeeds, else ``None``.
        """
        try:
            for record in records:
                parsed_record = json.loads(record)
                if "UID" not in parsed_record:
                    logger.error("UID is required in all records for update")
                    return None
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in records: %s", e)
            return None

        header = {"ETId": str(ETId)}
        response = self._post(
            "envelopes/submit", json={"Data": records}, headers=header
        )

        if not response or not response.get("success"):
            logger.error("Failed to update records")
            return None

        try:
            parsed_response = SingleDataRequestResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logger.error("SingleDataRequestResponse Validation Error: %s", e)
            return None

    # ------------------------------------------------------------------ READ – simple

    def get_all(
        self,
        ETId: int,
        pageNumber: int = 0,
        pageSize: int = 0,
        fromSummary: bool = False,
    ) -> list[dict[str, Any]] | None:
        """Retrieve **all** rows or a paginated slice.

        Args:
            ETId: Envelope‑type ID.
            pageNumber: 1‑based page index; ``0`` disables pagination.
            pageSize: Rows per page (*ignored* if ``pageNumber`` is ``0``).
            fromSummary: When *True* query the summary table.

        Returns:
            List of row dicts, or ``None``.
        """
        header = {"ETId": str(ETId)}
        query = f"query/get?pageNo={pageNumber}&pageSize={pageSize}&fromSummary={'true' if fromSummary else 'false'}"
        response = self._post(query, headers=header)

        if not response or not response.get("success"):
            logger.error("Failed to fetch all records")
            return None

        try:
            parsed_response = GetAllRecordsResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logger.error("GetAllRecordsResponse Validation Error: %s", e)
            return None

    def get_single_record_by_record_id(
        self, record_id: dict[str, str], ETId: int, fromSummary: bool = False
    ) -> list[dict[str, Any]] | None:
        """Fetch one or more records filtered by *record_id*.

        Args:
            record_id: Simple equality filter – usually ``{"UID": "…"}``.
            ETId: Envelope‑type ID of the table to query.
            fromSummary: Search summary view instead of full table.

        Returns:
            Matching rows or ``None``.
        """
        header = {"ETId": str(ETId)}
        query = f"query/get?fromSummary={'true' if fromSummary else 'false'}"
        response = self._post(query, headers=header, json=record_id)

        if not response or not response.get("success"):
            logger.error("Failed to fetch single record")
            return None

        try:
            parsed_response = GetSingleRecordResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logger.error("GetSingleRecordResponse Validation Error: %s", e)
            return None

    # ------------------------------------------------------------------ READ – complex/aggregate

    def post_complex_query(
        self, ETId: int, pipeline: list[dict[str, Any]]
    ) -> ComplexQueryRecords | None:
        """Run an arbitrary Mongo‑style aggregation *pipeline* (``getcomplex``).

        Args:
            ETId: Primary collection ETId.
            pipeline: List of pipeline stage dictionaries.

        Returns:
            :class:`ComplexQueryRecords` or ``None`` on failure.
        """
        header = {"ETId": str(ETId)}
        response = self._post("query/getcomplex", headers=header, json=pipeline)

        if not response or not response.get("success"):
            logger.error("Failed to fetch complex query results")
            return None

        try:
            parsed_response = GetComplexQueryResponse(**response)
            return ComplexQueryRecords(
                Records=parsed_response.data, Total=parsed_response.Total
            )
        except ValidationError as e:
            logger.error("Complex Query Parsing Error: %s", e)
            return None

    def post_query_api(
        self,
        ETId: int,
        payload: dict[str, Any],
        schemaVersion: int = 1,
        pageNumber: int = 1,
        pageSize: int = 0,
    ) -> list[str] | None:
        """Endpoint helper for the simplified *query API*.

        Args:
            ETId: Envelope‑type ID.
            payload: Query filter object (see Walacor docs).
            schemaVersion: `SV` header value – defaults to latest (``1``).
            pageNumber: 1‑based index of the page to retrieve.
            pageSize: Number of rows per page (``0`` = no limit).

        Returns:
            Raw JSON *strings* returned by the platform or ``None``.
        """
        headers = {"ETId": str(ETId), "SV": str(schemaVersion)}
        query = f"query/get?pageNo={pageNumber}&pageSize={pageSize}"
        response = self._post(query, headers=headers, json=payload)

        if not response or not response.get("success"):
            logger.error("Failed to fetch query results")
            return None

        try:
            parsed_response = QueryApiResponse(**response)
            return parsed_response.data
        except ValidationError as e:
            logger.error("QueryApiResponse Validation Error: %s", e)
            return None

    def post_query_api_aggregate(
        self,
        payload: list[dict[str, Any]],
        ETId: int = 10,
        schemaVersion: int = 1,
        dataVersion: int = 1,
    ) -> QueryApiAggregate | None:
        """Wrapper for *query/getComplex* when using the **aggregate** flavour.

        Args:
            payload: Aggregate pipeline list.
            ETId: Primary collection ETId – default ``10``.
            schemaVersion: `SV` header value.
            dataVersion: `DV` header value.

        Returns:
            :class:`QueryApiAggregate` with ``Records`` and ``Total`` or ``None``.
        """
        headers = {
            "ETId": str(ETId),
            "SV": str(schemaVersion),
            "DV": str(dataVersion),
        }
        response = self._post("query/getComplex", headers=headers, json=payload)

        if not response or not response.get("success"):
            logger.error("Failed to fetch aggregate results")
            return None

        try:
            parsed_response = QueryApiAggregateResponse(**response)
            return QueryApiAggregate(
                Records=parsed_response.data, Total=parsed_response.Total
            )
        except ValidationError as e:
            logger.error("QueryApiAggregateResponse Validation Error: %s", e)
            return None

    def post_complex_MQL_queries(
        self,
        pipeline: list[dict[str, Any]],
        ETId: int,
    ) -> ComplexQMLQueryRecords | None:
        """Pass‑through helper for advanced *MQL* pipelines.

        Args:
            pipeline: Mongo Query Language aggregate pipeline.
            ETId: Primary collection envelope‑type ID.

        Returns:
            :class:`ComplexQMLQueryRecords` or ``None``.
        """
        header = {"ETId": str(ETId)}
        response = self._post("query/getcomplex", headers=header, json=pipeline)

        if not response or not response.get("success"):
            logger.error("Failed to fetch MQL query results")
            return None

        try:
            parsed_response = GetComplexQMLQueryResponse(**response)
            return ComplexQMLQueryRecords(
                Records=parsed_response.data, Total=parsed_response.Total
            )
        except ValidationError as e:
            logger.error("GetComplexQMLQueryResponse Validation Error: %s", e)
            return None

    # ------------------------------------------------------------------ END REGION
