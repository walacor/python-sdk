import types

from importlib import import_module
from typing import TYPE_CHECKING

# Schema model types
from .models.models import (
    ArrayField,
    AutoGenField,
    BooleanField,
    CreateFieldRequest,
    CreateIndexRequest,
    CreateSchemaDefinition,
    CronField,
    DatetimeField,
    DecimalField,
    IndexEntry,
    IntegerField,
    SchemaDetail,
    SchemaEntry,
    SchemaItem,
    SchemaMetadata,
    SchemaSummary,
    SchemaType,
    SchemaVersionEntry,
    TextField,
)
from .models.schema_request import (
    CreateSchemaRequest,
    SchemaQueryListRequest,
)

__all__ = [
    "CreateFieldRequest",
    "CreateIndexRequest",
    "CreateSchemaDefinition",
    "CreateSchemaRequest",
    "SchemaQueryListRequest",
    "TextField",
    "IntegerField",
    "DecimalField",
    "BooleanField",
    "DatetimeField",
    "ArrayField",
    "CronField",
    "AutoGenField",
    "IndexEntry",
    "SchemaDetail",
    "SchemaEntry",
    "SchemaItem",
    "SchemaMetadata",
    "SchemaSummary",
    "SchemaType",
    "SchemaVersionEntry",
    "models",
]


def __getattr__(name: str) -> types.ModuleType:
    if name == "models":
        mod = import_module(f"{__name__}.models")
        globals()[name] = mod
        return mod
    raise AttributeError(name)


if TYPE_CHECKING:  # pragma: no cover
    from . import models
