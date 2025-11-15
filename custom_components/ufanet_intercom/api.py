"""API client for My Intercom integration."""

import logging
from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientSession

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_AUTH,
    API_CAMERAS,
    API_CONTRACT,
    API_INTERCOMS,
    API_OPEN_DOOR,
    CONF_HOST,
)
from .exceptions import UfanetIntercomAPIError
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
        self._host = "https://dom.ufanet.ru/"
        self._contract = contract
        self._password = password
        self._token: Token | None = None
        self._session: ClientSession = async_get_clientsession(hass)

    async def async_authenticate(self) -> bool:
        """Authenticate and get token."""
        json = {"contract": self._contract, "password": self._password}
        try:
            async with self._session.post(
                f"{self._host}{API_AUTH}", json=json, timeout=30
            ) as response:
                response.raise_for_status()
                data = await response.json()
                self._token = Token(**data["token"])
                return True
        except Exception as err:
            _LOGGER.error("Error auth: %s", err)
            raise

    async def async_get_intercoms(self) -> list[Intercom]:
        """Get list of intercoms with RTSP URLs."""
        if not self._token:
            await self.async_authenticate()
        try:
            async with self._session.get(
                f"{self._host}{API_INTERCOMS}",
                headers={"Authorization": f"JWT {self._token.access}"},
                timeout=30,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return [Intercom(**i) for i in data]
        except Exception as err:
            _LOGGER.error("Error fetching intercoms list: %s", err)
            raise

    async def async_get_cameras(self) -> list[UCamera]:
        """Get list of intercoms with RTSP URLs."""
        if not self._token:
            await self.async_authenticate()
        try:
            async with self._session.get(
                f"{self._host}{API_CAMERAS}",
                headers={"Authorization": f"JWT {self._token.access}"},
                timeout=30,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return [UCamera(**i) for i in data]
        except Exception as err:
            _LOGGER.error("Error fetching cameras list: %s", err)
            raise

    async def async_get_balance(self) -> float:
        """Get balance."""
        return 100

    async def async_open_door(self, intercom_id: str) -> bool:
        """Send open door command to intercom."""
        api_endpoint = f"{self._host}{API_OPEN_DOOR.format(intercom_id=intercom_id)}"
        if not self._token:
            await self.async_authenticate()
        try:
            async with self._session.get(
                api_endpoint,
                headers={"Authorization": f"JWT {self._token.access}"},
                timeout=30,
            ) as response:
                response.raise_for_status()
                return True
        except Exception as err:
            _LOGGER.error("Error fetching cameras list: %s", err)
            raise
