import types

from importlib import import_module
from typing import TYPE_CHECKING

from .file_request_service import FileRequestService
from .models.file_request_request import (
    StoreFileRequest,
    VerifySingleFileRequest,
)
from .models.file_request_response import (
    ListFilesResponse,
    StoreFileResponse,
    VerifyResponse,
)
from .models.models import FileInfo, FileItem, FileMetadata

__all__: list[str] = [
    "FileRequestService",
    "VerifySingleFileRequest",
    "StoreFileRequest",
    "VerifyResponse",
    "StoreFileResponse",
    "ListFilesResponse",
    "FileItem",
    "FileMetadata",
    "models",
    "FileInfo",
]


def __getattr__(name: str) -> types.ModuleType:
    if name == "models":
        mod = import_module(f"{__name__}.models")
        globals()[name] = mod
        return mod
    raise AttributeError(name)


if TYPE_CHECKING:  # pragma: no cover
    from . import models
