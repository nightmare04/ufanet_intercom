"""API client for My Intercom integration."""

import asyncio
import logging
from typing import Any
from urllib.parse import urljoin
from json.decoder import JSONDecodeError
from aiohttp.client_exceptions import ClientConnectorError, ContentTypeError

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from aiohttp import ClientSession, ClientTimeout

from .const import (
    API_BASE_URL,
    API_AUTH,
    API_CAMERAS,
    API_CONTRACT,
    API_INTERCOMS,
    API_OPEN_DOOR,
    DOMAIN,
)
from .exceptions import (
    UfanetIntercomAPIError,
    UnknownUfanetIntercomAPIError,
    UnauthorizedUfanetIntercomAPIError,
    TimeoutUfanetIntercomAPIError,
)
from .models import Contract, Intercom, Token, UCamera

_LOGGER = logging.getLogger(__name__)


class UfanetAPI:
    """API client for Ufanet."""

    def __init__(
        self,
        hass,
        contract: str,
        password: str,
    ) -> None:
        """Initialize API client."""
        self.hass = hass
        self._contract_number = contract
        self._password = password
        self._contract: Contract | None = None
        self._token: Token | None = None
        self._session: ClientSession = async_get_clientsession(hass)

    async def _send_request(
        self,
        api_endpoint: str,
        method: str = "GET",
        base_url: str = API_BASE_URL,
        params: dict[str, Any] = None,
        json: dict[str, Any] = None,
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        url = urljoin(base_url, api_endpoint)
        while True:
            try:
                # If token unavalible, try to auth
                if not self._token:
                    _LOGGER.debug(f"{DOMAIN} Unavalible token, trying auth...")
                    with self._session.request(
                        url=f"{base_url}{API_AUTH}",
                        method="POST",
                        json={
                            "contract": self._contract_number,
                            "password": self._password,
                        },
                    ) as response:
                        json_response = await response.json()

                    if response.status == 401:
                        raise UnauthorizedUfanetIntercomAPIError(
                            f"Ошибка, неверные имя пользователя или пароль: {response.status}"
                        )
                    if response.status == 200:
                        self._token = Token(**json_response)
                        _LOGGER.debug(f"{DOMAIN} Auth success, resend request.")
                        continue
                    raise UnknownUfanetIntercomAPIError(json_response)
                # Request
                with self._session.request(
                    url=url,
                    method=method,
                    json=json,
                    params=params,
                    headers=self._get_headers(),
                ) as response:
                    json_response = (
                        await response.json() if 199 < response.status < 500 else None
                    )
                    return json_response
                raise UnknownUfanetIntercomAPIError(json_response)

            except (JSONDecodeError, ContentTypeError) as e:
                raise UnknownUfanetIntercomAPIError(
                    f"Неизвестная ошибка: {response.status} {response.reason}, {e}"
                )
            except asyncio.exceptions.TimeoutError:
                raise TimeoutUfanetIntercomAPIError("Timeout error")

    def _get_headers(self) -> dict[str, Any]:
        headers = {{"Authorization": f"JWT {self._token.access}"}}
        return headers

    async def get_contract(self):
        response = await self._send_request(api_endpoint=API_CONTRACT)
        self._contract_number = Contract(**response)

    async def get_intercoms(self) -> Contract:
        response = await self._send_request(api_endpoint=API_INTERCOMS)
        return [Intercom(**i) for i in response]

    async def get_cameras(self) -> Contract:
        response = await self._send_request(api_endpoint=API_CAMERAS)
        return [UCamera(**i) for i in response]

    async def open_door(self, intercom_id: int) -> bool:
        api_endpoint = f"api/v0/skud/shared/{intercom_id}/open/"
        response = await self._send_request(api_endpoint=api_endpoint)
        return response["result"]
