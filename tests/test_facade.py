from unittest.mock import patch

from walacor_sdk.base.facade import Facade
from walacor_sdk.base.w_client import W_Client

BASE_URL = "http://fakeapi.com"
USERNAME = "testuser"
PASSWORD = "testpass"
TEST_ENDPOINT = "test-endpoint"


def test_sdk_facade_auth_service_lazy_loading():
    """Test that SDKFacade properly initializes AuthService lazily"""
    with patch(
        "walacor_sdk.authentication.auth_service.AuthService", autospec=True
    ) as mock_auth_service:
        client = W_Client(BASE_URL, USERNAME, PASSWORD)
        facade = Facade(client=client, auth_service_cls=mock_auth_service)

        assert facade._auth is None

        _ = facade.auth

        assert facade._auth is not None
        mock_auth_service.assert_called_once_with(client)
