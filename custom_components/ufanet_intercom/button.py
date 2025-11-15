"""Ufanet door button."""

import asyncio
import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import UfanetDataCoordinator
from .models import Intercom

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up camera platform."""
    coordinator: UfanetDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Wait for initial data to be available
    if not coordinator.data:
        await coordinator.async_request_refresh()

    intercoms = coordinator.data.get("intercoms", [])
    entities = []

    for intercom in intercoms:
        if intercom.is_fav:
            entities.append(UfanetButton(coordinator, intercom))
            _LOGGER.debug(
                "Created button for intercom %s ",
                intercom.id,
            )

    _LOGGER.info("Setting up %d buttons", len(entities))
    async_add_entities(entities)


class UfanetButton(CoordinatorEntity, ButtonEntity):
    """Ufanet open_button."""

    entity_description = ButtonEntityDescription(
        key="button",
        icon="mdi:lock-open",
        name="Open",
    )

    _attr_should_poll = False

    def __init__(self, coordinator: UfanetDataCoordinator, intercom: Intercom) -> None:
        """Init intercom button."""
        super().__init__(coordinator)
        ButtonEntity.__init__(self)
        self._coordinator = coordinator
        self._intercom = intercom
        self._attr_unique_id = f"{intercom.id}_button"
        self._attr_name = f"{intercom.custom_name} door button"
        self._attr_available = True

    async def async_press(self) -> None:
        """Press button."""
        try:
            await self._coordinator.api.async_open_door(self._intercom.id)
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
