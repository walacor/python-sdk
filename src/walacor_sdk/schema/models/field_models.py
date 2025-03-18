from typing import Annotated, Literal

from pydantic import BaseModel, Field

from walacor_sdk.utils.enums import FieldTypeEnum


class BaseDataType(BaseModel):
    Name: str = Field(..., description="The type of the schema field")


class IntegerField(BaseDataType):
    Name: Literal["INTEGER"] = FieldTypeEnum.INTEGER.value
    DefaultValue: int | None = None
    MinValue: int | None = None
    MaxValue: int | None = None


class TextField(BaseDataType):
    Name: Literal["TEXT"] = FieldTypeEnum.TEXT.value
    DefaultValue: str | None = None
    MinLength: int | None = None
    MaxLength: int | None = None


class DecimalField(BaseDataType):
    Name: Literal["DECIMAL"] = FieldTypeEnum.DECIMAL.value
    DefaultValue: float | None = None
    MinValue: float | None = None
    MaxValue: float | None = None


class BooleanField(BaseDataType):
    Name: Literal["BOOLEAN"] = FieldTypeEnum.BOOLEAN.value
    DefaultValue: bool | None = None


class DatetimeField(BaseDataType):
    Name: Literal["DATETIME(EPOCH)"] = FieldTypeEnum.DATETIME_EPOCH.value
    DefaultValue: str | None = None


class ArrayField(BaseDataType):
    Name: Literal["ARRAY"] = FieldTypeEnum.ARRAY.value
    DefaultValue: str | None = None
    Type: str


class CronField(BaseDataType):
    Name: Literal["CRON"] = FieldTypeEnum.CRON.value
    DefaultValue: str | None = None
    MinLength: int | None = None
    MaxLength: int | None = None


SchemaType = Annotated[
    IntegerField
    | TextField
    | DecimalField
    | BooleanField
    | DatetimeField
    | ArrayField
    | CronField,
    Field(discriminator="Name"),
]
