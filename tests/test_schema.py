from unittest.mock import MagicMock, patch

import pytest

from pydantic import ValidationError

from walacor_sdk.schema.models.models import AutoGenField, IntegerField
from walacor_sdk.schema.schema_service import SchemaService


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return SchemaService(mock_client)


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_data_types_success(mock_logging, service):
    """Test successful parsing of get_data_types with valid response."""
    mock_response = {
        "success": True,
        "data": [
            {"Name": "INTEGER", "DefaultValue": 0, "MinValue": 0, "MaxValue": 100}
        ],
    }
    service.get = MagicMock(return_value=mock_response)

    result = service.get_data_types()

    assert len(result) == 1
    assert isinstance(result[0], IntegerField)
    assert result[0].Name == "INTEGER"
    mock_logging.info.assert_called_with("Fetching data types...")


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_data_types_failure_flag(mock_logging, service):
    """Test get_data_types returns empty list when success flag is False."""
    service.get = MagicMock(return_value={"success": False})

    result = service.get_data_types()

    assert result == []
    mock_logging.error.assert_called_with("Failed to fetch data")


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_data_types_validation_error(mock_logging, service):
    """Test get_data_types handles ValidationError and logs it."""
    # Mock response with invalid structure to trigger validation error
    service.get = MagicMock(return_value={"success": True, "data": [{}]})

    with patch(
        "walacor_sdk.schema.schema_service.SchemaResponse",
        side_effect=ValidationError.from_exception_data("SchemaResponse", []),
    ):
        result = service.get_data_types()

        assert result == []
        mock_logging.error.assert_called()
        assert "Schema Validation Error" in mock_logging.error.call_args[0][0]


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_platform_auto_generation_fields_success(mock_logging, service):
    """Test successful parsing of get_platform_auto_generation_fields with valid response."""
    mock_response = {
        "success": True,
        "data": {
            "FieldA": {
                "FieldName": "FieldA",
                "DataType": "TEXT",
                "Required": True,
                "SystemGenerated": False,
            }
        },
    }
    service.get = MagicMock(return_value=mock_response)

    result = service.get_platform_auto_generation_fields()

    assert isinstance(result, dict)
    assert "FieldA" in result
    assert isinstance(result["FieldA"], AutoGenField)
    assert result["FieldA"].FieldName == "FieldA"
    mock_logging.info.assert_called_with("Fetching platform auto-generation fields...")


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_platform_auto_generation_fields_failure_flag(mock_logging, service):
    """Test get_platform_auto_generation_fields returns empty dict when success flag is False."""
    service.get = MagicMock(return_value={"success": False})

    result = service.get_platform_auto_generation_fields()

    assert result == {}
    mock_logging.error.assert_called_with(
        "Failed to fetch platform auto-generation fields"
    )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_platform_auto_generation_fields_validation_error(mock_logging, service):
    """Test get_platform_auto_generation_fields handles ValidationError and logs it."""
    # Mock response with invalid structure to trigger validation error
    service.get = MagicMock(return_value={"success": True, "data": {"Invalid": {}}})

    with patch(
        "walacor_sdk.schema.schema_service.AutoGenFieldsResponse",
        side_effect=ValidationError.from_exception_data("AutoGenFieldsResponse", []),
    ):
        result = service.get_platform_auto_generation_fields()

        assert result == {}
        mock_logging.error.assert_called()
        assert "AutoGenFields Validation Error" in mock_logging.error.call_args[0][0]
