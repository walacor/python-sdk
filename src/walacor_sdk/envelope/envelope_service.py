from typing import Any
from urllib.parse import urlencode

from pydantic import ValidationError

from walacor_sdk.base.base_service import BaseService
from walacor_sdk.base.w_client import W_Client
from walacor_sdk.envelope.models.envelope_response import (
    GetReplayHistoryDetailedResponse,
    GetReplayHistoryResponse,
    PostEnvelopeQueryResponse,
)
from walacor_sdk.envelope.models.models import ReplayHistoryDetailed
from walacor_sdk.utils.logger import get_logger

logger = get_logger(__name__)


class EnvelopeService(BaseService):
    def __init__(self, client: W_Client) -> None:
        super().__init__(client)

    def _build_replay_headers(
        self,
        ETId: int,
        schemaVersion: int | None = None,
    ) -> dict[str, str]:
        headers: dict[str, str] = {
            "ETId": str(ETId),
        }

        if schemaVersion is not None:
            headers["SV"] = str(schemaVersion)

        return headers

    def _build_replay_payload(
        self,
        UID: str,
        EId: str | None = None,
        updated_at: int | None = None,
    ) -> dict[str, Any] | None:
        if not isinstance(UID, str) or UID.strip() == "":
            logger.error("UID must be a non-empty string")
            return None

        if EId is not None and (not isinstance(EId, str) or EId.strip() == ""):
            logger.error("EId must be a non-empty string when provided")
            return None

        if updated_at is not None and (
            isinstance(updated_at, bool) or not isinstance(updated_at, int)
        ):
            logger.error("updated_at must be an integer timestamp when provided")
            return None

        payload: dict[str, Any] = {
            "UID": UID.strip(),
        }

        if EId is not None:
            payload["EId"] = EId.strip()

        if updated_at is not None:
            payload["updated_at"] = updated_at

        return payload

    def _build_query_params(
        self,
        org_id: str | None = None,
        pageNo: int | None = None,
        pageSize: int | None = None,
        order: str | None = None,
        orderBy: str | None = None,
        totalReq: bool | None = None,
    ) -> str:
        query_params: dict[str, str] = {}

        if org_id is not None:
            query_params["ORGId"] = org_id

        if pageNo is not None:
            query_params["pageNo"] = str(pageNo)

        if pageSize is not None:
            query_params["pageSize"] = str(pageSize)

        if order is not None:
            query_params["order"] = order

        if orderBy is not None:
            query_params["orderBy"] = orderBy

        if totalReq is not None:
            query_params["totalReq"] = str(totalReq).lower()

        if not query_params:
            return ""

        return f"?{urlencode(query_params)}"

    def _validate_pagination(
        self,
        pageNo: int | None,
        pageSize: int | None,
    ) -> bool:
        if pageNo is not None and (
            isinstance(pageNo, bool) or not isinstance(pageNo, int) or pageNo < 0
        ):
            logger.error("pageNo must be a non-negative integer when provided")
            return False

        if pageSize is not None and (
            isinstance(pageSize, bool) or not isinstance(pageSize, int) or pageSize <= 0
        ):
            logger.error("pageSize must be a positive integer when provided")
            return False

        return True

    def query_envelopes(
        self,
        query: dict[str, Any] | list[dict[str, Any]] | None = None,
        pageNo: int | None = None,
        pageSize: int | None = None,
        order: str | None = None,
        orderBy: str | None = None,
        totalReq: bool | None = None,
    ) -> PostEnvelopeQueryResponse | None:
        logger.info("Querying envelopes")

        if not self._validate_pagination(
            pageNo=pageNo,
            pageSize=pageSize,
        ):
            return None

        if order is not None and order not in {"asc", "desc"}:
            logger.error("order must be either 'asc' or 'desc' when provided")
            return None

        if query is None:
            payload: dict[str, Any] | list[dict[str, Any]] = {}
        elif isinstance(query, dict):
            payload = query
        elif isinstance(query, list) and all(isinstance(item, dict) for item in query):
            payload = query
        else:
            logger.error("query must be a dict, list of dicts, or None")
            return None

        endpoint = "envelopes/query"
        endpoint += self._build_query_params(
            pageNo=pageNo,
            pageSize=pageSize,
            order=order,
            orderBy=orderBy,
            totalReq=totalReq,
        )

        raw = self._post(endpoint, json=payload)
        response = self._handle_response(raw, action="query_envelopes")

        if response is None:
            return None

        try:
            return PostEnvelopeQueryResponse(**response)
        except ValidationError as e:
            logger.error(
                "PostEnvelopeQueryResponse Validation Error: %s; raw=%s",
                e,
                response,
            )
            return None

    def get_replay_history(
        self,
        UID: str,
        ETId: int,
        EId: str | None = None,
        updated_at: int | None = None,
        schemaVersion: int | None = None,
        org_id: str | None = None,
    ) -> dict[str, Any] | None:
        logger.info("Fetching replay history for UID=%s", UID)

        headers = self._build_replay_headers(
            ETId=ETId,
            schemaVersion=schemaVersion,
        )

        payload = self._build_replay_payload(
            UID=UID,
            EId=EId,
            updated_at=updated_at,
        )

        if payload is None:
            return None

        endpoint = "envelopes/history/replay"
        endpoint += self._build_query_params(org_id=org_id)

        raw = self._post(endpoint, headers=headers, json=payload)
        response = self._handle_response(raw, action="get_replay_history")

        if response is None:
            return None

        try:
            parsed = GetReplayHistoryResponse(**response)
            return parsed.data
        except ValidationError as e:
            logger.error(
                "GetReplayHistoryResponse Validation Error: %s; raw=%s",
                e,
                response,
            )
            return None

    def get_replay_history_detailed(
        self,
        UID: str,
        ETId: int,
        EId: str | None = None,
        updated_at: int | None = None,
        schemaVersion: int | None = None,
        org_id: str | None = None,
        pageNo: int | None = None,
        pageSize: int | None = None,
    ) -> ReplayHistoryDetailed | None:
        logger.info("Fetching detailed replay history for UID=%s", UID)

        if not self._validate_pagination(
            pageNo=pageNo,
            pageSize=pageSize,
        ):
            return None

        headers = self._build_replay_headers(
            ETId=ETId,
            schemaVersion=schemaVersion,
        )

        payload = self._build_replay_payload(
            UID=UID,
            EId=EId,
            updated_at=updated_at,
        )

        if payload is None:
            return None

        endpoint = "envelopes/history/replay/detailed"
        endpoint += self._build_query_params(
            org_id=org_id,
            pageNo=pageNo,
            pageSize=pageSize,
        )

        raw = self._post(endpoint, headers=headers, json=payload)
        response = self._handle_response(raw, action="get_replay_history_detailed")

        if response is None:
            return None

        try:
            parsed = GetReplayHistoryDetailedResponse(**response)
            return parsed.data
        except ValidationError as e:
            logger.error(
                "GetReplayHistoryDetailedResponse Validation Error: %s; raw=%s",
                e,
                response,
            )
            return None

    def get_replay_history_up_to_updated_at(
        self,
        UID: str,
        ETId: int,
        updated_at: int,
        schemaVersion: int | None = None,
        org_id: str | None = None,
    ) -> dict[str, Any] | None:
        logger.info(
            "Fetching replay history up to updated_at for UID=%s updated_at=%s",
            UID,
            updated_at,
        )

        headers = self._build_replay_headers(
            ETId=ETId,
            schemaVersion=schemaVersion,
        )

        payload = self._build_replay_payload(
            UID=UID,
            updated_at=updated_at,
        )

        if payload is None:
            return None

        endpoint = "envelopes/history/replay/upToUpdatedAt"
        endpoint += self._build_query_params(org_id=org_id)

        raw = self._post(endpoint, headers=headers, json=payload)
        response = self._handle_response(
            raw,
            action="get_replay_history_up_to_updated_at",
        )

        if response is None:
            return None

        try:
            parsed = GetReplayHistoryResponse(**response)
            return parsed.data
        except ValidationError as e:
            logger.error(
                "GetReplayHistoryResponse Validation Error: %s; raw=%s",
                e,
                response,
            )
            return None
