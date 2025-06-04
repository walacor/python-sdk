from unittest.mock import MagicMock, mock_open, patch

import pytest

from pydantic import ValidationError
from requests import RequestException

from walacor_sdk.file_request.file_request_service import FileRequestService
from walacor_sdk.file_request.models.file_request_request import VerifySingleFileRequest
from walacor_sdk.file_request.models.models import (
    DuplicateData,
    FileInfo,
    FileMetadata,
    VerifyFile,
)
from walacor_sdk.utils.exceptions import FileRequestError

# ------------------------------> FIXTURES


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return FileRequestService(mock_client)


# ------------------------------> VERIFY


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("walacor_sdk.file_request.file_request_service.logger")
@patch("walacor_sdk.file_request.models.file_request_request.FileItem.to_tuple")
def test_verify_success(mock_to_tuple, mock_logger, mock_is_file, mock_exists, service):
    """Test successful verification returns parsed FileInfo."""
    file_request = VerifySingleFileRequest(
        path="/fake/sample.pdf", mimetype="application/pdf"
    )
    mock_to_tuple.return_value = ("file", ("sample.pdf", b"data", "application/pdf"))

    mock_response = {
        "success": True,
        "message": "File verified successfully",
        "data": {
            "fileInfo": {
                "file": {
                    "name": "sample.pdf",
                    "encoding": "utf-8",
                    "mimetype": "application/pdf",
                    "TempFilePath": "/tmp/sample.pdf",
                    "size": 1024,
                    "FolderName": "uploads",
                    "Status": "processed",
                    "SL": "some-sl",
                    "UID": "user123",
                    "FH": "hash==",
                },
                "fileSignature": "abc123sig",
                "fileHash": "abc123hash",
                "totalEncryptedChunkFile": 1,
            }
        },
    }

    service._post = MagicMock(return_value=mock_response)

    result = service.verify(file=file_request)

    assert result.File.Name == "sample.pdf"
    assert result.File.MimeType == "application/pdf"
    assert result.FileSignature == "abc123sig"
    assert result.FileHash == "abc123hash"
    assert result.TotalEncryptedChunkFile == 1
    service._post.assert_called_once()
    mock_logger.info.assert_called()


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("walacor_sdk.file_request.file_request_service.logger")
@patch("walacor_sdk.file_request.models.file_request_request.FileItem.to_tuple")
def test_verify_duplicate_file(
    mock_to_tuple, mock_logger, mock_is_file, mock_exists, service
):
    """Test verify raises DuplicateFileError when duplicateData is returned."""

    file_request = VerifySingleFileRequest(
        path="/fake/sample.pdf", mimetype="application/pdf"
    )
    mock_to_tuple.return_value = ("file", ("sample.pdf", b"data", "application/pdf"))

    duplicate_data_model = DuplicateData(
        EId="eid456",
        UID=["dupe123"],
        DH="hash==",
        CreatedAt=1710000000,
        Signature="signature123",
        SignatureType="SHA256",
    )

    mock_response = {"duplicateData": duplicate_data_model.model_dump(by_alias=True)}

    service._post = MagicMock(return_value=mock_response)

    result = service.verify(file=file_request)

    assert isinstance(result, DuplicateData)
    assert result.eid == "eid456"
    assert result.uid == ["dupe123"]
    assert result.dh == "hash=="
    assert result.signature == "signature123"
    mock_logger.exception.assert_not_called()


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("walacor_sdk.file_request.file_request_service.logger")
@patch("walacor_sdk.file_request.models.file_request_request.FileItem.to_tuple")
def test_verify_validation_error(
    mock_to_tuple, mock_logger, mock_is_file, mock_exists, service
):
    """Test verify raises FileRequestError on validation error."""
    file_request = VerifySingleFileRequest(
        path="/fake/sample.pdf", mimetype="application/pdf"
    )
    mock_to_tuple.return_value = ("file", ("sample.pdf", b"data", "application/pdf"))

    malformed_response = {
        "success": True,
        "message": "Invalid structure",
        "data": {"fileInfo": {}},
    }

    service._post = MagicMock(return_value=malformed_response)

    with patch(
        "walacor_sdk.file_request.file_request_service.VerifySuccessResponse",
        side_effect=ValidationError.from_exception_data("VerifySuccessResponse", []),
    ):
        with pytest.raises(FileRequestError, match="verification failed"):
            service.verify(file=file_request)
    mock_logger.exception.assert_called()


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("walacor_sdk.file_request.file_request_service.logger")
@patch("walacor_sdk.file_request.models.file_request_request.FileItem.to_tuple")
def test_verify_network_error(
    mock_to_tuple, mock_logger, mock_is_file, mock_exists, service
):
    """Test verify raises FileRequestError on request exception."""
    file_request = VerifySingleFileRequest(
        path="/fake/sample.pdf", mimetype="application/pdf"
    )
    mock_to_tuple.return_value = ("file", ("sample.pdf", b"data", "application/pdf"))

    service._post = MagicMock(side_effect=RequestException("timeout"))

    with pytest.raises(FileRequestError, match="verification failed"):
        service.verify(file=file_request)
    mock_logger.exception.assert_called()


# ------------------------------> STORE


def make_file_info() -> FileInfo:
    return FileInfo(
        file=VerifyFile(
            name="sample.pdf",
            encoding="utf-8",
            mimetype="application/pdf",
            TempFilePath="/tmp/sample.pdf",
            size=1024,
            FolderName="uploads",
            Status="processed",
            SL="sl-001",
            UID="uid123",
            FH="hash==",
        ),
        fileSignature="abc123sig",
        fileHash="abc123hash",
        totalEncryptedChunkFile=1,
    )


@patch("walacor_sdk.file_request.file_request_service.logger")
def test_store_success(mock_logger, service):
    """Test store returns StoreFileData on valid response."""
    file_info = make_file_info()

    mock_response = {
        "success": True,
        "message": "Stored successfully",
        "data": {"UID": ["stored123"]},
    }

    service._post = MagicMock(return_value=mock_response)

    result = service.store(file_info=file_info)

    assert result.UID == ["stored123"]
    service._post.assert_called_once()
    mock_logger.exception.assert_not_called()


@patch("walacor_sdk.file_request.file_request_service.logger")
def test_store_validation_error(mock_logger, service):
    """Test store raises FileRequestError on response validation failure."""
    file_info = make_file_info()

    service._post = MagicMock(return_value={"success": True, "data": {}})

    with patch(
        "walacor_sdk.file_request.file_request_service.StoreFileResponse",
        side_effect=ValidationError.from_exception_data("StoreFileResponse", []),
    ):
        with pytest.raises(FileRequestError, match="store failed"):
            service.store(file_info=file_info)

    mock_logger.exception.assert_called()


@patch("walacor_sdk.file_request.file_request_service.logger")
def test_store_network_error(mock_logger, service):
    """Test store raises FileRequestError on request failure."""
    file_info = make_file_info()

    service._post = MagicMock(side_effect=RequestException("network error"))

    with pytest.raises(FileRequestError, match="store failed"):
        service.store(file_info=file_info)

    mock_logger.exception.assert_called()


# ------------------------------> DOWNLOAD


@patch("walacor_sdk.file_request.file_request_service.open", new_callable=mock_open)
@patch("walacor_sdk.file_request.file_request_service.Path.mkdir")
@patch("walacor_sdk.file_request.file_request_service.logger")
def test_download_success_with_filename(
    mock_logger, mock_mkdir, mock_open_file, service
):
    """Test successful download writes file to disk with metadata.name"""
    uid = "file123"
    metadata = FileMetadata(
        _id="id1",
        name="report.pdf",
        size=1024,
        ORGId="org1",
        SL="sl1",
        mimetype="application/pdf",
        Hash="xyz",
        EId="eid1",
        UID=uid,
        LastModifiedBy="user",
        SV=1,
        UpdatedAt=1,
        CreatedAt=1,
        IsDeleted=False,
        Status="received",
    )

    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
    mock_response.headers = {}

    service._get_metadata = MagicMock(return_value=metadata)
    service._request_stream = MagicMock(return_value=mock_response)

    result_path = service.download(uid=uid, save_to="/fake/dir")

    assert result_path.name == "report.pdf"
    assert result_path.parent.name == "dir"
    mock_open_file().write.assert_any_call(b"chunk1")
    mock_open_file().write.assert_any_call(b"chunk2")
    mock_logger.info.assert_called_with("File saved to %s", result_path)


@patch("walacor_sdk.file_request.file_request_service.logger")
def test_download_no_metadata(mock_logger, service):
    """Test FileRequestError is raised if metadata is missing."""
    service._get_metadata = MagicMock(return_value=None)

    with pytest.raises(FileRequestError, match="no metadata found for UID"):
        service.download(uid="missing")
    mock_logger.info.assert_called()


@patch(
    "walacor_sdk.file_request.file_request_service.open",
    side_effect=OSError("disk full"),
)
@patch("walacor_sdk.file_request.file_request_service.Path.mkdir")
@patch("walacor_sdk.file_request.file_request_service.logger")
def test_download_oserror(mock_logger, mock_mkdir, mock_open_file, service):
    """Test FileRequestError is raised if file write fails."""
    uid = "file123"
    metadata = FileMetadata(
        _id="id1",
        name="file.txt",
        size=1024,
        ORGId="org1",
        SL="sl1",
        mimetype="text/plain",
        Hash="xyz",
        EId="eid1",
        UID=uid,
        LastModifiedBy="user",
        SV=1,
        UpdatedAt=1,
        CreatedAt=1,
        IsDeleted=False,
        Status="received",
    )

    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"chunk"]
    mock_response.headers = {}

    service._get_metadata = MagicMock(return_value=metadata)
    service._request_stream = MagicMock(return_value=mock_response)

    with pytest.raises(FileRequestError, match="failed to write file"):
        service.download(uid=uid)
    mock_logger.exception.assert_called()


@patch("walacor_sdk.file_request.file_request_service.Path.mkdir")
@patch("walacor_sdk.file_request.file_request_service.open", new_callable=mock_open)
@patch("walacor_sdk.file_request.file_request_service.logger")
def test_download_filename_from_headers(
    mock_logger, mock_open_file, mock_mkdir, service
):
    """Test filename is extracted from Content-Disposition when metadata.name is empty."""
    uid = "file123"
    metadata = FileMetadata(
        _id="id1",
        name="",
        size=1024,
        ORGId="org1",
        SL="sl1",
        mimetype="application/pdf",
        Hash="xyz",
        EId="eid1",
        UID=uid,
        LastModifiedBy="user",
        SV=1,
        UpdatedAt=1,
        CreatedAt=1,
        IsDeleted=False,
        Status="received",
    )

    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"data"]
    mock_response.headers = {
        "Content-Disposition": 'attachment; filename="downloaded.pdf"'
    }

    service._get_metadata = MagicMock(return_value=metadata)
    service._request_stream = MagicMock(return_value=mock_response)

    result_path = service.download(uid=uid)

    assert result_path.name == "downloaded.pdf"
    mock_logger.info.assert_called_with("File saved to %s", result_path)


# ------------------------------> HELPERS


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("builtins.open", new_callable=MagicMock)
def test_to_files_param_structure(mock_open, mock_is_file, mock_exists):
    """Ensure to_files_param returns correct multipart tuple."""
    req = VerifySingleFileRequest(path="/fake/file.txt", mimetype="text/plain")
    result = req.to_files_param()

    assert isinstance(result, list)
    assert result[0][0] == "file"
    assert result[0][1][0] == "file.txt"
    assert result[0][1][2] == "text/plain"
