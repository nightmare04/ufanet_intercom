"""Camera platform for My Intercom integration."""

import logging
from typing import Optional

from homeassistant.components.camera import (
    Camera,
    CameraEntityFeature,
    CameraEntityDescription,
    StreamType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_CAMERA_NUMBER, ATTR_RTSP_URL, DOMAIN
from .coordinator import UfanetDataCoordinator
from .models import UCamera

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
    entities = []
    for camera in coordinator.data.get("cameras"):
        entities.append(UfanetCamera(coordinator, camera))
        _LOGGER.debug(
            "Created camera %s with RTSP: %s",
            camera.number,
            camera.rtsp_url,
        )

    _LOGGER.info("Setting up %d cameras", len(entities))
    async_add_entities(entities)


class UfanetCamera(CoordinatorEntity, Camera):
    """Representation of an Intercom Camera using RTSP stream."""

    _attr_supported_features = CameraEntityFeature.STREAM
    _attr_frontend_stream_type = StreamType.HLS
    _attr_motion_detection_enabled = False

    entity_description = CameraEntityDescription(
        key="camera",
        icon="mdi:doorbell-video",
    )

    def __init__(self, coordinator: UfanetDataCoordinator, camera: UCamera) -> None:
        """Initialize the camera."""
        super().__init__(coordinator)
        Camera.__init__(self)

        self._id = camera.number
        self._camera_name = f"{camera.address} {camera.title}"
        self._rtsp_url = camera.rtsp_url

        self._attr_name = f"Ufanet {self._camera_name}"
        self._attr_unique_id = self._id

        # Camera attributes for better UI integration
        self._attr_brand = "Ufanet"
        self._attr_model = "RTSP Camera"

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        _LOGGER.debug(
            "Camera %s added to hass with RTSP URL: %s",
            self._id,
            self._rtsp_url,
        )
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def stream_source(self) -> Optional[str]:
        """Return the RTSP stream source."""
        return self._rtsp_url

    @property
    def extra_state_attributes(self):
        """Return additional camera attributes."""
        return {
            ATTR_CAMERA_NUMBER: self._id,
            ATTR_RTSP_URL: self._rtsp_url,
        }

    @property
    def use_stream_for_stills(self) -> bool:
        """Use stream to generate stills."""
        return True
