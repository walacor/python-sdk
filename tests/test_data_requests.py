from unittest.mock import MagicMock, patch

import pytest

from pydantic import ValidationError

from walacor_sdk.data_requests.data_requests_service import DataRequestsService
from walacor_sdk.data_requests.models.models import SingleRecordDetail


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return DataRequestsService(mock_client)


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_insert_single_record_success(mock_logging, service):
    """"""
    mock_request = {
        "Data": [
            {
                "au_id": "1234",
                "au_lname": "l_test",
                "au_fname": "f_test",
                "phone": "9999999",
                "address": "test 999",
                "city": "test",
                "state": "TST",
                "zip": "9999",
                "contract": True,
            }
        ]
    }

    mock_response = {
        "success": True,
        "data": {"EId": "test", "ETId": 90000000, "ES": 30, "UID": ["213132"]},
    }

    service.get = MagicMock(return_value=mock_response)
    result = service.insert_single_record(mock_request, 90000000)

    assert isinstance(result, SingleRecordDetail)
    service.get.assert_called_once_with(
        "envelopes/submit", headers={"ETId": "90000000"}
    )
    mock_logging.info.assert_called_with("")


@patch("walacor_sdk.data_requests.data_requests_service.logging")
def test_insert_single_record_failure_flag(mock_logging, service):
    mock_request = {"test": "test"}
    service.get = MagicMock(return_value={"success": False})

    result = service.insert_single_record(mock_request, 123)

    assert result == []
    mock_logging.error.assert_called_with("Failed to fetch data")


@patch("walacor_sdk.schema.schema_service.logging")
def test_insert_single_record_validation_error(mock_logging, service):
    service.get = MagicMock(return_value={"success": True, "data": {"Invalid": {}}})

    with patch(
        "walacor_sdk.data_requests.data_requests_service.SingleDataRequestResponse",
        side_effect=ValidationError.from_exception_data(
            "SingleDataRequestResponse", []
        ),
    ):
        result = service.insert_single_record(9999)
        assert result == {}
        mock_logging.error.assert_called()
        assert "AutoGenFields Validation Error" in mock_logging.error.call_args[0][0]
