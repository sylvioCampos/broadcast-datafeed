# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

"""
Unit tests for the Broadcast client module.

This module contains tests for the Broadcast class in the datafeeder module,
ensuring the proper functionality of authentication, session management,
and data retrieval operations.

Tests cover:
- Client initialization
- Authentication (login, logout)
- Session management (token refresh, keep-alive)
- Data retrieval (quote requests)
- Error handling for various failure scenarios
"""

import pytest
from unittest.mock import ANY, MagicMock, patch
import httpx
from dotenv import load_dotenv
import os
import ssl
from broadcast_datafeed import Broadcast

def pytest_configure(config):
    """Load test environment variables before tests run."""
    load_dotenv(".env.test")


@pytest.fixture
def test_credentials():
    """Provide test credentials from environment variables."""
    return {
        "username": os.environ.get("BROADCAST_TEST_USER", "test_user"),
        "password": os.environ.get("BROADCAST_TEST_PASSWORD", "test_password")
    }


@pytest.fixture
def mock_httpx_client():
    """
    Fixture to mock the httpx.Client.

    Returns:
        MagicMock: A mocked instance of httpx.Client with pre-configured responses.
    """
    with patch("httpx.Client") as mock_client:
        client_instance = MagicMock()
        # Make headers a real dict so assignment works and can be asserted
        client_instance.headers = {}
        mock_client.return_value = client_instance

        # Setup default login response
        login_response = MagicMock()
        login_response.json.return_value = {
            "token": "fake_token",
            "refreshToken": "fake_refresh_token",
        }
        login_response.status_code = 200
        client_instance.post.return_value = login_response

        # Setup default get response
        get_response = MagicMock()
        get_response.json.return_value = {"status": "success"}
        client_instance.get.return_value = get_response

        yield client_instance


class TestBroadcast:
    """Test suite for the Broadcast class."""

    def test_init(self, mock_httpx_client):
        """Tests if initialization correctly sets up attributes."""
        broadcast = Broadcast("test_user", "test_password")

        assert broadcast.usr == "test_user"
        assert broadcast.pwd == "test_password"
        assert broadcast.url == "https://svc.aebroadcast.com.br/"
        assert broadcast.token == "fake_token"
        assert broadcast.refreshToken == "fake_refresh_token"
        assert "accept" in broadcast.headers
        assert "Content-Type" in broadcast.headers

        # Verify that login is called during initialization
        mock_httpx_client.post.assert_called_once()

    def test_init_with_keep_alive(self, mock_httpx_client):
        """Tests if initialization with keep_alive=True calls keep_alive method."""
        # Setup keep_alive response
        keep_alive_response = MagicMock()
        keep_alive_response.json.return_value = {"status": "session_extended"}
        mock_httpx_client.get.return_value = keep_alive_response

        # Execute
        broadcast = Broadcast("test_user", "test_password", keep_alive=True)

        # Assert
        assert broadcast.usr == "test_user"
        assert broadcast.token == "fake_token"
        # Verify keep_alive was called after login
        mock_httpx_client.get.assert_called_once_with(
            url="https://svc.aebroadcast.com.br/Authentication/v1/keep"
        )

    def test_init_with_ssl_verification(self, mock_httpx_client):
        """Tests if initialization respects verify_ssl parameter."""
        with patch("httpx.Client") as mock_client_class:
            client_instance = MagicMock()
            client_instance.headers = {}
            mock_client_class.return_value = client_instance

            login_response = MagicMock()
            login_response.json.return_value = {
                "token": "fake_token",
                "refreshToken": "fake_refresh_token",
            }
            client_instance.post.return_value = login_response

            # Test with verify_ssl=True (default)
            _ = Broadcast("test_user", "test_password", verify_ssl=True)
            mock_client_class.assert_called_with(
                headers={"accept": "application/json", "Content-Type": "application/json"},
                timeout=None,
                verify=ANY,
            )
            verify_arg = mock_client_class.call_args.kwargs["verify"]
            assert isinstance(verify_arg, ssl.SSLContext)

            # Test with verify_ssl=False
            mock_client_class.reset_mock()
            _ = Broadcast("test_user", "test_password", verify_ssl=False)
            mock_client_class.assert_called_with(
                headers={"accept": "application/json", "Content-Type": "application/json"},
                timeout=None,
                verify=False
            )

    def test_init_with_ssl_pem_path_loads_custom_ca(self):
        """Tests if ssl_pem_path is loaded into the SSL context when provided."""
        with (
            patch("broadcast_datafeed.datafeed.certifi.where") as mock_certifi_where,
            patch("broadcast_datafeed.datafeed.ssl.create_default_context") as mock_create_default_context,
            patch("httpx.Client") as mock_client_class,
        ):
            mock_certifi_where.return_value = "/tmp/cacert.pem"
            ssl_context = MagicMock()
            mock_create_default_context.return_value = ssl_context

            client_instance = MagicMock()
            client_instance.headers = {}
            mock_client_class.return_value = client_instance

            login_response = MagicMock()
            login_response.json.return_value = {
                "token": "fake_token",
                "refreshToken": "fake_refresh_token",
            }
            client_instance.post.return_value = login_response

            _ = Broadcast(
                "test_user",
                "test_password",
                verify_ssl=True,
                ssl_pem_path="/path/custom-ca.pem",
            )

            mock_create_default_context.assert_called_once_with(cafile="/tmp/cacert.pem")
            ssl_context.load_verify_locations.assert_called_once_with(
                cafile="/path/custom-ca.pem"
            )
            assert mock_client_class.call_args.kwargs["verify"] is ssl_context

    def test_login_success(self, mock_httpx_client, test_credentials):
        """Tests if login is successful."""
        broadcast = Broadcast(
            test_credentials["username"], test_credentials["password"]
        )
        tokens = broadcast.login("test_user", "test_password")

        assert tokens["token"] == "fake_token"
        assert tokens["refreshToken"] == "fake_refresh_token"

        # Verify request was made with correct parameters
        mock_httpx_client.post.assert_called_with(
            url="https://svc.aebroadcast.com.br/Authentication/v1/login",
            headers=broadcast.headers,
            json={
                "applicationId": "datafeed",
                "login": "test_user",
                "password": "test_password",
            },
        )

    def test_login_request_error(self, mock_httpx_client):
        """Tests if login properly handles request errors."""
        mock_httpx_client.post.side_effect = httpx.RequestError(
            "Connection error", request=MagicMock()
        )

        with pytest.raises(httpx.RequestError):
            Broadcast("test_user", "test_password")

    def test_login_http_error(self, mock_httpx_client):
        """Tests if login properly handles HTTP errors."""
        response = MagicMock()
        response.status_code = 401
        response.text = "Unauthorized"
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized", request=MagicMock(), response=response
        )
        mock_httpx_client.post.return_value = response

        with pytest.raises(httpx.HTTPStatusError):
            Broadcast("test_user", "test_password")

    def test_login_unexpected_error(self, mock_httpx_client):
        """Tests if login re-raises unexpected errors (generic Exception handler)."""
        broadcast = Broadcast("test_user", "test_password")

        mock_httpx_client.post.reset_mock()
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.side_effect = ValueError("Invalid JSON")
        mock_httpx_client.post.return_value = response

        with pytest.raises(ValueError):
            broadcast.login("test_user", "test_password")

    def test_refresh_token_property_setter(self, mock_httpx_client):
        """Tests the backward-compatible refreshToken property setter."""
        broadcast = Broadcast("test_user", "test_password")
        broadcast.refreshToken = "new_refresh_token"

        assert broadcast.refresh_token == "new_refresh_token"
        assert broadcast.refreshToken == "new_refresh_token"

    def test_logout(self, mock_httpx_client):
        """Tests if logout is performed correctly."""
        # Setup
        logout_response = MagicMock()
        logout_response.json.return_value = {
            "success": False,
            "code": "bc_01104",
            "message": "The user session is disconnected",
        }
        mock_httpx_client.get.return_value = logout_response

        # Execute
        broadcast = Broadcast("test_user", "test_password")
        result = broadcast.logout()

        # Assert
        assert result == {
            "success": False,
            "code": "bc_01104",
            "message": "The user session is disconnected",
        }
        mock_httpx_client.get.assert_called_with(
            url="https://svc.aebroadcast.com.br/Authentication/v1/logout"
        )
        assert broadcast.client.headers["authorization"] == "Bearer fake_token"

    def test_logout_request_error(self, mock_httpx_client):
        """Tests if logout properly handles request errors."""
        broadcast = Broadcast("test_user", "test_password")
        mock_httpx_client.get.side_effect = httpx.RequestError(
            "Connection error", request=MagicMock()
        )

        with pytest.raises(httpx.RequestError):
            broadcast.logout()

    def test_logout_http_error(self, mock_httpx_client):
        """Tests if logout properly handles HTTP errors."""
        broadcast = Broadcast("test_user", "test_password")
        response = MagicMock()
        response.status_code = 401
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized", request=MagicMock(), response=response
        )
        mock_httpx_client.get.return_value = response

        with pytest.raises(httpx.HTTPStatusError):
            broadcast.logout()

    def test_keep_alive(self, mock_httpx_client):
        """Tests if keep_alive is performed correctly."""
        # Setup
        keep_alive_response = MagicMock()
        keep_alive_response.json.return_value = {"status": "session_extended"}
        mock_httpx_client.get.return_value = keep_alive_response

        # Execute
        broadcast = Broadcast("test_user", "test_password")
        result = broadcast.keep_alive()

        # Assert
        assert result == {"status": "session_extended"}
        mock_httpx_client.get.assert_called_with(
            url="https://svc.aebroadcast.com.br/Authentication/v1/keep"
        )

    def test_keep_alive_request_error(self, mock_httpx_client):
        """Tests if keep_alive properly handles request errors."""
        broadcast = Broadcast("test_user", "test_password")
        mock_httpx_client.get.side_effect = httpx.RequestError(
            "Connection error", request=MagicMock()
        )

        with pytest.raises(httpx.RequestError):
            broadcast.keep_alive()

    def test_keep_alive_http_error(self, mock_httpx_client):
        """Tests if keep_alive properly handles HTTP errors."""
        broadcast = Broadcast("test_user", "test_password")
        response = MagicMock()
        response.status_code = 401
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized", request=MagicMock(), response=response
        )
        mock_httpx_client.get.return_value = response

        with pytest.raises(httpx.HTTPStatusError):
            broadcast.keep_alive()

    def test_token_refresh_success(self, mock_httpx_client):
        """Tests if token refresh is successful."""
        # Setup login response (used at __init__)
        login_response = MagicMock()
        login_response.json.return_value = {
            "token": "fake_token",
            "refreshToken": "fake_refresh_token",
        }
        login_response.status_code = 200
        mock_httpx_client.post.return_value = login_response

        # login consumed by instance
        broadcast = Broadcast("test_user", "test_password")
        mock_httpx_client.post.assert_called_once()  # login call

        # Setup refresh response
        refresh_response = MagicMock()
        refresh_response.json.return_value = {
            "token": "new_token",
            "refreshToken": "new_refresh_token",
        }
        refresh_response.status_code = 200

        # mock subscriber
        mock_httpx_client.post.reset_mock()
        mock_httpx_client.post.return_value = refresh_response

        # Execute
        result = broadcast.token_refresh()

        # Assert
        assert result == {"status": 200, "success": True}
        assert broadcast.token == "new_token"
        assert broadcast.refreshToken == "new_refresh_token"
        mock_httpx_client.post.assert_called_once_with(
            url="https://svc.aebroadcast.com.br/Authentication/v1/refresh",
            json={"refreshToken": "fake_refresh_token", "token": "fake_token"},
        )

    def test_token_refresh_failure(self, mock_httpx_client):
        """Tests if token refresh properly handles failures."""
        # 1) First, let login succeed (using the fixture’s default login_response)
        broadcast = Broadcast("test_user", "test_password")
        mock_httpx_client.post.assert_called_once()  # login was called

        # 2) Now reset post and simulate failure on refresh only
        mock_httpx_client.post.reset_mock()
        mock_httpx_client.post.side_effect = Exception("Refresh failed")

        # 3) Execute refresh
        result = broadcast.token_refresh()

        # 4) Assert it returned False and post was called exactly once
        assert result is False
        mock_httpx_client.post.assert_called_once_with(
            url="https://svc.aebroadcast.com.br/Authentication/v1/refresh",
            json={"refreshToken": "fake_refresh_token", "token": "fake_token"},
        )

    def test_get_quote_success(self, mock_httpx_client):
        """Tests if quote retrieval is successful."""
        # Setup quote response
        quote_response = MagicMock()
        quote_data = {
            "data": {
                "PETR4": {"ULT": "28,50", "VAR": "1,25%"},
                "VALE3": {"ULT": "68,45", "VAR": "-0,50%"},
            }
        }
        quote_response.json.return_value = quote_data

        # 1) Instantiate and consume the login (login mock already configured)
        broadcast = Broadcast("test_user", "test_password")
        mock_httpx_client.post.assert_called_once()

        # 2) Reset and inject the quote mock
        mock_httpx_client.post.reset_mock()
        mock_httpx_client.post.return_value = quote_response

        # 3) Execute and assert behavior
        result = broadcast.get_quote(symbols=["PETR4", "VALE3"], fields=["ULT", "VAR"])

        # Assert
        assert result == quote_data
        mock_httpx_client.post.assert_called_with(
            url="https://svc.aebroadcast.com.br/stock/v1/quote/request",
            json={"symbols": ["PETR4", "VALE3"], "fields": ["ULT", "VAR"]},
        )

    def test_get_quote_with_fields(self, mock_httpx_client):
        """Tests quote retrieval with specific fields."""
        # Setup
        quote_response = MagicMock()
        quote_data = {
            'data': {
                "PETR4": {'ULT': '32,09', 'COD': 'PETR4'}, 
                "VALE3": {'ULT': '55,35', 'COD': 'VALE3'},
            }    
        }
        quote_response.json.return_value = quote_data
        # 1) Instantiate and consume the login (login mock already configured)
        broadcast = Broadcast("test_user", "test_password")
        mock_httpx_client.post.assert_called_once()

        # 2) Reset and inject the quote mock
        mock_httpx_client.post.reset_mock()
        mock_httpx_client.post.return_value = quote_response

        result = broadcast.get_quote(symbols=["PETR4", "VALE3"], fields=["ULT"])

        # Assert
        assert result == quote_data
        mock_httpx_client.post.assert_called_with(
            url="https://svc.aebroadcast.com.br/stock/v1/quote/request",
            json={"symbols": ["PETR4", "VALE3"], "fields": ["ULT"]},
        )

    def test_get_quote_failure(self, mock_httpx_client):
        """Tests if quote retrieval properly handles failures."""
        # Setup & execute
        broadcast = Broadcast("test_user", "test_password")
        mock_httpx_client.post.reset_mock()  # Reset mock to ignore login call
        mock_httpx_client.post.side_effect = httpx.RequestError(
            "API error", request=MagicMock()
        )

        with pytest.raises(httpx.RequestError):
            broadcast.get_quote(symbols=["PETR4", "VALE3"])

    def test_get_quote_http_error(self, mock_httpx_client):
        """Tests if quote retrieval properly handles HTTP errors."""
        broadcast = Broadcast("test_user", "test_password")
        mock_httpx_client.post.reset_mock()
        response = MagicMock()
        response.status_code = 500
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=MagicMock(), response=response
        )
        mock_httpx_client.post.return_value = response

        with pytest.raises(httpx.HTTPStatusError):
            broadcast.get_quote(symbols=["PETR4", "VALE3"])
