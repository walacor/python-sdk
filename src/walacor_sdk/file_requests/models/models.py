import mimetypes

from pathlib import Path
from typing import IO

from pydantic import BaseModel


class File(BaseModel):
    Name: str
    Encoding: str
    MimeType: str
    TempFilePath: str
    Size: str
    FolderName: str


class FileInfo(BaseModel):
    File: File
    FileSignature: str
    FileHash: str
    FolderName: str
    TotalEncryptedChunkFile: int


class FileItem:
    def __init__(
        self,
        path: str | Path,
        name: str | None = None,
        mimetype: str | None = None,
    ) -> None:
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"File does not exist: {self.path}")
        if not self.path.is_file():
            raise ValueError(f"Path is not a file: {self.path}")

        self.name = name or self.path.name
        self.mimetype = (
            mimetype
            or mimetypes.guess_type(str(self.path))[0]
            or "application/octet-stream"
        )

    def to_tuple(self) -> tuple[str, tuple[str, IO[bytes], str]]:
        file_obj = open(self.path, "rb")
        return ("file", (self.name, file_obj, self.mimetype))
