from typing import Any

from pydantic import BaseModel


class ReplayHistoryPagination(BaseModel):
    pageNo: int | None = None
    pageNumber: int | None = None  # backward-compatible fallback
    pageSize: int
    total: int
    totalPage: int | None = None

    @property
    def current_page(self) -> int:
        return self.pageNo if self.pageNo is not None else self.pageNumber or 0


class ReplayHistoryDetailed(BaseModel):
    result: dict[str, Any] | None
    history: list[dict[str, Any]]
    pagination: ReplayHistoryPagination
