import mimetypes

from pathlib import Path
from typing import IO

from pydantic import BaseModel, Field


class VerifyFile(BaseModel):
    Name: str = Field(..., alias="name")
    Encoding: str = Field(..., alias="encoding")
    MimeType: str = Field(..., alias="mimetype")
    TempFilePath: str = Field(default="", alias="TempFilePath")
    Size: int = Field(..., alias="size")
    FolderName: str = Field(default="", alias="FolderName")
    Status: str = Field(default="", alias="Status")
    SL: str = Field(default="", alias="SL")
    UID: str = Field(default="", alias="UID")
    FH: str = Field(default="", alias="FH")


class FileInfo(BaseModel):
    File: VerifyFile = Field(..., alias="file")
    FileSignature: str = Field(..., alias="fileSignature")
    FileHash: str = Field(..., alias="fileHash")
    TotalEncryptedChunkFile: int = Field(..., alias="totalEncryptedChunkFile")


class StoreFileData(BaseModel):
    UID: list[str]


class FileInfoWrapper(BaseModel):
    fileInfo: FileInfo = Field(..., alias="fileInfo")


class DuplicateData(BaseModel):
    eid: str = Field(..., alias="EId")
    uid: list[str] = Field(..., alias="UID")
    dh: str = Field(..., alias="DH")
    created_at: int = Field(..., alias="CreatedAt")
    signature: str = Field(..., alias="Signature")
    signature_type: str = Field(..., alias="SignatureType")


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


class FileMetadata(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    size: int | None = None
    ORGId: str
    SL: str
    FH: str | None = None
    tempFilePath: str | None = None
    mimetype: str
    Hash: str | None = None
    EId: str
    UID: str
    LastModifiedBy: str
    SV: int
    UpdatedAt: int
    CreatedAt: int
    IsDeleted: bool
    Status: str


class MemoryFileItem:

    def __init__(self, buffer: IO[bytes], *, name: str, mimetype: str | None = None):
        self._buffer = buffer
        self.name = name
        self.mimetype = (
            mimetype or mimetypes.guess_type(name)[0] or "application/octet-stream"
        )

    def to_tuple(self) -> tuple[str, tuple[str, IO[bytes], str]]:
        self._buffer.seek(0)
        return ("file", (self.name, self._buffer, self.mimetype))
