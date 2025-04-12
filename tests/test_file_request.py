from unittest.mock import MagicMock, patch

import pytest

from walacor_sdk.file_requests.file_request_service import FileRequestService
from walacor_sdk.file_requests.models.file_request_request import (
    VerifySingleFileRequest,
)
from walacor_sdk.file_requests.models.models import File, FileInfo


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return FileRequestService(mock_client)


@patch("walacor_sdk.file_request.file_request_service.logger")
def test_verify_single_file_success(mock_logging, service):
    path = "tests/assets/sample.pdf"
    request_model = VerifySingleFileRequest(path=path)

    mock_response = FileInfo(
        File=File(
            Name="sample.pdf",
            Encoding="7bit",
            MimeType="application/pdf",
            TempFilePath="/tmp/sample.pdf",
            Size="12456",
            FolderName="uploads",
        ),
        FileSignature="fake-signature",
        FileHash="abc123",
        FolderName="uploads",
        TotalEncryptedChunkFile=1,
    )

    service.post = MagicMock(return_value=mock_response)

    result = service.verify(request_model)

    assert isinstance(result, FileInfo)
    assert result.File.Name == "sample.pdf"
    assert result.FileSignature == "fake-signature"
    assert result.FileHash == "abc123"
    assert result.TotalEncryptedChunkFile == 1
    service.post.assert_called_once()


@patch("walacor_sdk.file_request.file_request_service.logging")
def test_verify_single_file_failure(mock_logging):
    path = "tests/assets/sample.pdf"
    request_model = VerifySingleFileRequest(path=path)

    service = FileRequestService(client=MagicMock())

    service.post = MagicMock(return_value=None)

    result = service.verify(request_model)

    assert result is None
    service.post.assert_called_once()
    mock_logging.error.assert_called()


@patch("walacor_sdk.file_request.file_request_service.logging")
def test_verify_single_file_validation_error(mock_logging):
    path = "tests/assets/sample.pdf"
    request_model = VerifySingleFileRequest(path=path)

    service = FileRequestService(client=MagicMock())

    malformed_response = {
        "File": {
            "Name": "sample.pdf",
            "Encoding": "7bit",
            "MimeType": "application/pdf",
            "TempFilePath": "/tmp/sample.pdf",
            "Size": "12456",
            "FolderName": "uploads",
        },
    }

    service.post = MagicMock(return_value=malformed_response)

    result = service.verify(request_model)

    assert result is None
    mock_logging.error.assert_called()
