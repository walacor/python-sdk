from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class WalacorErrorItem(BaseModel):
    reason: str
    message: str


class WalacorError(BaseModel):
    code: int | None = None
    errors: list[WalacorErrorItem] = []


def format_walacor_error(err: WalacorError | None) -> str:
    if not err or not err.errors:
        return "No error details returned"
    return "; ".join(f"{e.reason}: {e.message}" for e in err.errors)


def extract_error_payload(resp: dict[str, Any] | None) -> WalacorError | None:
    if not isinstance(resp, dict):
        return None
    payload = resp.get("error") or resp.get("errors")
    if not payload:
        return None
    try:
        return WalacorError(**payload)
    except Exception:
        return None
