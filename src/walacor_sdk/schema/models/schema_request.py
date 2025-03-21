from pydantic import BaseModel

from walacor_sdk.schema.models.models import (
    CreateSchemaDefinition,
)


class CreateSchemaRequest(BaseModel):
    ETId: int
    SV: int
    Schema: CreateSchemaDefinition
