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

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API - только баланс, камеры обновляются отдельно."""
        try:
            intercoms_data = await self.api.get_intercoms()
            cameras_data = await self.api.get_cameras()
            contract_data = await self.api.get_contract()

            return {
                "intercoms": intercoms_data,
                "cameras": cameras_data,
                "contract": contract_data,
                "last_update": time.time(),
            }

        except Exception as err:
            _LOGGER.error("Error updating data: %s", err)
            raise
