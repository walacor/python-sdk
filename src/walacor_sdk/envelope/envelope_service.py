from typing import Any
from urllib.parse import urlencode

from pydantic import ValidationError

from walacor_sdk.base.base_service import BaseService
from walacor_sdk.base.w_client import W_Client
from walacor_sdk.envelope.models.envelope_response import (
    GetReplayHistoryDetailedResponse,
    GetReplayHistoryResponse,
)
from walacor_sdk.envelope.models.models import ReplayHistoryDetailed
from walacor_sdk.utils.logger import get_logger

logger = get_logger(__name__)


class EnvelopeService(BaseService):
    def __init__(self, client: W_Client) -> None:
        super().__init__(client)

    def _post_replay_history(
        self,
        UID: str,
        ETId: int,
        EId: str | None = None,
        updated_at: int | None = None,
        detailed: bool = False,
        schemaVersion: int = 1,
        org_id: str | None = None,
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

        headers: dict[str, str] = {
            "ETId": str(ETId),
            "SV": str(schemaVersion),
        }

        payload: dict[str, Any] = {
            "UID": UID.strip(),
        }

        if EId is not None:
            payload["EId"] = EId.strip()

        if updated_at is not None:
            payload["updated_at"] = updated_at

        query_params: dict[str, str] = {}
        if detailed:
            query_params["detailed"] = "true"
        if org_id is not None:
            query_params["ORGId"] = org_id

        endpoint = "envelopes/history/replay"
        if query_params:
            endpoint = f"{endpoint}?{urlencode(query_params)}"

        raw = self._post(endpoint, headers=headers, json=payload)
        return self._handle_response(raw, action="get_replay_history")

    def get_replay_history(
        self,
        UID: str,
        ETId: int,
        EId: str | None = None,
        updated_at: int | None = None,
        schemaVersion: int = 1,
        org_id: str | None = None,
    ) -> dict[str, object] | None:
        logger.info("Fetching replay history for UID=%s", UID)

        response = self._post_replay_history(
            UID=UID,
            ETId=ETId,
            EId=EId,
            updated_at=updated_at,
            detailed=False,
            schemaVersion=schemaVersion,
            org_id=org_id,
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

    def get_replay_history_detailed(
        self,
        UID: str,
        ETId: int,
        EId: str | None = None,
        updated_at: int | None = None,
        schemaVersion: int = 1,
        org_id: str | None = None,
    ) -> ReplayHistoryDetailed | None:
        logger.info("Fetching detailed replay history for UID=%s", UID)

        response = self._post_replay_history(
            UID=UID,
            ETId=ETId,
            EId=EId,
            updated_at=updated_at,
            detailed=True,
            schemaVersion=schemaVersion,
            org_id=org_id,
        )
        if response is None:
            return None

        data = response.get("data")

        if not isinstance(data, dict):
            logger.error(
                "Detailed replay history response has invalid data type; raw=%s",
                response,
            )
            return None

        if "result" not in data or "history" not in data:
            logger.error(
                "Detailed replay history requested, but backend returned non-detailed payload; raw=%s",
                response,
            )
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
