# -*- coding: utf-8 -*-
# Copyright (c) 2025 Sylvio Neto
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

Examples:
    >>> client = Broadcast("username", "password")
    >>> quotes = client.get_quote(["PETR4", "VALE3"])
"""

__author__ = "Sylvio Campos Neto"
__license__ = "MIT"
__version__ = "0.1.3"
__email__ = "sylvio.campos@gmail.com.br"
__all__ = ["Broadcast"]

from typing import Any

import httpx


class Broadcast:
    def __init__(self, usr: str, pwd: str, keep_alive: bool = False) -> None:
        """
        Initialize the Broadcast client, perform login, and store auth tokens.

        Args:
            usr (str): Username used for authentication.
            pwd (str): Password used for authentication.
            keep_alive (bool, optional): If True, keeps the session alive. Defaults to False.
        """
        self.url = "https://svc.aebroadcast.com.br/"
        self.usr: str = usr
        self.pwd: str = pwd
        self.headers: dict[str, str] = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        self.client = httpx.Client(headers=self.headers, timeout=None, verify=False)
        self.tokens: dict[str, Any] = self.login(usr, pwd)
        self.token: str = self.tokens["token"]
        self.refresh_token: str = self.tokens["refreshToken"]
        if keep_alive:
            self.keep_alive()

    def login(self, usr: str, pwd: str) -> dict[str, str]:
        """
        Perform login against the API and return the authentication tokens.

        Args:
            usr (str): Username used during login.
            pwd (str): Password used during login.

        Returns:
            dict[str, str]: Dictionary containing 'token' and 'refreshToken'.

        Raises:
            httpx.RequestError: Connection or SSL error.
            httpx.HTTPStatusError: HTTP error returned by the API.
            Exception: Any other unexpected error.
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
        """
        url: str = self.url + "Authentication/v1/logout"
        self.client.headers["authorization"] = f"Bearer {self.token}"
        response: httpx.Response = self.client.get(url=url)
        return response.json()

    def keep_alive(self) -> dict[str, Any]:
        """
        Keep the current API session alive.

        Returns:
            dict[str, Any]: Response from the API for the keep-alive request.
        """
        url: str = self.url + "Authentication/v1/keep"
        self.client.headers["authorization"] = f"Bearer {self.token}"
        response: httpx.Response = self.client.get(url=url)
        return response.json()

    def token_refresh(self) -> dict[str, Any] | bool:
        """
        Refresh the authentication token using the refresh token.

        Returns:
            dict[str, Any]: Outcome of the refresh operation when successful.
            bool: False in case of an error.
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
            symbols (list[str]): List of instrument symbols.
            fields (list[str], optional): List of desired fields. Defaults to all fields.

        Returns:
            dict[str, Any]: Quote payload or an error message.
        """
        if fields is None:
            fields = []
        url: str = self.url + "stock/v1/quote/request"
        self.client.headers["authorization"] = f"Bearer {self.token}"
        try:
            response: httpx.Response = self.client.post(
                url=url, json={"symbols": symbols, "fields": fields}
            )
            data: dict[str, Any] = response.json()
            return data
        except Exception as e:
            data: dict[str, Any] = {"success": False, "message": str(e)}
            return data

    @property
    def refreshToken(self) -> str:
        """Backward-compatible camelCase alias for refresh_token."""
        return self.refresh_token

    @refreshToken.setter
    def refreshToken(self, value: str) -> None:
        self.refresh_token = value
