"""API client for My Intercom integration."""

import logging
import time
from aiohttp import ClientSession
from urllib.parse import urljoin
from .models import Token, Intercom, UCamera, Contract
from typing import Any, List, Dict, Optional
from .const import (
    CONF_HOST,
    API_AUTH,
    API_CONTRACT,
    API_CAMERAS,
    API_INTERCOMS,
    API_OPEN_DOOR,
)
from .exceptions import UfanetIntercomAPIError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


class UfanetAPI:
    """API client for Ufanet."""

    def __init__(
        self,
        hass,
        contract: str,
        password: str,
    ):
        """Initialize API client."""
        self.hass = hass
        self._host = CONF_HOST
        self._contract = contract
        self._password = password
        self._token: Token | None = None
        self._session: ClientSession = async_get_clientsession(hass)
        self._maxretries = 3

    @property
    def token(self) -> Optional[str]:
        """Get current token."""
        return self._token.access

    async def _async_send_request(
        self,
        api_endpoint: str,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        headers = self._get_headers
        url = urljoin(self._host, api_endpoint)
        for attempt in range(self._max_retries + 1):
            try:
                async with self._session.request(
                    method, url, params=params, json=json, headers=headers
                ) as response:
                    if response.status == 401:
                        # Token expired, reauthenticate
                        await self.async_authenticate()
                        continue
                    response.raise_for_status()
                    data = await response.json()
                    return data
            except Exception as err:
                _LOGGER.error("Request error: %s", err)
                raise
            if attempt < self.max_retries:
                raise UfanetIntercomAPIError("Превышено количество попыток")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication."""
        if not self._token:
            raise Exception("No token available")

        return {
            "Authorization": f"Bearer {self._token.access}",
            "Content-Type": "application/json",
        }

    async def async_authenticate(self) -> Token:
        """Authenticate and get token."""
        json = {"contract": self._contract, "password": self._password}
        await self._async_send_request(api_endpoint=API_AUTH, method="POST", json=json)
        return True

    async def async_get_intercoms(self) -> List[Intercom]:
        """Get list of intercoms with RTSP URLs."""
        response = await self._async_send_request(api_endpoint=API_INTERCOMS)
        return [Intercom(**i) for i in response]

    async def async_get_cameras(self) -> List[UCamera]:
        """Get list of intercoms with RTSP URLs."""
        response = await self._async_send_request(api_endpoint=API_INTERCOMS)
        return [UCamera(**i) for i in response]

    async def async_get_balance(self) -> float:
        response = await self._async_send_request(api_endpoint=API_CONTRACT)
        return Contract(**response).balance

    async def async_open_door(self, intercom_id: str) -> bool:
        """Send open door command to intercom."""
        api_endpoint = f"{self._host}{API_OPEN_DOOR.format(intercom_id=intercom_id)}"
        await self._async_send_request(api_endpoint=api_endpoint, method="POST")
        return True
