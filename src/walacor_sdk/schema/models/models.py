from typing import Annotated, Literal

from pydantic import BaseModel, Field

from walacor_sdk.utils.enums import FieldType

# region Schema Fields


class BaseDataType(BaseModel):
    Name: str


class IntegerField(BaseDataType):
    Name: Literal["INTEGER"] = FieldType.INTEGER.value
    DefaultValue: int | None = None
    MinValue: int | None = None
    MaxValue: int | None = None


class TextField(BaseDataType):
    Name: Literal["TEXT"] = FieldType.TEXT.value
    DefaultValue: str | None = None
    MinLength: int | None = None
    MaxLength: int | None = None


class DecimalField(BaseDataType):
    Name: Literal["DECIMAL"] = FieldType.DECIMAL.value
    DefaultValue: float | None = None
    MinValue: float | None = None
    MaxValue: float | None = None


class BooleanField(BaseDataType):
    Name: Literal["BOOLEAN"] = FieldType.BOOLEAN.value
    DefaultValue: bool | None = None


class DatetimeField(BaseDataType):
    Name: Literal["DATETIME(EPOCH)"] = FieldType.DATETIME_EPOCH.value
    DefaultValue: str | None = None


class ArrayField(BaseDataType):
    Name: Literal["ARRAY"] = FieldType.ARRAY.value
    DefaultValue: str | None = None
    Type: str


class CronField(BaseDataType):
    Name: Literal["CRON"] = FieldType.CRON.value
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


class AutoGenField(BaseModel):
    FieldName: str
    DataType: str
    Required: bool
    SystemGenerated: bool
    MaxLength: int | None = None


# endregion


# region Schema UI - Data
class SchemaEntry(BaseModel):
    ETId: int
    TableName: str
    SV: int


class SchemaVersionEntry(BaseModel):
    ETId: int
    versions: list[int]


# endregion


# region Schema UI - Index
class IndexKey(BaseModel):
    _id: int


class IndexEntry(BaseModel):
    version: int = Field(..., alias="v")
    key: IndexKey
    name: str
    namespace: str = Field(..., alias="ns")


# endregion

# region Add Schema


class CreateFieldRequest(BaseModel):
    FieldName: str
    DataType: FieldType
    Required: bool = False
    MaxLength: int | None = None


class CreateIndexRequest(BaseModel):
    Fields: list[str]
    IndexValue: str
    ForceUpdate: bool = False
    Delete: bool = False


class SchemaData(BaseModel):
    EId: str
    ETId: int
    SV: int
    ES: int
    CreatedAt: int
    UpdatedAt: int
    UID: list[str]


class CreateSchemaDefinition(BaseModel):
    ETId: int = Field(..., ge=10000, description="ETId must be at least 10000")
    TableName: str
    Family: str
    DoSummary: bool = False
    Fields: list[CreateFieldRequest]
    Indexes: list[CreateIndexRequest] = Field(default_factory=list)


class SchemaMetadata(BaseModel):
    EId: str
    ETId: int
    SV: int
    ES: int
    CreatedAt: int
    UpdatedAt: int
    UID: list[str]


# endregion

# region Schema Detail


class SchemaField(BaseModel):
    FieldName: str
    DataType: str
    MaxLength: int | None = None
    Required: bool | None = False
    Default: bool | int | float | str | None = None
    Decimals: int | None = None
    SystemGenerated: bool | None = False


class SchemaIndexItem(BaseModel):
    Fields: list[str]
    IndexValue: str
    ForceUpdate: bool = False
    Delete: bool = False


class SchemaDetail(BaseModel):
    id: str = Field(..., alias="_id")
    ETId: int
    TableName: str
    Family: str
    DoSummary: bool
    Fields: list[SchemaField]
    Indexes: list[SchemaIndexItem]
    DbTableName: str
    DbHistoryTableName: str
    SV: int
    LastModifiedBy: str
    UID: str
    ORGId: str
    SL: str
    HashSign: str
    HS: str
    EId: str
    UpdatedAt: int
    IsDeleted: bool
    CreatedAt: int


class SchemaItem(BaseModel):
    id: str = Field(..., alias="_id")
    ORGId: str
    ORGName: str
    EId: str
    ETId: int
    TableName: str
    DbTableName: str
    DbHistoryTableName: str
    Family: str
    DoSummary: bool
    LastModifiedBy: str
    CreatedAt: int
    UpdatedAt: int
    DV: int | None = None
    Description: str | None = ""


class SchemaSummary(BaseModel):
    UID: str
    schema_name: str = Field(..., alias="schema")
    ETId: int
    createdDate: int
    Family: str
    SV: int
    numberOfFields: int


class SchemaQueryList(BaseModel):
    data: list[SchemaSummary]
    total: int


# endregion
