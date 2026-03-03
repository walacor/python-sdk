from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from walacor_sdk.base.exceptions.errors import WalacorErrorItem


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
