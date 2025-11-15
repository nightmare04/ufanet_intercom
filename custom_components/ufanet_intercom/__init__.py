"""Init for therion intercom."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .api import UfanetAPI as API
from .const import DOMAIN, PLATFORMS
from .coordinator import UfanetDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up My Intercom from a config entry."""

    coordinator = UfanetDataCoordinator(hass, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
        await coordinator.async_initialize_intercoms()
    except Exception as err:
        _LOGGER.error("Failed to setup integration: %s", err)
        return False

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return unload_ok
    return False
