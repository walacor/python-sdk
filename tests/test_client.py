from unittest.mock import MagicMock, patch

import pytest

from walacor_sdk.base.w_client import W_Client

BASE_URL = "http://fakeapi.com"
USERNAME = "testuser"
PASSWORD = "testpass"
TEST_ENDPOINT = "test-endpoint"


def test_client_authenticate_success():
    """Test that W_Client successfully authenticates and stores token"""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"api_token": "fake_token"}
        mock_post.return_value = mock_response

        client = W_Client(BASE_URL, USERNAME, PASSWORD)
        client.authenticate()

        mock_post.assert_called_once_with(
            f"{BASE_URL}/auth/login",
            json={"userName": USERNAME, "password": PASSWORD},
            headers={"Content-Type": "application/json"},
        )

        assert (
            client.token == "fake_token"
        ), f"Expected 'fake_token' but got {client.token}"


def test_client_authenticate_failure():
    """Test that W_Client raises an exception on failed authentication"""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        client = W_Client(BASE_URL, USERNAME, PASSWORD)

        with pytest.raises(Exception, match="Authentication failed"):
            client.authenticate()


def test_client_request_with_authentication():
    """Test that W_Client adds the authentication token in headers"""
    with patch("requests.post") as mock_post, patch("requests.request") as mock_request:
        # Mock authentication response
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {"api_token": "fake_token"}
        mock_post.return_value = mock_auth_response

        # Mock request response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        client = W_Client(BASE_URL, USERNAME, PASSWORD)
        client.authenticate()

        response = client.request("GET", TEST_ENDPOINT)

        assert response == mock_response
        mock_request.assert_called_once_with(
            "GET",
            f"{BASE_URL}/{TEST_ENDPOINT}",
            headers={
                "Authorization": "fake_token",
                "Content-Type": "application/json",
            },
        )


def test_client_request_reauth_on_401():
    """Test that W_Client re-authenticates and retries on 401 Unauthorized"""
    with patch("requests.post") as mock_post, patch("requests.request") as mock_request:
        # Mock authentication response
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {"api_token": "fake_token"}
        mock_post.return_value = mock_auth_response

        # Mock request response (First 401, then success)
        mock_unauth_response = MagicMock()
        mock_unauth_response.status_code = 401

        mock_success_response = MagicMock()
        mock_success_response.status_code = 200

        mock_request.side_effect = [mock_unauth_response, mock_success_response]

        client = W_Client(BASE_URL, USERNAME, PASSWORD)

        client._token = "expired_token"

        response = client.request("GET", TEST_ENDPOINT)

        assert response == mock_success_response
        assert client.token == "fake_token"

        assert mock_post.call_count == 1
        assert mock_request.call_count == 2
