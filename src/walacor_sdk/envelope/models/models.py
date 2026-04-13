from typing import Any

from pydantic import BaseModel


class ReplayHistoryDetailed(BaseModel):
    result: dict[str, Any] | None
    history: list[dict[str, Any]]
