from pathlib import Path
from typing import IO

from pydantic import BaseModel

from walacor_sdk.file_requests.models.models import FileInfo, FileItem


class VerifySingleFileRequest:
    def __init__(
        self,
        path: str | Path,
        name: str | None = None,
        mimetype: str | None = None,
    ) -> None:
        self.file = FileItem(path=path, name=name, mimetype=mimetype)

    def to_files_param(self) -> list[tuple[str, tuple[str, IO[bytes], str]]]:
        return [self.file.to_tuple()]


class StoreFileRequest(BaseModel):
    fileInfo: FileInfo
