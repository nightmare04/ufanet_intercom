"""Sensors for Ufanet intercom."""

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .models import Contract
from .coordinator import UfanetDataCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator: UfanetDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    contracts = await coordinator.api.get_contract()

    sensors = []

    for contract in contracts:
        sensors.append
    async_add_entities(sensors)


class SensorBalance(SensorEntity):
    """Ufanet intercom balance sensor."""

    def __init__(self, api, contract: Contract) -> None:
        """Init intercom balance."""
        super().__init__()
        self._api = api
        self._contract = contract
        self._attr_unique_id = contract.id
        self._attr_name = "Balance"
        self._attr_native_unit_of_measurement = "RUB"
        self._attr_icon = "mdi:currency-rub"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.TOTAL

    async def async_update(self):
        """Update balance."""
        contract = await self._api.get_contract()
        self._attr_native_value = contract[0].balance
