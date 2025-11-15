"""Camera platform for My Intercom integration."""

import asyncio
import logging
from typing import Optional

from homeassistant.components.camera import (
    Camera,
    CameraEntityFeature,
    CameraEntityDescription,
    StreamType,
)
from homeassistant.components.ffmpeg import get_ffmpeg_manager
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_INTERCOM_ID, ATTR_RTSP_URL, DOMAIN, SNAPSHOT_TIMEOUT
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

    cameras = coordinator.data.get("cameras", [])
    entities = []

    for camera in cameras:
        # Only create camera if intercom has RTSP URL
        if camera.rtsp_url:
            entities.append(UfanetCamera(coordinator, camera))
            _LOGGER.debug(
                "Created camera %s with RTSP: %s",
                camera.number,
                camera.rtsp_url,
            )
        else:
            _LOGGER.warning("Camera %s has no RTSP URL, skipping camera", camera.number)

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

    async def async_camera_image(
        self, width: Optional[int] = None, height: Optional[int] = None
    ) -> Optional[bytes]:
        """Return a still image response from the camera."""
        if not self._rtsp_url:
            _LOGGER.error("No RTSP URL for camera %s", self._id)
            return None

        _LOGGER.debug("Generating snapshot for camera %s from RTSP", self._id)

        try:
            image = await asyncio.wait_for(
                self._ffmpeg.async_get_image(
                    self._rtsp_url, output_format="mjpeg", extra_cmd="-frames:v 1"
                ),
                timeout=SNAPSHOT_TIMEOUT,
            )
            return image

        except asyncio.TimeoutError:
            _LOGGER.error("Timeout generating snapshot for camera %s", self._id)
            return None
        except Exception as err:
            _LOGGER.error("Error generating snapshot for camera %s: %s", self._id, err)
            return None

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        _LOGGER.debug(
            "Camera %s added to hass with RTSP URL: %s",
            self._id,
            self._rtsp_url,
        )

    async def stream_source(self) -> Optional[str]:
        """Return the RTSP stream source."""
        return self._rtsp_url

    async def async_update(self) -> None:
        """Update camera entity - noop, updates handled by coordinator."""
        pass

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._camera_name,
        }

    @property
    def extra_state_attributes(self):
        """Return additional camera attributes."""
        return {
            ATTR_INTERCOM_ID: self._id,
            ATTR_RTSP_URL: self._rtsp_url,
        }

    @property
    def rtsp_url(self) -> Optional[str]:
        """Return RTSP URL for this camera."""
        return self._rtsp_url

    @property
    def use_stream_for_stills(self) -> bool:
        """Use stream to generate stills."""
        return True
