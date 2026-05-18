from datetime import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field

from walacor_sdk.schema.models.models import CreateSchemaDefinition


class CreateSchemaRequest(BaseModel):
    ETId: int = Field(default=50)
    SV: int = Field(default=1)
    Schema: CreateSchemaDefinition


class SchemaQueryListRequest(BaseModel):
    page: int = Field(default=0, ge=0)
    pageSize: int = Field(default=10, ge=0)
    order: Literal["asc", "desc"] = "desc"
    orderBy: str = "Family"
    startDate: dt | None = None
    endDate: dt | None = None
