"""Therion intercom camera."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import UfanetAPI
from .const import DOMAIN
from .models import Intercom

_LOGGER = logging.getLogger(__name__)
UPDATE_INTERVAL = timedelta(seconds=15)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """Setup button from a config entry created in the integrations UI."""
    api = hass.data[DOMAIN][entry.entry_id]
    session = async_get_clientsession(hass)
    intercoms = await api.get_intercoms()
    for intercom in intercoms:
        if intercom.is_fav:
            async_add_entities(
                [UfanetButton(session, api, intercom)], update_before_add=True
            )
    return True


class UfanetButton(ButtonEntity):
    """Therion intercom open_button."""

    entity_description = ButtonEntityDescription(
        key="button",
        icon="mdi:lock-open",
        name="Open",
    )

    _attr_should_poll = False

    def __init__(self, session, api: UfanetAPI, intercom: Intercom) -> None:
        """Init intercom button."""
        super().__init__()
        self._api = api
        self._intercom = intercom
        self.session = session
        self._attr_unique_id = f"{intercom.id}_button"
        self._attr_name = f"{intercom.custom_name} door button"
        self._attr_available = True

    async def async_press(self) -> None:
        """Press button."""
        try:
            await self._api.open_intercom(self._intercom.id)
            # Optional: provide feedback in UI
            self._attr_icon = "mdi:lock-open-check"
            self.async_write_ha_state()
            # Reset icon after delay
            await asyncio.sleep(2)
            self._attr_icon = "mdi:lock-open"
            self.async_write_ha_state()
        except Exception as ex:
            _LOGGER.error("Failed to open intercom %s: %s", self._intercom.id, ex)
            self._attr_available = False
            self.async_write_ha_state()
