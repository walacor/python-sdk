from unittest.mock import MagicMock, patch

import pytest

from pydantic import ValidationError

from walacor_sdk.data_requests.data_requests_service import DataRequestsService
from walacor_sdk.data_requests.models.data_request_response import (
    SingleDataRequestResponse,
)
from walacor_sdk.data_requests.models.models import SubmissionResult

# ------------------------------> FIXTURES


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return DataRequestsService(mock_client)


# ------------------------------> INSERT SINGLE RECORD


@patch("walacor_sdk.data_requests.data_requests_service.logger")
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

    service._post = MagicMock(return_value=mock_response)

    result = service.insert_single_record(mock_request, 90000000)

    assert isinstance(result, SubmissionResult)
    assert result.ETId == 90000000
    service._post.assert_called_once_with(
        "envelopes/submit", json={"Data": [mock_request]}, headers={"ETId": "90000000"}
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_insert_single_record_failure_flag(mock_logging, service):
    """Test insert_single_record returns None and logs error if success=False in API response."""
    mock_request = {"Data": "test"}
    service._post = MagicMock(return_value={"success": False})

    result = service.insert_single_record(mock_request, 123)

    assert result is None
    mock_logging.error.assert_called_once_with("Failed to insert record")


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_insert_single_record_validation_error(mock_logging, service):
    """Test insert_single_record handles ValidationError and logs it properly."""
    mock_request = {"some": "payload"}
    bad_response = {"success": True, "data": {"invalid": "structure"}}
    service._post = MagicMock(return_value=bad_response)

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


# ------------------------------> INSERT MULTIPLE RECORDS


@patch("walacor_sdk.data_requests.data_requests_service.logger")
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

    service._post = MagicMock(return_value=mock_response)

    result = service.insert_single_record(mock_request, 90000000)

    assert isinstance(result, SubmissionResult)
    assert result.ETId == 90000000
    service._post.assert_called_once_with(
        "envelopes/submit", json={"Data": [mock_request]}, headers={"ETId": "90000000"}
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_insert_multiple_records_failure_flag(mock_logging, service):
    """Test insert_single_record returns None and logs error if success=False in API response."""
    mock_request = {"test": "test"}
    service._post = MagicMock(return_value={"success": False})

    result = service.insert_single_record(mock_request, 123)

    assert result is None
    mock_logging.error.assert_called_once_with("Failed to insert record")


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_insert_multiple_records_validation_error(mock_logging, service):
    """Test insert_single_record handles ValidationError and logs it properly."""
    mock_request = {"some": "payload"}
    bad_response = {"success": True, "data": {"invalid": "structure"}}
    service._post = MagicMock(return_value=bad_response)

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


# ------------------------------> UPDATE SINGLE RECORD


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_update_single_record_with_UID_success(mock_logging, service):
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
        service._post = MagicMock(return_value=mock_response)
        result = service.update_single_record_with_UID(record, etid)

        assert isinstance(result, SubmissionResult)
        service._post.assert_called_once_with(
            "envelopes/submit", json={"Data": [record]}, headers={"ETId": str(etid)}
        )
        mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_update_single_record_with_UID_failure_flag(mock_logging, service):
    """
    Test update_single_record returns None and logs error if response.success is False.
    """
    record = {"fname": "Bob", "UID": "uid_fail"}
    service._post = MagicMock(return_value={"success": False})
    result = service.update_single_record_with_UID(record, 123)

    assert result is None
    mock_logging.error.assert_called_with("Failed to update record")


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_update_single_record_with_UID_validation_error(mock_logging, service):
    """
    Test update_single_record_with_UID returns None and logs validation error on schema mismatch.
    """
    record = '{"fname": "Mismatch", "UID": "uid_val"}'
    service._post = MagicMock(
        return_value={"success": True, "data": {"invalid": "yes"}}
    )

    with patch(
        "walacor_sdk.data_requests.data_requests_service.SingleDataRequestResponse",
        side_effect=ValidationError.from_exception_data(
            "SingleDataRequestResponse", []
        ),
    ):
        result = service.update_single_record_with_UID(record, 999)

        assert result is None
        mock_logging.error.assert_called()
        assert (
            "SingleDataRequestResponse Validation Error"
            in mock_logging.error.call_args[0][0]
        )


# ------------------------------> UPDATE MULTIPLE RECORDS


@patch("walacor_sdk.data_requests.data_requests_service.logger")
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
        service._post = MagicMock(return_value=mock_response)
        result = service.update_multiple_record(records, etid)

        assert isinstance(result, SubmissionResult)
        service._post.assert_called_once_with(
            "envelopes/submit", json={"Data": records}, headers={"ETId": str(etid)}
        )
        mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_update_multiple_record_failure_flag(mock_logging, service):
    """
    Test update_multiple_record returns None and logs error if API returns success=False.
    """
    records = ['{"fname": "Charlie", "UID": "fail_uid"}']
    service._post = MagicMock(return_value={"success": False})
    result = service.update_multiple_record(records, 321)

    assert result is None
    mock_logging.error.assert_called_with("Failed to update records")


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_update_multiple_record_validation_error(mock_logging, service):
    """
    Test update_multiple_record handles validation errors during parsing.
    """
    records = ['{"fname": "Test", "UID": "uid_val_err"}']
    service._post = MagicMock(return_value={"success": True, "data": {"bad": "data"}})

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


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_update_single_record_missing_uid(mock_logging, service):
    """
    Should log error and return None if UID is missing in single record.
    """
    invalid_record = {"fname": "Missing UID"}
    result = service.update_single_record_with_UID(invalid_record, 1)

    assert result is None
    mock_logging.error.assert_called_with("UID is required to update a record")


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_update_multiple_record_missing_uid(mock_logging, service):
    """
    Should log error and return None if any record in the list lacks UID.
    """
    records = ['{"fname": "Valid", "UID": "uid1"}', '{"fname": "Invalid"}']
    result = service.update_multiple_record(records, 42)

    assert result is None
    mock_logging.error.assert_called_with("UID is required in all records for update")


# ------------------------------> GET ALL RECORDS


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_get_all_success(mock_logging, service):
    """Test get_all returns list of records when response is valid."""
    mock_records = [
        {
            "_id": "test1233",
            "test_id": "123",
            "title": "My test",
            "UID": "test12",
            "IsDeleted": False,
            "CreatedAt": 1234233,
            "ORGId": "test",
            "UpdatedAt": 453331133,
            "EId": "test",
            "SV": 2,
            "LastModifiedBy": "tester",
        }
    ]

    mock_response = {"success": True, "data": mock_records}
    service._post = MagicMock(return_value=mock_response)

    result = service.get_all(ETId=123, pageNumber=1, pageSize=0, fromSummary=False)

    assert result == mock_records
    service._post.assert_called_once_with(
        "query/get?pageNo=1&pageSize=0&fromSummary=false", headers={"ETId": "123"}
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_get_all_failure_flag(mock_logging, service):
    """Test get_all returns None and logs error when response.success is False."""
    service._post = MagicMock(return_value={"success": False})

    result = service.get_all(ETId=123)

    assert result is None
    mock_logging.error.assert_called_once_with("Failed to fetch all records")


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_get_all_validation_error(mock_logging, service):
    """Test get_all returns None and logs ValidationError when parsing fails."""
    service._post = MagicMock(return_value={"success": True, "data": [{}]})

    with patch(
        "walacor_sdk.data_requests.data_requests_service.GetAllRecordsResponse",
        side_effect=ValidationError.from_exception_data("GetAllRecordsResponse", []),
    ):
        result = service.get_all(ETId=123)

        assert result is None
        mock_logging.error.assert_called()
        assert (
            "GetAllRecordsResponse Validation Error"
            in mock_logging.error.call_args[0][0]
        )


# ------------------------------> GET SINGLE RECORD


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_get_single_record_by_record_id_success(mock_logging, service):
    """Test get_single_record_by_record_id returns list of matching records when response is valid."""

    mock_response = {
        "success": True,
        "data": [
            {
                "_id": "abc",
                "test_id": "123",
                "title": "My test",
                "UID": "testUID",
                "IsDeleted": False,
                "CreatedAt": 1234,
                "ORGId": "testORGId",
                "UpdatedAt": 1234,
                "EId": "test_EID",
                "SV": 2,
                "LastModifiedBy": "test_user",
            }
        ],
    }

    service._post = MagicMock(return_value=mock_response)

    record_id = {"test_id": "123"}

    result = service.get_single_record_by_record_id(record_id, ETId=999)

    assert result == mock_response["data"]
    service._post.assert_called_once_with(
        "query/get?fromSummary=false",
        headers={"ETId": "999"},
        json=record_id,
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_get_single_record_by_record_id_failure_flag(mock_logging, service):
    """Test get_single_record_by_record_id returns None and logs error on failed response."""
    service._post = MagicMock(return_value={"success": False})

    result = service.get_single_record_by_record_id("au321", 42)

    assert result is None
    mock_logging.error.assert_called_once_with("Failed to fetch single record")


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_get_single_record_by_record_id_validation_error(mock_logging, service):
    """Test get_single_record_by_record_id handles and logs validation errors."""
    service._post = MagicMock(return_value={"success": True, "data": [{}]})

    with patch(
        "walacor_sdk.data_requests.data_requests_service.GetSingleRecordResponse",
        side_effect=ValidationError.from_exception_data("GetSingleRecordResponse", []),
    ):
        result = service.get_single_record_by_record_id("au999", 10)

        assert result is None
        mock_logging.error.assert_called()
        assert (
            "GetSingleRecordResponse Validation Error"
            in mock_logging.error.call_args[0][0]
        )


# ------------------------------> COMPLEX QUERY


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_post_complex_query_success(mock_logging, service):
    """Test post_complex_query returns ComplexQueryRecords when response is valid."""
    mock_response = {"success": True, "data": [{"row": "data"}], "total": 1}
    service._post = MagicMock(return_value=mock_response)

    with patch(
        "walacor_sdk.data_requests.data_requests_service.GetComplexQueryResponse",
        return_value=MagicMock(data=[{"row": "data"}], Total=1),
    ):
        result = service.post_complex_query(ETId=101, pipeline=[{"match": "criteria"}])

        assert result.Total == 1
        assert isinstance(result.Records, list)
        service._post.assert_called_once_with(
            "query/getcomplex",
            headers={"ETId": "101"},
            json=[{"match": "criteria"}],
        )
        mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_post_complex_query_failure_flag(mock_logging, service):
    """Test post_complex_query returns None and logs error when API fails."""
    service._post = MagicMock(return_value={"success": False})

    result = service.post_complex_query(ETId=5, pipeline=[])

    assert result is None
    mock_logging.error.assert_called_once_with("Failed to fetch complex query results")


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_post_complex_query_validation_error(mock_logging, service):
    """Test post_complex_query handles and logs ValidationError on bad data."""
    service._post = MagicMock(return_value={"success": True, "data": [{}], "Total": 5})

    with patch(
        "walacor_sdk.data_requests.data_requests_service.GetComplexQueryResponse",
        side_effect=ValidationError.from_exception_data("GetComplexQueryResponse", []),
    ):
        result = service.post_complex_query(ETId=33, pipeline=[{}])

        assert result is None
        mock_logging.error.assert_called()
        assert "Complex Query Parsing Error" in mock_logging.error.call_args[0][0]


# ------------------------------> QUERY API


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_post_query_api_success(mock_logging, service):
    """Test post_query_api returns list of records on valid response."""
    mock_response = {"success": True, "data": ["row1", "row2"]}
    service._post = MagicMock(return_value=mock_response)

    with patch(
        "walacor_sdk.data_requests.data_requests_service.QueryApiResponse",
        return_value=MagicMock(data=["row1", "row2"]),
    ):
        result = service.post_query_api(ETId=22, payload={"some": "query"})

        assert result == ["row1", "row2"]
        service._post.assert_called_once_with(
            "query/get?pageNo=1&pageSize=0",
            headers={"ETId": "22", "SV": "1"},
            json={"some": "query"},
        )
        mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_post_query_api_failure_flag(mock_logging, service):
    """Test post_query_api returns None and logs error when response is unsuccessful."""
    service._post = MagicMock(return_value={"success": False})

    result = service.post_query_api(ETId=7, payload={"bad": "query"})

    assert result is None
    mock_logging.error.assert_called_once_with("Failed to fetch query results")


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_post_query_api_validation_error(mock_logging, service):
    """Test post_query_api handles and logs validation error on malformed response."""
    service._post = MagicMock(return_value={"success": True, "data": [{}]})

    with patch(
        "walacor_sdk.data_requests.data_requests_service.QueryApiResponse",
        side_effect=ValidationError.from_exception_data("QueryApiResponse", []),
    ):
        result = service.post_query_api(ETId=5, payload={})

        assert result is None
        mock_logging.error.assert_called()
        assert "QueryApiResponse Validation Error" in mock_logging.error.call_args[0][0]


# ------------------------------> QUERY API AGGREGATE


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_post_query_api_aggregate_success(mock_logging, service):
    """Test post_query_api_aggregate returns QueryApiAggregate on valid input."""
    mock_response = {
        "success": True,
        "data": [{"agg": "value"}],
        "Total": 3,
    }
    service._post = MagicMock(return_value=mock_response)

    with patch(
        "walacor_sdk.data_requests.data_requests_service.QueryApiAggregateResponse",
        return_value=MagicMock(data=[{"agg": "value"}], Total=3),
    ):
        result = service.post_query_api_aggregate(payload={"agg": "test"})

        assert result.Total == 3
        assert isinstance(result.Records, list)
        service._post.assert_called_once_with(
            "query/getComplex",
            headers={"ETId": "10", "SV": "1", "DV": "1"},
            json={"agg": "test"},
        )
        mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_post_query_api_aggregate_failure_flag(mock_logging, service):
    """Test post_query_api_aggregate returns None and logs error when API fails."""
    service._post = MagicMock(return_value={"success": False})

    result = service.post_query_api_aggregate(payload={})

    assert result is None
    mock_logging.error.assert_called_once_with("Failed to fetch aggregate results")


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_post_query_api_aggregate_validation_error(mock_logging, service):
    """Test post_query_api_aggregate logs validation error and returns None."""
    service._post = MagicMock(return_value={"success": True, "data": [{}], "Total": 0})

    with patch(
        "walacor_sdk.data_requests.data_requests_service.QueryApiAggregateResponse",
        side_effect=ValidationError.from_exception_data(
            "QueryApiAggregateResponse", []
        ),
    ):
        result = service.post_query_api_aggregate(payload={})

        assert result is None
        mock_logging.error.assert_called()
        assert (
            "QueryApiAggregateResponse Validation Error"
            in mock_logging.error.call_args[0][0]
        )


# ------------------------------> COMPLEX MQL


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_post_complex_MQL_queries_success(mock_logging, service):
    """Test post_complex_MQL_queries returns ComplexQMLQueryRecords on success."""
    mock_response = {"success": True, "data": [{"q": "s"}], "Total": 99}
    service._post = MagicMock(return_value=mock_response)

    with patch(
        "walacor_sdk.data_requests.data_requests_service.GetComplexQMLQueryResponse",
        return_value=MagicMock(data=[{"q": "s"}], Total=99),
    ):
        result = service.post_complex_MQL_queries(
            ETId=77, pipeline=[{"stage": "match"}]
        )

        assert result.Total == 99
        assert isinstance(result.Records, list)
        service._post.assert_called_once_with(
            "query/getcomplex", headers={"ETId": "77"}, json=[{"stage": "match"}]
        )
        mock_logging.error.assert_not_called()


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_post_complex_MQL_queries_failure_flag(mock_logging, service):
    """Test post_complex_MQL_queries logs and returns None on failure."""
    service._post = MagicMock(return_value={"success": False})

    result = service.post_complex_MQL_queries(ETId=7, pipeline=[])

    assert result is None
    mock_logging.error.assert_called_once_with("Failed to fetch MQL query results")


@patch("walacor_sdk.data_requests.data_requests_service.logger")
def test_post_complex_MQL_queries_validation_error(mock_logging, service):
    """Test post_complex_MQL_queries logs and returns None on invalid response."""
    service._post = MagicMock(return_value={"success": True, "data": [{}], "Total": 0})

    with patch(
        "walacor_sdk.data_requests.data_requests_service.GetComplexQMLQueryResponse",
        side_effect=ValidationError.from_exception_data(
            "GetComplexQMLQueryResponse", []
        ),
    ):
        result = service.post_complex_MQL_queries(ETId=11, pipeline=[])

        assert result is None
        mock_logging.error.assert_called()
        assert (
            "GetComplexQMLQueryResponse Validation Error"
            in mock_logging.error.call_args[0][0]
        )
