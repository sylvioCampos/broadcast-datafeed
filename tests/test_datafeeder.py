# -*- coding: utf-8 -*-
# Copyright (c) 2025 Sylvio Neto
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
from unittest.mock import patch, MagicMock
import httpx
from dotenv import load_dotenv
import os
from broadcast import Broadcast

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
            broadcast = Broadcast("test_user", "test_password")

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
            broadcast = Broadcast("test_user", "test_password")

    def test_logout(self, mock_httpx_client):
        """Tests if logout is performed correctly."""
        # Setup
        logout_response = MagicMock()
        logout_response.json.return_value = {
            'success': False, 
            'code': 'bc_01104', 
            'message': 'A sessão do usuário está desconectada'
        }
        mock_httpx_client.get.return_value = logout_response

        # Execute
        broadcast = Broadcast("test_user", "test_password")
        result = broadcast.logout()

        # Assert
        assert result == {
            'success': False, 
            'code': 'bc_01104', 
            'message': 'A sessão do usuário está desconectada'
        }
        mock_httpx_client.get.assert_called_with(
            url="https://svc.aebroadcast.com.br/Authentication/v1/logout"
        )
        assert broadcast.client.headers["authorization"] == "Bearer fake_token"

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
        # Setup
        mock_httpx_client.post.side_effect = Exception("Refresh failed")

        # Execute
        broadcast = Broadcast("test_user", "test_password")
        mock_httpx_client.post.reset_mock()  # Reset mock to ignore login call
        mock_httpx_client.post.side_effect = Exception("Refresh failed")
        result = broadcast.token_refresh()

        # Assert
        assert result is False

    def test_get_quote_success(self, mock_httpx_client):
        """Tests if quote retrieval is successful."""
        # Setup
        quote_response = MagicMock()
        quote_data = {
            "symbols": {
                "PETR4": {"price": 28.50, "change": 1.25},
                "VALE3": {"price": 68.45, "change": -0.50},
            }
        }
        quote_response.json.return_value = quote_data
        mock_httpx_client.post.return_value = quote_response

        # Execute
        broadcast = Broadcast("test_user", "test_password")
        mock_httpx_client.post.reset_mock()  # Reset mock to ignore login call
        result = broadcast.get_quote(symbols=["PETR4", "VALE3"])

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
        quote_data = {"symbols": {"PETR4": {"price": 28.50}, "VALE3": {"price": 68.45}}}
        quote_response.json.return_value = quote_data
        mock_httpx_client.post.return_value = quote_response

        # Execute
        broadcast = Broadcast("test_user", "test_password")
        mock_httpx_client.post.reset_mock()  # Reset mock to ignore login call
        result = broadcast.get_quote(symbols=["PETR4", "VALE3"], fields=["price"])

        # Assert
        assert result == quote_data
        mock_httpx_client.post.assert_called_with(
            url="https://svc.aebroadcast.com.br/stock/v1/quote/request",
            json={"symbols": ["PETR4", "VALE3"], "fields": ["price"]},
        )

    def test_get_quote_failure(self, mock_httpx_client):
        """Tests if quote retrieval properly handles failures."""
        # Setup
        mock_httpx_client.post.side_effect = Exception("API error")

        # Execute
        broadcast = Broadcast("test_user", "test_password")
        mock_httpx_client.post.reset_mock()  # Reset mock to ignore login call
        mock_httpx_client.post.side_effect = Exception("API error")
        result = broadcast.get_quote(symbols=["PETR4", "VALE3"])

        # Assert
        assert result["success"] is False
        assert "API error" in result["message"]
