# walacor_sdk/base/exceptions.py
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


@dataclass
class WalacorErrorItem:
    reason: str
    message: str


class WalacorRequestError(RuntimeError):
    def __init__(
        self,
        *,
        code: int | None = None,
        errors: Iterable[WalacorErrorItem] | None = None,
        raw: dict[str, Any] | None = None,
        message: str | None = None,
    ) -> None:
        self.code = code
        self.errors = list(errors or [])
        self.raw = raw or {}
        super().__init__(message or self._build_message())

    def _build_message(self) -> str:
        if not self.errors:
            return f"Walacor request failed (code={self.code})"
        lines = [f"Walacor request failed (code={self.code}):"]
        for e in self.errors:
            lines.append(f"- {e.reason}: {e.message}")
        return "\n".join(lines)
