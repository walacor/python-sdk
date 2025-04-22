from datetime import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field

from walacor_sdk.schema.models.models import CreateSchemaDefinition


class CreateSchemaRequest(BaseModel):
    ETId: int
    SV: int
    Schema: CreateSchemaDefinition


class SchemaQueryListRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1)
    order: Literal["asc", "desc"] = "desc"
    orderBy: str = "Family"
    startDate: dt
    endDate: dt
