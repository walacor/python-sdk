import types

from importlib import import_module
from typing import TYPE_CHECKING

from .models.models import (
    ComplexQMLQueryRecords,
    ComplexQueryRecords,
    QueryApiAggregate,
    SubmissionResult,
)

__all__: list[str] = [
    "SubmissionResult",
    "ComplexQueryRecords",
    "QueryApiAggregate",
    "ComplexQMLQueryRecords",
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
