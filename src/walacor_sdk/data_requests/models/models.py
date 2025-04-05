from pydantic import BaseModel


class SubmissionResult(BaseModel):
    EId: str
    ETId: int
    ES: int
    UID: list[str]


class ComplexQueryRecords(BaseModel):
    Records: list[str]
    Total: int


class QueryApiAggregate(BaseModel):
    Records: list[str]
    Total: int


class ComplexQMLQueryRecords(BaseModel):
    Records: list[str]
    Total: int
