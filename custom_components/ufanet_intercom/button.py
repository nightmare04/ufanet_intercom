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

    def __init__(self, session, api: UfanetAPI, intercom: Intercom) -> None:
        """Init intercom button."""
        super().__init__()
        self._api = api
        self._intercom = intercom
        self.session = session

    @property
    def name(self) -> str:
        """Return name of Therion open door button."""
        return f"{self._intercom.custom_name} door button"

    async def async_update(self):
        """Update."""

    async def async_press(self):
        """Press button."""
        await self._api.open_intercom(self._intercom.id)

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return f"{self._intercom.id}button"
