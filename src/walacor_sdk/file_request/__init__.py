import types

from importlib import import_module
from typing import TYPE_CHECKING

from .models.file_request_request import (
    StoreFileRequest,
    VerifySingleFileRequest,
)
from .models.models import (
    DuplicateData,
    FileInfo,
    FileInfoWrapper,
    FileItem,
    FileMetadata,
    MemoryFileItem,
    StoreFileData,
    VerifyFile,
)

__all__: list[str] = [
    "VerifySingleFileRequest",
    "StoreFileRequest",
    "FileItem",
    "MemoryFileItem",
    "FileMetadata",
    "FileInfo",
    "FileInfoWrapper",
    "StoreFileData",
    "VerifyFile",
    "DuplicateData",
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
