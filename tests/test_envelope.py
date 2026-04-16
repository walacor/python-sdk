from unittest.mock import MagicMock, patch

import pytest

from pydantic import ValidationError

from walacor_sdk.envelope.envelope_service import EnvelopeService
from walacor_sdk.envelope.models.models import ReplayHistoryDetailed


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return EnvelopeService(mock_client)


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
        },
        "total": 5,
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

    service._post.assert_called_once_with(
        "envelopes/history/replay?detailed=true",
        headers={"ETId": "44556677"},
        json={
            "UID": "8d68852c-0475-408a-9e8b-73b739d857e2",
            "EId": "1aac5015-8f0d-4626-96ae-95792405b572",
        },
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.envelope.envelope_service.logger")
def test_get_replay_history_detailed_with_org_id(mock_logging, service):
    mock_response = {
        "success": True,
        "data": {
            "result": {"UID": "test-uid", "pub_name": "Updated"},
            "history": [{"UID": "test-uid", "pub_name": "Updated"}],
        },
        "total": 1,
    }

    service._post = MagicMock(return_value=mock_response)

    result = service.get_replay_history_detailed(
        UID="test-uid",
        ETId=123456,
        org_id="org-1",
    )

    assert isinstance(result, ReplayHistoryDetailed)
    assert result.result is not None
    assert result.result["UID"] == "test-uid"

    service._post.assert_called_once_with(
        "envelopes/history/replay?detailed=true&ORGId=org-1",
        headers={"ETId": "123456"},
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
def test_get_replay_history_detailed_returns_none_when_backend_returns_non_detailed_payload(
    mock_logging, service
):
    mock_response = {
        "success": True,
        "data": {
            "UID": "8d68852c-0475-408a-9e8b-73b739d857e2",
            "pub_name": "Updated 3",
            "EId": "1aac5015-8f0d-4626-96ae-95792405b572",
        },
        "total": 5,
    }

    service._post = MagicMock(return_value=mock_response)

    result = service.get_replay_history_detailed(
        UID="8d68852c-0475-408a-9e8b-73b739d857e2",
        ETId=44556677,
        EId="1aac5015-8f0d-4626-96ae-95792405b572",
    )

    assert result is None
    mock_logging.error.assert_called()
    assert (
        "Detailed replay history requested, but backend returned non-detailed payload"
        in mock_logging.error.call_args[0][0]
    )
