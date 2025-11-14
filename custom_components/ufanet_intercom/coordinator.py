"""Data coordinator for My Integration."""

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import UfanetIntercomAPI
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class UfanetDataCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data updates."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize coordinator."""
        self.entry = entry
        self.api = UfanetIntercomAPI(
            hass=hass,
            contract=entry.data["contract"],
            password=entry.data["password"]
        )
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL),
        )
        
    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            # Fetch all data in parallel
            camera_task = self.api.get_cameras()
            intercom_task = self.api.get_intercoms()
            contract_task = self.api.get_contract()
            
            camera_data, intercom_data, contract_data = await asyncio.gather(
                camera_task, intercom_task, contract_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(camera_data, Exception):
                _LOGGER.error("Camera data error: %s", camera_data)
                camera_data = None
            if isinstance(intercom_data, Exception):
                _LOGGER.error("Intercom data error: %s", intercom_data)
                intercom_data = 0
            if isinstance(contract_data, Exception):
                _LOGGER.error("Contract data error: %s", contract_data)
                contract_data = {}
                
            return {
                "camera": camera_data,
                "intercom": intercom_data,
                "contract": contract_data,
                "last_update": asyncio.get_event_loop().time()
            }
            
        except Exception as err:
            _LOGGER.error("Error updating data: %s", err)
            raise