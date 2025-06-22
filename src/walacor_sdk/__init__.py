import types

from importlib import import_module
from typing import TYPE_CHECKING

from .base.walacor_service import WalacorService

__all__: list[str] = [
    "WalacorService",
    "authentication",
    "schema",
    "file_request",
    "data_requests",
    "utils",
]


def __getattr__(name: str) -> types.ModuleType:
    if name in __all__[1:]:
        mod = import_module(f"{__name__}.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(name)


if TYPE_CHECKING:  # pragma: no cover
    from . import authentication, data_requests, file_request, schema, utils
