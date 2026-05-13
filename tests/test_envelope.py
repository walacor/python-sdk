from unittest.mock import MagicMock, patch

import pytest

from pydantic import ValidationError

from walacor_sdk.envelope.envelope_service import EnvelopeService
from walacor_sdk.envelope.models.envelope_response import PostEnvelopeQueryResponse
from walacor_sdk.envelope.models.models import ReplayHistoryDetailed


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return EnvelopeService(mock_client)


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_query_envelopes_success_with_filter_and_pagination(mock_logging, service):
    mock_response = {
        "success": True,
        "data": [
            {
                "_id": "69dd0c7ec76f65c480761675",
                "UID": "uid-1",
                "pub_name": "Updated 1",
                "UpdatedAt": 1776094334506,
            },
            {
                "_id": "69dd0c7ec76f65c480761676",
                "UID": "uid-2",
                "pub_name": "Updated 2",
                "UpdatedAt": 1776094334507,
            },
        ],
        "total": 50,
        "pageNo": 2,
        "pageSize": 25,
        "totalPage": 2,
    }

    service._post = MagicMock(return_value=mock_response)

    result = service.query_envelopes(
        query={"pub_name": "Updated 1"},
        pageNo=2,
        pageSize=25,
        order="asc",
        orderBy="UpdatedAt",
        totalReq=True,
    )

    assert isinstance(result, PostEnvelopeQueryResponse)
    assert len(result.data) == 2
    assert result.data[0]["UID"] == "uid-1"
    assert result.total == 50
    assert result.pageNo == 2
    assert result.pageSize == 25
    assert result.totalPage == 2

    service._post.assert_called_once_with(
        "envelopes/query?pageNo=2&pageSize=25&order=asc&orderBy=UpdatedAt&totalReq=true",
        json={"pub_name": "Updated 1"},
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_query_envelopes_success_with_pipeline(mock_logging, service):
    mock_response = {
        "success": True,
        "data": [
            {
                "_id": "69dd0c7ec76f65c480761675",
                "UID": "uid-1",
                "pub_name": "Updated 1",
            }
        ],
    }

    pipeline = [
        {"$match": {"UID": "uid-1"}},
        {"$project": {"UID": 1, "pub_name": 1}},
    ]

    service._post = MagicMock(return_value=mock_response)

    result = service.query_envelopes(
        query=pipeline,
        pageNo=0,
        pageSize=10,
        totalReq=False,
    )

    assert isinstance(result, PostEnvelopeQueryResponse)
    assert len(result.data) == 1
    assert result.data[0]["UID"] == "uid-1"
    assert result.total is None
    assert result.pageNo is None
    assert result.pageSize is None
    assert result.totalPage is None

    service._post.assert_called_once_with(
        "envelopes/query?pageNo=0&pageSize=10&totalReq=false",
        json=pipeline,
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_query_envelopes_defaults_to_empty_filter(mock_logging, service):
    mock_response = {
        "success": True,
        "data": [],
    }

    service._post = MagicMock(return_value=mock_response)

    result = service.query_envelopes()

    assert isinstance(result, PostEnvelopeQueryResponse)
    assert result.data == []

    service._post.assert_called_once_with(
        "envelopes/query",
        json={},
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_query_envelopes_invalid_page_no(mock_logging, service):
    service._post = MagicMock()

    result = service.query_envelopes(
        query={},
        pageNo=-1,
        pageSize=10,
    )

    assert result is None
    service._post.assert_not_called()
    mock_logging.error.assert_called_once_with(
        "pageNo must be a non-negative integer when provided"
    )


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_query_envelopes_invalid_page_size(mock_logging, service):
    service._post = MagicMock()

    result = service.query_envelopes(
        query={},
        pageNo=0,
        pageSize=0,
    )

    assert result is None
    service._post.assert_not_called()
    mock_logging.error.assert_called_once_with(
        "pageSize must be a positive integer when provided"
    )


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_query_envelopes_invalid_order(mock_logging, service):
    service._post = MagicMock()

    result = service.query_envelopes(
        query={},
        order="ascending",
    )

    assert result is None
    service._post.assert_not_called()
    mock_logging.error.assert_called_once_with(
        "order must be either 'asc' or 'desc' when provided"
    )


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_query_envelopes_invalid_query_type(mock_logging, service):
    service._post = MagicMock()

    result = service.query_envelopes(
        query="not-a-valid-query",
    )

    assert result is None
    service._post.assert_not_called()
    mock_logging.error.assert_called_once_with(
        "query must be a dict, list of dicts, or None"
    )


@patch("walacor_sdk.base.base_service.logger")
def test_query_envelopes_failure_flag(mock_logging, service):
    service._post = MagicMock(return_value={"success": False})

    result = service.query_envelopes(query={})

    assert result is None
    mock_logging.error.assert_called_once()

    fmt, *args = mock_logging.error.call_args[0]
    rendered = fmt % tuple(args)
    assert "query_envelopes" in rendered


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_query_envelopes_validation_error(mock_logging, service):
    bad_response = {
        "success": True,
        "data": {"not": "a-list"},
    }

    service._post = MagicMock(return_value=bad_response)

    with patch(
        "walacor_sdk.envelope.envelope_service.PostEnvelopeQueryResponse",
        side_effect=ValidationError.from_exception_data(
            "PostEnvelopeQueryResponse", []
        ),
    ):
        result = service.query_envelopes(query={})

    assert result is None
    mock_logging.error.assert_called()
    assert (
        "PostEnvelopeQueryResponse Validation Error"
        in mock_logging.error.call_args[0][0]
    )


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_success(mock_logging, service):
    mock_response = {
        "success": True,
        "data": {
            "_id": "69dd0c7ec76f65c480761675",
            "pub_id": "1",
            "pub_name": "Updated 3",
            "UID": "8d68852c-0475-408a-9e8b-73b739d857e2",
            "UpdatedAt": 1776094334506,
            "EId": "1aac5015-8f0d-4626-96ae-95792405b572",
            "SV": 2,
        },
        "total": 5,
    }

    service._post = MagicMock(return_value=mock_response)

    result = service.get_replay_history(
        UID="8d68852c-0475-408a-9e8b-73b739d857e2",
        ETId=44556677,
        EId="1aac5015-8f0d-4626-96ae-95792405b572",
        updated_at=1776094334506,
    )

    assert isinstance(result, dict)
    assert result["UID"] == "8d68852c-0475-408a-9e8b-73b739d857e2"
    assert result["EId"] == "1aac5015-8f0d-4626-96ae-95792405b572"

    service._post.assert_called_once_with(
        "envelopes/history/replay",
        headers={"ETId": "44556677"},
        json={
            "UID": "8d68852c-0475-408a-9e8b-73b739d857e2",
            "EId": "1aac5015-8f0d-4626-96ae-95792405b572",
            "updated_at": 1776094334506,
        },
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_with_schema_version(mock_logging, service):
    mock_response = {
        "success": True,
        "data": {"UID": "test-uid", "pub_name": "Updated", "SV": 2},
    }

    service._post = MagicMock(return_value=mock_response)

    result = service.get_replay_history(
        UID="test-uid",
        ETId=123456,
        schemaVersion=2,
    )

    assert isinstance(result, dict)
    assert result["UID"] == "test-uid"
    assert result["SV"] == 2

    service._post.assert_called_once_with(
        "envelopes/history/replay",
        headers={"ETId": "123456", "SV": "2"},
        json={"UID": "test-uid"},
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_with_org_id(mock_logging, service):
    mock_response = {
        "success": True,
        "data": {"UID": "test-uid", "pub_name": "Updated"},
        "total": 2,
    }

    service._post = MagicMock(return_value=mock_response)

    result = service.get_replay_history(
        UID="test-uid",
        ETId=123456,
        org_id="org-1",
    )

    assert isinstance(result, dict)
    assert result["UID"] == "test-uid"

    service._post.assert_called_once_with(
        "envelopes/history/replay?ORGId=org-1",
        headers={"ETId": "123456"},
        json={"UID": "test-uid"},
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_detailed_success(mock_logging, service):
    mock_response = {
        "success": True,
        "data": {
            "result": {
                "UID": "8d68852c-0475-408a-9e8b-73b739d857e2",
                "pub_name": "Updated 3",
                "EId": "1aac5015-8f0d-4626-96ae-95792405b572",
                "UpdatedAt": 1776094334506,
            },
            "history": [
                {
                    "UID": "8d68852c-0475-408a-9e8b-73b739d857e2",
                    "pub_name": "Initial",
                    "EId": "older-event",
                    "UpdatedAt": 1776094282001,
                },
                {
                    "UID": "8d68852c-0475-408a-9e8b-73b739d857e2",
                    "pub_name": "Updated 3",
                    "EId": "1aac5015-8f0d-4626-96ae-95792405b572",
                    "UpdatedAt": 1776094334506,
                },
            ],
            "pagination": {
                "pageNo": 0,
                "pageSize": 10,
                "total": 2,
                "totalPage": 1,
            },
        },
    }

    service._post = MagicMock(return_value=mock_response)

    result = service.get_replay_history_detailed(
        UID="8d68852c-0475-408a-9e8b-73b739d857e2",
        ETId=44556677,
        EId="1aac5015-8f0d-4626-96ae-95792405b572",
    )

    assert isinstance(result, ReplayHistoryDetailed)
    assert result.result is not None
    assert result.result["pub_name"] == "Updated 3"
    assert len(result.history) == 2
    assert result.pagination.pageNo == 0
    assert result.pagination.pageSize == 10
    assert result.pagination.total == 2

    service._post.assert_called_once_with(
        "envelopes/history/replay/detailed",
        headers={"ETId": "44556677"},
        json={
            "UID": "8d68852c-0475-408a-9e8b-73b739d857e2",
            "EId": "1aac5015-8f0d-4626-96ae-95792405b572",
        },
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_detailed_with_org_id_and_pagination(mock_logging, service):
    mock_response = {
        "success": True,
        "data": {
            "result": {"UID": "test-uid", "pub_name": "Updated"},
            "history": [{"UID": "test-uid", "pub_name": "Updated"}],
            "pagination": {
                "pageNo": 1,
                "pageSize": 20,
                "total": 21,
                "totalPage": 2,
            },
        },
    }

    service._post = MagicMock(return_value=mock_response)

    result = service.get_replay_history_detailed(
        UID="test-uid",
        ETId=123456,
        org_id="org-1",
        pageNo=1,
        pageSize=20,
    )

    assert isinstance(result, ReplayHistoryDetailed)
    assert result.result is not None
    assert result.result["UID"] == "test-uid"
    assert result.pagination.pageNo == 1
    assert result.pagination.pageSize == 20
    assert result.pagination.total == 21

    service._post.assert_called_once_with(
        "envelopes/history/replay/detailed?ORGId=org-1&pageNo=1&pageSize=20",
        headers={"ETId": "123456"},
        json={"UID": "test-uid"},
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_detailed_with_schema_version(mock_logging, service):
    mock_response = {
        "success": True,
        "data": {
            "result": {"UID": "test-uid", "SV": 2},
            "history": [{"UID": "test-uid", "SV": 1}],
            "pagination": {
                "pageNo": 0,
                "pageSize": 10,
                "total": 1,
                "totalPage": 1,
            },
        },
    }

    service._post = MagicMock(return_value=mock_response)

    result = service.get_replay_history_detailed(
        UID="test-uid",
        ETId=123456,
        schemaVersion=2,
    )

    assert isinstance(result, ReplayHistoryDetailed)
    assert result.result is not None
    assert result.result["SV"] == 2

    service._post.assert_called_once_with(
        "envelopes/history/replay/detailed",
        headers={"ETId": "123456", "SV": "2"},
        json={"UID": "test-uid"},
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_invalid_uid(mock_logging, service):
    service._post = MagicMock()

    result = service.get_replay_history(
        UID="   ",
        ETId=44556677,
    )

    assert result is None
    service._post.assert_not_called()
    mock_logging.error.assert_called_once_with("UID must be a non-empty string")


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_invalid_eid(mock_logging, service):
    service._post = MagicMock()

    result = service.get_replay_history(
        UID="valid-uid",
        ETId=44556677,
        EId="   ",
    )

    assert result is None
    service._post.assert_not_called()
    mock_logging.error.assert_called_once_with(
        "EId must be a non-empty string when provided"
    )


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_invalid_updated_at(mock_logging, service):
    service._post = MagicMock()

    result = service.get_replay_history(
        UID="valid-uid",
        ETId=44556677,
        updated_at="1776094334506",
    )

    assert result is None
    service._post.assert_not_called()
    mock_logging.error.assert_called_once_with(
        "updated_at must be an integer timestamp when provided"
    )


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_invalid_updated_at_bool(mock_logging, service):
    service._post = MagicMock()

    result = service.get_replay_history(
        UID="valid-uid",
        ETId=44556677,
        updated_at=True,
    )

    assert result is None
    service._post.assert_not_called()
    mock_logging.error.assert_called_once_with(
        "updated_at must be an integer timestamp when provided"
    )


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_detailed_invalid_page_no(mock_logging, service):
    service._post = MagicMock()

    result = service.get_replay_history_detailed(
        UID="valid-uid",
        ETId=44556677,
        pageNo=-1,
        pageSize=10,
    )

    assert result is None
    service._post.assert_not_called()
    mock_logging.error.assert_called_once_with(
        "pageNo must be a non-negative integer when provided"
    )


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_detailed_invalid_page_size(mock_logging, service):
    service._post = MagicMock()

    result = service.get_replay_history_detailed(
        UID="valid-uid",
        ETId=44556677,
        pageNo=0,
        pageSize=0,
    )

    assert result is None
    service._post.assert_not_called()
    mock_logging.error.assert_called_once_with(
        "pageSize must be a positive integer when provided"
    )


@patch("walacor_sdk.base.base_service.logger")
def test_get_replay_history_failure_flag(mock_logging, service):
    service._post = MagicMock(return_value={"success": False})

    result = service.get_replay_history(
        UID="valid-uid",
        ETId=44556677,
    )

    assert result is None
    mock_logging.error.assert_called_once()

    fmt, *args = mock_logging.error.call_args[0]
    rendered = fmt % tuple(args)
    assert "get_replay_history" in rendered


@patch("walacor_sdk.base.base_service.logger")
def test_get_replay_history_detailed_failure_flag(mock_logging, service):
    service._post = MagicMock(return_value={"success": False})

    result = service.get_replay_history_detailed(
        UID="valid-uid",
        ETId=44556677,
    )

    assert result is None
    mock_logging.error.assert_called_once()

    fmt, *args = mock_logging.error.call_args[0]
    rendered = fmt % tuple(args)
    assert "get_replay_history_detailed" in rendered


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_validation_error(mock_logging, service):
    bad_response = {
        "success": True,
        "data": ["not-a-dict"],
        "total": 1,
    }

    service._post = MagicMock(return_value=bad_response)

    with patch(
        "walacor_sdk.envelope.envelope_service.GetReplayHistoryResponse",
        side_effect=ValidationError.from_exception_data("GetReplayHistoryResponse", []),
    ):
        result = service.get_replay_history(
            UID="valid-uid",
            ETId=44556677,
        )

    assert result is None
    mock_logging.error.assert_called()
    assert (
        "GetReplayHistoryResponse Validation Error"
        in mock_logging.error.call_args[0][0]
    )


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_detailed_validation_error(mock_logging, service):
    bad_response = {
        "success": True,
        "data": {
            "result": {"UID": "valid-uid"},
            "history": [{"UID": "valid-uid"}],
            # Missing pagination.total, which should make the model invalid.
            "pagination": {
                "pageNo": 0,
                "pageSize": 10,
            },
        },
    }

    service._post = MagicMock(return_value=bad_response)

    result = service.get_replay_history_detailed(
        UID="valid-uid",
        ETId=44556677,
    )

    assert result is None
    mock_logging.error.assert_called()
    assert (
        "GetReplayHistoryDetailedResponse Validation Error"
        in mock_logging.error.call_args[0][0]
    )
