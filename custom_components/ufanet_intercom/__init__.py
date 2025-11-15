"""Init for therion intercom."""

import logging

from homeassistant import config_entries, core

from .api import UfanetAPI as API
from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    api = API(
        hass=hass,
        contract=config_entry.data["contract"],
        password=config_entry.data["password"],
    )
    try:
        # Test connection during setup
        if not await api.async_authenticate():
            _LOGGER.error("Failed to authenticate with Ufanet API")
            return False

        hass.data[DOMAIN][config_entry.entry_id] = api
        # Forward the setup to the camera, button, sensor platform.
        await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
        return True

    except Exception as ex:
        _LOGGER.error("Error setting up Ufanet integration: %s", ex)
        return False


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return unload_ok
    return False
