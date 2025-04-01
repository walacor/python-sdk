from pydantic import BaseModel


class SubmissionResult(BaseModel):
    EId: str
    ETId: int
    ES: int
    UID: list[str]
