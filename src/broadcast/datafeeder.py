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
    ctx (truststore.SSLContext): SSL context for secure connections.
    client (httpx.Client): HTTP client for making API requests.
    tokens (dict): Authentication tokens received after login.
    token (str): Current authentication token.
    refreshToken (str): Token used to refresh the authentication.

Examples:
    >>> client = Broadcast("username", "password")
    >>> quotes = client.get_quote(["PETR4", "VALE3"])
"""

__author__ = "Sylvio Campos Neto"
__license__ = "MIT"
__version__ = "0.1.2"
__email__ = "sylvio.campos@gmail.com.br"
__all__ = ["Broadcast"]

import httpx
from typing import Any


class Broadcast:
    def __init__(self, usr: str, pwd: str, keep_alive: bool = False) -> None:
        """
        Inicializa o cliente Broadcast, realiza login e armazena os tokens de autenticação.

        Args:
            usr (str): Nome de usuário para autenticação.
            pwd (str): Senha para autenticação.
            keep_alive (bool, opcional): Se True, mantém a sessão ativa. Padrão é False.
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
        self.refreshToken: str = self.tokens["refreshToken"]
        if keep_alive:
            self.keep_alive()

    def login(self, usr: str, pwd: str) -> dict[str, str]:
        """
        Realiza o login na API e retorna os tokens de autenticação.

        Args:
            usr (str): Nome de usuário.
            pwd (str): Senha.

        Returns:
            dict[str, str]: Dicionário contendo 'token' e 'refreshToken'.

        Raises:
            httpx.RequestError: Erro de conexão ou SSL.
            httpx.HTTPStatusError: Erro HTTP retornado pela API.
            Exception: Outros erros inesperados.
        """
        url: str = self.url + "Authentication/v1/login"
        try:
            response: httpx.Response = self.client.post(
                url=url,
                headers=self.headers,
                json={"applicationId": "datafeed", "login": usr, "password": pwd},
            )
            response.raise_for_status()  # Verifica por erros HTTP
            data: dict[str, Any] = response.json()
            tokens: dict[str, Any] = {
                "token": data["token"],
                "refreshToken": data["refreshToken"],
            }
            return tokens
        except httpx.RequestError as e:
            print(f"Erro SSL: {e}")
            raise
        except httpx.HTTPStatusError as e:
            print(f"Erro HTTP: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"Erro inesperado: {e}")
            raise

    def logout(self) -> dict[str, Any]:
        """
        Realiza logout na API, invalidando o token atual.

        Returns:
            dict[str, Any]: Resposta da API após logout.
        """
        url: str = self.url + "Authentication/v1/logout"
        self.client.headers["authorization"] = f"Bearer {self.token}"
        response: httpx.Response = self.client.get(url=url)
        return response.json()

    def keep_alive(self) -> dict[str, Any]:
        """
        Mantém a sessão ativa na API.

        Returns:
            dict[str, Any]: Resposta da API para o keep alive.
        """
        url: str = self.url + "Authentication/v1/keep"
        self.client.headers["authorization"] = f"Bearer {self.token}"
        response: httpx.Response = self.client.get(url=url)
        return response.json()

    def token_refresh(self) -> dict[str, Any] | bool:
        """
        Atualiza o token de autenticação usando o refreshToken.

        Returns:
            dict[str, Any]: Status da operação se bem-sucedida.
            bool: False em caso de erro.
        """
        url: str = self.url + "Authentication/v1/refresh"
        self.client.headers["authorization"] = f"Bearer {self.token}"
        try:
            response: httpx.Response = self.client.post(
                url=url, json={"refreshToken": self.refreshToken, "token": self.token}
            )
            data: dict[str, Any] = response.json()
            tokens: dict[str, Any] = {
                "token": data["token"],
                "refreshToken": data["refreshToken"],
            }
            self.token = tokens["token"]
            self.refreshToken = tokens["refreshToken"]
            rtr: dict[str, Any] = {"status": response.status_code, "success": True}
            return rtr
        except Exception as e:
            print(e)
            return False

    def get_quote(self, symbols: list[str], fields: list[str] = None) -> dict[str, Any]:
        """
        Obtém cotações de ativos financeiros.

        Args:
            symbols (list[str]): Lista de símbolos dos ativos.
            fields (list[str], opcional): Lista de campos desejados. Padrão é todos.

        Returns:
            dict[str, Any]: Dados das cotações ou mensagem de erro.
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
