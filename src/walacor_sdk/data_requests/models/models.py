from pydantic import BaseModel


class SingleRecordDetail(BaseModel):
    EId: str
    ETId: int
    ES: int
    UID: list[str]
