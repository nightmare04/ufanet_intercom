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

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API - только баланс, камеры обновляются отдельно."""
        try:
            intercoms_data = await self.api.async_get_intercoms()
            cameras_data = await self.api.async_get_cameras()
            balance_data = await self.api.async_get_balance()

            return {
                "intercoms": intercoms_data,
                "cameras": cameras_data,
                "balance": balance_data,
                "last_update": time.time(),
            }

        except Exception as err:
            _LOGGER.error("Error updating data: %s", err)
            raise
