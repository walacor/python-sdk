from pathlib import Path
from typing import IO, Union

from pydantic import BaseModel

from walacor_sdk.file_request.models.models import FileInfo, FileItem, MemoryFileItem


class VerifySingleFileRequest:
    file: Union["FileItem", "MemoryFileItem"]

    def __init__(
        self,
        path: str | Path,
        name: str | None = None,
        mimetype: str | None = None,
    ) -> None:
        self.file = FileItem(path=path, name=name, mimetype=mimetype)

    def to_files_param(self) -> list[tuple[str, tuple[str, IO[bytes], str]]]:
        return [self.file.to_tuple()]

    @classmethod
    def from_memory(cls, item: MemoryFileItem) -> "VerifySingleFileRequest":
        obj = cls.__new__(cls)
        obj.file = item
        return obj


class StoreFileRequest(BaseModel):
    fileInfo: FileInfo
