import types

from importlib import import_module
from typing import TYPE_CHECKING

from .models.models import (
    ArrayField,
    BooleanField,
    CreateSchemaDefinition,
    CronField,
    DatetimeField,
    DecimalField,
    IndexEntry,
    IntegerField,
    TextField,
)
from .models.schema_request import (
    CreateSchemaRequest,
    SchemaQueryListRequest,
)
from .schema_service import SchemaService

__all__: list[str] = [
    "SchemaService",
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
    "IndexEntry",
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
