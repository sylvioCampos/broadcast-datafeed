# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

"""
Broadcast client for interacting with the AEBroadcast API service.

This class provides authentication and methods to interact with AEBroadcast's
financial data services, including retrieving stock quotes.

Attributes:
    url (str): The base URL for the AEBroadcast API.
    usr (str): Username for authentication.
    pwd (str): Password for authentication.
    headers (dict): HTTP headers used for requests.
    client (httpx.Client): HTTP client for making API requests.
    tokens (dict): Authentication tokens received after login.
    token (str): Current authentication token.
    refresh_token (str): Token used to refresh the authentication (camelCase alias available).

Security Note:
    For production environments, always use verify_ssl=True (default) to ensure
    secure HTTPS connections. Setting verify_ssl=False disables SSL certificate
    verification and should only be used in development/testing environments.

    When verify_ssl=True, this client configures certificate verification via an
    ssl.SSLContext (built with certifi's CA bundle by default). You can also
    provide an additional custom CA bundle path via ssl_pem_path.

Examples:
    >>> client = Broadcast("username", "password")
    >>> quotes = client.get_quote(["PETR4", "VALE3"])

    Production (with SSL verification - recommended):
    >>> client = Broadcast("username", "password", verify_ssl=True)

    Development only (without SSL verification):
    >>> client = Broadcast("username", "password", verify_ssl=False)

    Custom CA bundle (additional trust store):
    >>> client = Broadcast(
    ...     "username",
    ...     "password",
    ...     verify_ssl=True,
    ...     ssl_pem_path="/path/to/custom-ca.pem",
    ... )
"""

from __future__ import annotations

__author__ = "Sylvio Campos Neto"
__license__ = "MIT"
__version__ = "1.1.0"
__email__ = "sylvio.campos@gmail.com.br"
__all__ = ["Broadcast"]

from typing import Any

import httpx
import certifi
import ssl

class Broadcast:
    """
    Client for interacting with the AEBroadcast API.

    This class provides authentication and methods to interact with AEBroadcast's
    financial data services, including retrieving stock quotes.

    Attributes:
        url (str): Base URL of the AEBroadcast API.
        usr (str): Username for authentication.
        pwd (str): Password for authentication.
        headers (dict[str, str]): HTTP headers used in requests.
        client (httpx.Client): HTTP client for making API requests.
        tokens (dict[str, Any]): Authentication tokens received after login.
        token (str): Current authentication token.
        refresh_token (str): Token used to refresh authentication.

    Examples:
        Basic usage:
        >>> client = Broadcast("username", "password")
        >>> quotes = client.get_quote(["PETR4", "VALE3"])
        >>> print(quotes)
        {'data': {'PETR4': {...}, 'VALE3': {...}}}
        >>> client.logout()

        With keep_alive:
        >>> client = Broadcast("username", "password", keep_alive=True)
        >>> # Session will be kept alive automatically
    """

    def __init__(
        self,
        usr: str,
        pwd: str,
        keep_alive: bool = False,
        verify_ssl: bool = True,
        ssl_pem_path: str | None = None,
    ) -> None:
        """
        Initialize the Broadcast client, perform login, and store authentication tokens.

        Args:
            usr (str): Username used for authentication.
            pwd (str): Password used for authentication.
            keep_alive (bool, optional): If True, keeps the session alive. Default: False.
            verify_ssl (bool, optional): If True, verifies SSL certificates. Default: True.
                For development, can be set to False, but not recommended for
                production due to security concerns.
            ssl_pem_path (str, optional): Path to a PEM-encoded CA bundle file.
                When provided, it will be loaded into the SSL context in addition
                to certifi's default CA bundle. Default: None.

        Raises:
            httpx.RequestError: Connection or SSL error during login.
            httpx.HTTPStatusError: HTTP error returned by the API during login.

        Examples:
            >>> client = Broadcast("my_username", "my_password")
            >>> print(client.token)
            'eyJhbGc...'  # Authentication token

            With keep_alive:
            >>> client = Broadcast("username", "password", keep_alive=True)
            >>> # Session will be kept alive automatically

            Development (without SSL verification - NOT RECOMMENDED FOR PRODUCTION):
            >>> client = Broadcast("username", "password", verify_ssl=False)
        """
        self.url = "https://svc.aebroadcast.com.br/"
        self.usr: str = usr
        self.pwd: str = pwd
        self.headers: dict[str, str] = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        if verify_ssl:
            self.ssl_context: ssl.SSLContext | None = ssl.create_default_context(cafile=certifi.where())
            if ssl_pem_path:
                self.ssl_context.load_verify_locations(cafile=ssl_pem_path)
            self.client = httpx.Client(
                headers=self.headers,
                timeout=None,
                verify=self.ssl_context,
            )
        else:
            self.ssl_context = None
            self.client = httpx.Client(
                headers=self.headers,
                timeout=None,
                verify=False,
            )
        self.tokens: dict[str, Any] = self.login(usr, pwd)
        self.token: str = self.tokens["token"]
        self.refresh_token: str = self.tokens["refreshToken"]
        if keep_alive:
            self.keep_alive()

    def login(self, usr: str, pwd: str) -> dict[str, str]:
        """
        Perform login against the API and return authentication tokens.

        Args:
            usr (str): Username used during login.
            pwd (str): Password used during login.

        Returns:
            dict[str, str]: Dictionary containing 'token' and 'refreshToken'.

        Raises:
            httpx.RequestError: Connection or SSL error.
            httpx.HTTPStatusError: HTTP error returned by the API.
            Exception: Any other unexpected error.

        Examples:
            >>> client = Broadcast("username", "password")
            >>> tokens = client.login("username", "password")
            >>> print(tokens['token'])
            'eyJhbGc...'
        """
        url: str = self.url + "Authentication/v1/login"
        try:
            response: httpx.Response = self.client.post(
                url=url,
                headers=self.headers,
                json={"applicationId": "datafeed", "login": usr, "password": pwd},
            )
            response.raise_for_status()  # Check for HTTP errors
            data: dict[str, Any] = response.json()
            tokens: dict[str, Any] = {
                "token": data["token"],
                "refreshToken": data["refreshToken"],
            }
            return tokens
        except httpx.RequestError as e:
            print(f"SSL error: {e}")
            raise
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    def logout(self) -> dict[str, Any]:
        """
        Log out from the API, invalidating the current token.

        Returns:
            dict[str, Any]: Response from the API after logout.

        Raises:
            httpx.RequestError: Connection or SSL error.
            httpx.HTTPStatusError: HTTP error returned by the API.

        Examples:
            >>> client = Broadcast("username", "password")
            >>> result = client.logout()
            >>> print(result)
            {'success': False, 'code': 'bc_01104', 'message': 'Session disconnected'}
        """
        url: str = self.url + "Authentication/v1/logout"
        self.client.headers["authorization"] = f"Bearer {self.token}"
        try:
            response: httpx.Response = self.client.get(url=url)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            print(f"Request error during logout: {e}")
            raise
        except httpx.HTTPStatusError as e:
            print(f"HTTP error during logout: {e.response.status_code}")
            raise

    def keep_alive(self) -> dict[str, Any]:
        """
        Keep the current API session alive.

        Returns:
            dict[str, Any]: Response from the API for the keep-alive request.

        Raises:
            httpx.RequestError: Connection or SSL error.
            httpx.HTTPStatusError: HTTP error returned by the API.

        Examples:
            >>> client = Broadcast("username", "password")
            >>> result = client.keep_alive()
            >>> print(result)
            {'status': 'session_extended'}
        """
        url: str = self.url + "Authentication/v1/keep"
        self.client.headers["authorization"] = f"Bearer {self.token}"
        try:
            response: httpx.Response = self.client.get(url=url)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            print(f"Request error during keep_alive: {e}")
            raise
        except httpx.HTTPStatusError as e:
            print(f"HTTP error during keep_alive: {e.response.status_code}")
            raise

    def token_refresh(self) -> dict[str, Any] | bool:
        """
        Refresh the authentication token using the refresh token.

        Returns:
            dict[str, Any]: Result of the refresh operation when successful.
                Contains 'status' (int) and 'success' (bool).
            bool: False in case of error.

        Examples:
            >>> client = Broadcast("username", "password")
            >>> result = client.token_refresh()
            >>> if result["success"]:
            ...     print("Token refreshed successfully")
            ...     print(f"New token: {client.token}")
            Token refreshed successfully
            New token: eyJhbGc...
        """
        url: str = self.url + "Authentication/v1/refresh"
        self.client.headers["authorization"] = f"Bearer {self.token}"
        try:
            response: httpx.Response = self.client.post(
                url=url, json={"refreshToken": self.refresh_token, "token": self.token}
            )
            data: dict[str, Any] = response.json()
            tokens: dict[str, Any] = {
                "token": data["token"],
                "refreshToken": data["refreshToken"],
            }
            self.token = tokens["token"]
            self.refresh_token = tokens["refreshToken"]
            rtr: dict[str, Any] = {"status": response.status_code, "success": True}
            return rtr
        except Exception as e:
            print(e)
            return False

    def get_quote(
        self, symbols: list[str], fields: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Retrieve quotes for the requested financial instruments.

        Args:
            symbols (list[str]): List of instrument symbols (e.g., ["PETR4", "VALE3"]).
            fields (list[str], optional): List of desired fields (e.g., ["ULT", "VAR"]).
                If None, returns all available fields. Default: None.

        Returns:
            dict[str, Any]: Quote payload or error message.

        Raises:
            httpx.RequestError: Connection or SSL error.
            httpx.HTTPStatusError: HTTP error returned by the API.

        Examples:
            Request all fields:
            >>> client = Broadcast("username", "password")
            >>> quotes = client.get_quote(["PETR4", "VALE3"])
            >>> print(quotes)
            {'data': {'PETR4': {'ULT': '28.50', 'VAR': '1.25%'}, ...}}

            Request specific fields:
            >>> quotes = client.get_quote(
            ...     symbols=["PETR4", "VALE3"],
            ...     fields=["ULT", "VAR"]
            ... )
            >>> print(quotes['data']['PETR4']['ULT'])
            '28.50'
        """
        if fields is None:
            fields = []
        url: str = self.url + "stock/v1/quote/request"
        self.client.headers["authorization"] = f"Bearer {self.token}"
        try:
            response: httpx.Response = self.client.post(
                url=url, json={"symbols": symbols, "fields": fields}
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            return data
        except httpx.RequestError as e:
            print(f"Request error during get_quote: {e}")
            raise
        except httpx.HTTPStatusError as e:
            print(f"HTTP error during get_quote: {e.response.status_code}")
            raise

    @property
    def refreshToken(self) -> str:
        """Backward-compatible camelCase alias for refresh_token."""
        return self.refresh_token

    @refreshToken.setter
    def refreshToken(self, value: str) -> None:
        self.refresh_token = value
