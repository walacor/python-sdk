from unittest.mock import MagicMock, patch

import pytest

from pydantic import ValidationError

from walacor_sdk.data_requests.data_requests_service import DataRequestsService
from walacor_sdk.data_requests.models.data_request_response import (
    SingleDataRequestResponse,
)
from walacor_sdk.data_requests.models.models import SubmissionResult


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return DataRequestsService(mock_client)


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_insert_single_record_success(mock_logging, service):
    """Test insert_single_record returns SingleRecordDetail when response is valid and successful."""
    mock_request = {
        "au_id": "1234",
        "test_lname": "l_test",
        "test_fname": "f_test",
        "test_phone": "9999999",
    }

    mock_response = {
        "success": True,
        "data": {"EId": "test", "ETId": 90000000, "ES": 30, "UID": ["213132"]},
    }

    service.post = MagicMock(return_value=mock_response)

    result = service.insert_single_record(mock_request, 90000000)

    assert isinstance(result, SubmissionResult)
    assert result.ETId == 90000000
    service.post.assert_called_once_with(
        "envelopes/submit", json={"Data": [mock_request]}, headers={"ETId": "90000000"}
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_insert_single_record_failure_flag(mock_logging, service):
    """Test insert_single_record returns None and logs error if success=False in API response."""
    mock_request = {"Data": "test"}
    service.post = MagicMock(return_value={"success": False})

    result = service.insert_single_record(mock_request, 123)

    assert result is None
    mock_logging.error.assert_called_once_with("Failed to insert record")


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_insert_single_record_validation_error(mock_logging, service):
    """Test insert_single_record handles ValidationError and logs it properly."""
    mock_request = {"some": "payload"}
    bad_response = {"success": True, "data": {"invalid": "structure"}}
    service.post = MagicMock(return_value=bad_response)

    with patch(
        "walacor_sdk.data_requests.data_requests_service.SingleDataRequestResponse",
        side_effect=ValidationError.from_exception_data(
            "SingleDataRequestResponse", []
        ),
    ):
        result = service.insert_single_record(mock_request, 42)

    assert result is None
    mock_logging.error.assert_called()
    assert (
        "SingleDataRequestResponse Validation Error"
        in mock_logging.error.call_args[0][0]
    )


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_insert_multiple_records_success(mock_logging, service):
    mock_request = [
        {
            "au_id": "1234",
            "test_lname": "l_test",
            "test_fname": "f_test",
            "test_phone": "9999999",
        },
        {
            "au_id": "4567",
            "test_lname": "l_test",
            "test_fname": "f_test",
            "test_phone": "92929292",
        },
    ]

    mock_response = {
        "success": True,
        "data": {
            "EId": "test",
            "ETId": 90000000,
            "ES": 30,
            "UID": ["213132", "1223131"],
        },
    }

    service.post = MagicMock(return_value=mock_response)

    result = service.insert_single_record(mock_request, 90000000)

    assert isinstance(result, SubmissionResult)
    assert result.ETId == 90000000
    service.post.assert_called_once_with(
        "envelopes/submit", json={"Data": [mock_request]}, headers={"ETId": "90000000"}
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_insert_multiple_records_failure_flag(mock_logging, service):
    """Test insert_single_record returns None and logs error if success=False in API response."""
    mock_request = {"test": "test"}
    service.post = MagicMock(return_value={"success": False})

    result = service.insert_single_record(mock_request, 123)

    assert result is None
    mock_logging.error.assert_called_once_with("Failed to insert record")


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_insert_multiple_records_validation_error(mock_logging, service):
    """Test insert_single_record handles ValidationError and logs it properly."""
    mock_request = {"some": "payload"}
    bad_response = {"success": True, "data": {"invalid": "structure"}}
    service.post = MagicMock(return_value=bad_response)

    with patch(
        "walacor_sdk.data_requests.data_requests_service.SingleDataRequestResponse",
        side_effect=ValidationError.from_exception_data(
            "SingleDataRequestResponse", []
        ),
    ):
        result = service.insert_single_record(mock_request, 42)

    assert result is None
    mock_logging.error.assert_called()
    assert (
        "SingleDataRequestResponse Validation Error"
        in mock_logging.error.call_args[0][0]
    )


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_update_single_record_success(mock_logging, service):
    """
    Test update_single_record with valid input and response.
    """
    record = '{"fname": "Alice", "UID": "abc123"}'
    etid = 1
    mock_response = {
        "success": True,
        "data": {"EId": "id1", "ETId": etid, "ES": 10, "UID": ["abc123"]},
    }

    with patch(
        "walacor_sdk.data_requests.data_requests_service.SingleDataRequestResponse",
        return_value=SingleDataRequestResponse(**mock_response),
    ):
        service.post = MagicMock(return_value=mock_response)
        result = service.update_single_record(record, etid)

        assert isinstance(result, SubmissionResult)
        service.post.assert_called_once_with(
            "envelopes/submit", json={"Data": [record]}, headers={"ETId": str(etid)}
        )
        mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_update_single_record_failure_flag(mock_logging, service):
    """
    Test update_single_record returns None and logs error if response.success is False.
    """
    record = '{"fname": "Bob", "UID": "uid_fail"}'
    service.post = MagicMock(return_value={"success": False})
    result = service.update_single_record(record, 123)

    assert result is None
    mock_logging.error.assert_called_with("Failed to insert record")


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_update_single_record_validation_error(mock_logging, service):
    """
    Test update_single_record returns None and logs validation error on schema mismatch.
    """
    record = '{"fname": "Mismatch", "UID": "uid_val"}'
    service.post = MagicMock(return_value={"success": True, "data": {"invalid": "yes"}})

    with patch(
        "walacor_sdk.data_requests.data_requests_service.SingleDataRequestResponse",
        side_effect=ValidationError.from_exception_data(
            "SingleDataRequestResponse", []
        ),
    ):
        result = service.update_single_record(record, 999)

        assert result is None
        mock_logging.error.assert_called()
        assert (
            "SingleDataRequestResponse Validation Error"
            in mock_logging.error.call_args[0][0]
        )


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_update_multiple_record_success(mock_logging, service):
    """
    Test update_multiple_record with valid records including UID should return SubmissionResult.
    """
    records = [
        '{"fname": "test_name", "UID": "uid1"}',
        '{"fname": "test_name", "UID": "uid2"}',
    ]
    etid = 77
    mock_response = {
        "success": True,
        "data": {"EId": "id_batch", "ETId": etid, "ES": 20, "UID": ["uid1", "uid2"]},
    }

    with patch(
        "walacor_sdk.data_requests.data_requests_service.SingleDataRequestResponse",
        return_value=SingleDataRequestResponse(**mock_response),
    ):
        service.post = MagicMock(return_value=mock_response)
        result = service.update_multiple_record(records, etid)

        assert isinstance(result, SubmissionResult)
        service.post.assert_called_once_with(
            "envelopes/submit", json={"Data": records}, headers={"ETId": str(etid)}
        )
        mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_update_multiple_record_failure_flag(mock_logging, service):
    """
    Test update_multiple_record returns None and logs error if API returns success=False.
    """
    records = ['{"fname": "Charlie", "UID": "fail_uid"}']
    service.post = MagicMock(return_value={"success": False})
    result = service.update_multiple_record(records, 321)

    assert result is None
    mock_logging.error.assert_called_with("Failed to insert record")


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_update_multiple_record_validation_error(mock_logging, service):
    """
    Test update_multiple_record handles validation errors during parsing.
    """
    records = ['{"fname": "Test", "UID": "uid_val_err"}']
    service.post = MagicMock(return_value={"success": True, "data": {"bad": "data"}})

    with patch(
        "walacor_sdk.data_requests.data_requests_service.SingleDataRequestResponse",
        side_effect=ValidationError.from_exception_data(
            "SingleDataRequestResponse", []
        ),
    ):
        result = service.update_multiple_record(records, 555)

        assert result is None
        mock_logging.error.assert_called()
        assert (
            "SingleDataRequestResponse Validation Error"
            in mock_logging.error.call_args[0][0]
        )


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_update_single_record_missing_uid(mock_logging, service):
    """
    Should log error and return None if UID is missing in single record.
    """
    invalid_record = '{"fname": "Missing UID"}'
    result = service.update_single_record(invalid_record, 1)

    assert result is None
    mock_logging.error.assert_called_with("UID is required to update a record")


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_update_multiple_record_missing_uid(mock_logging, service):
    """
    Should log error and return None if any record in the list lacks UID.
    """
    records = ['{"fname": "Valid", "UID": "uid1"}', '{"fname": "Invalid"}']
    result = service.update_multiple_record(records, 42)

    assert result is None
    mock_logging.error.assert_called_with("UID is required in all records for update")
