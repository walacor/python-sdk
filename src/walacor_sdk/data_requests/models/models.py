from typing import Any

from pydantic import BaseModel


class SubmissionResult(BaseModel):
    EId: str
    ETId: int
    ES: int
    UID: list[str]


class ComplexQueryRecords(BaseModel):
    Records: list[dict[str, Any]]
    Total: int


class QueryApiAggregate(BaseModel):
    Records: list[dict[str, Any]]
    Total: int


class ComplexQMLQueryRecords(BaseModel):
    Records: list[dict[str, Any]]
    Total: int
