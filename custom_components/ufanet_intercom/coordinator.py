"""DataCoordinator Ufanet."""

from datetime import timedelta
import logging
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import UfanetAPI
from .const import DOMAIN, UPDATE_INTERVAL
from .models import Intercom, UCamera

_LOGGER = logging.getLogger(__name__)


class UfanetDataCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.entry = entry
        self.api = UfanetAPI(
            hass=hass, contract=entry.data["contract"], password=entry.data["password"]
        )
        self.intercoms: list[Intercom] = []
        self.cameras: list[UCamera] = []

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def async_authenticate(self):
        """Perform authentication and update config entry."""
        await self.api.async_authenticate()
        # Update config entry with new token
        hass = self.hass
        new_data = {**self.entry.data}
        new_data["token"] = self.api.token

        hass.config_entries.async_update_entry(self.entry, data=new_data)

        _LOGGER.debug("Authentication successful")

    async def async_initialize_intercoms(self):
        """Initialize intercoms list on startup."""
        self.intercoms = await self.api.async_get_intercoms()
        self.cameras = await self.api.async_get_cameras()
        _LOGGER.debug("Found %d intercoms", len(self.intercoms))

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API - только баланс, камеры обновляются отдельно."""
        try:
            # Initialize intercoms if not done yet
            await self.async_initialize_intercoms()

            # Fetch only balance (cameras handle their own updates via RTSP)
            balance_data = await self.api.async_get_balance()

            # Handle balance exception
            if isinstance(balance_data, Exception):
                _LOGGER.error("Balance data error: %s", balance_data)
                balance_data = 0

            return {
                "intercoms": self.intercoms,
                "cameras": self.cameras,
                "balance": balance_data,
                "last_update": time.time(),
            }

        except Exception as err:
            _LOGGER.error("Error updating data: %s", err)
            raise
