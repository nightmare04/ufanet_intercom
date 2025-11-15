"""Camera platform for My Intercom integration."""

import asyncio
import logging
from typing import Any, Optional

from homeassistant.components.camera import Camera
from homeassistant.components.ffmpeg import get_ffmpeg_manager
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_INTERCOM_ID, ATTR_RTSP_URL, DOMAIN, SNAPSHOT_TIMEOUT
from .coordinator import UfanetDataCoordinator

_LOGGER = logging.getLogger(__name__)


class IntercomCamera(CoordinatorEntity, Camera):
    """Representation of an Intercom Camera using RTSP stream."""

    def __init__(
        self, coordinator: UfanetDataCoordinator, intercom_info: dict[str, Any]
    ) -> None:
        """Initialize the camera."""
        super().__init__(coordinator)
        Camera.__init__(self)

        self._intercom_id = intercom_info["id"]
        self._intercom_name = intercom_info.get("name", f"Intercom {self._intercom_id}")
        self._rtsp_url = intercom_info.get("rtsp_url")
        self._ffmpeg = get_ffmpeg_manager(self.hass)

        self._attr_name = f"{self._intercom_name} Camera"
        self._attr_unique_id = f"{self._intercom_id}_camera"

        # Camera attributes for better UI integration
        self._attr_brand = "My Intercom"
        self._attr_model = "RTSP Camera"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._intercom_id)},
            "name": self._intercom_name,
            "manufacturer": "My Intercom",
            "model": "Smart Intercom",
        }

    @property
    def extra_state_attributes(self):
        """Return additional camera attributes."""
        return {
            ATTR_INTERCOM_ID: self._intercom_id,
            ATTR_RTSP_URL: self._rtsp_url,
        }

    @property
    def rtsp_url(self) -> Optional[str]:
        """Return RTSP URL for this camera."""
        return self._rtsp_url

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        _LOGGER.debug(
            "Camera %s added to hass with RTSP URL: %s",
            self._intercom_id,
            self._rtsp_url,
        )

    async def async_camera_image(
        self, width: Optional[int] = None, height: Optional[int] = None
    ) -> Optional[bytes]:
        """Return a still image response from the camera."""
        if not self._rtsp_url:
            _LOGGER.error("No RTSP URL for camera %s", self._intercom_id)
            return None

        _LOGGER.debug("Generating snapshot for camera %s from RTSP", self._intercom_id)

        try:
            # Generate snapshot from RTSP stream using ffmpeg
            image = await asyncio.wait_for(
                self._ffmpeg.async_get_image(
                    self._rtsp_url,
                    output_format="mjpeg",
                    extra_cmd="-frames:v 1",  # Capture single frame
                ),
                timeout=SNAPSHOT_TIMEOUT,
            )
            return image

        except asyncio.TimeoutError:
            _LOGGER.error(
                "Timeout generating snapshot for camera %s", self._intercom_id
            )
            return None
        except Exception as err:
            _LOGGER.error(
                "Error generating snapshot for camera %s: %s", self._intercom_id, err
            )
            return None

    async def async_stream_source(self) -> Optional[str]:
        """Return the RTSP stream source."""
        return self._rtsp_url

    async def async_handle_web_rtsp_stream(self) -> bool:
        """Handle RTSP stream for WebRTC."""
        return True

    async def async_update(self) -> None:
        """Update camera entity - noop, updates handled by coordinator."""
        pass


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up camera platform."""
    coordinator: MyIntercomDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Wait for initial data to be available
    if not coordinator.data:
        await coordinator.async_request_refresh()

    intercoms = coordinator.data.get("intercoms", [])
    entities = []

    for intercom in intercoms:
        # Only create camera if intercom has RTSP URL
        if intercom.get("rtsp_url"):
            entities.append(IntercomCamera(coordinator, intercom))
            _LOGGER.debug(
                "Created camera for intercom %s with RTSP: %s",
                intercom["id"],
                intercom["rtsp_url"],
            )
        else:
            _LOGGER.warning(
                "Intercom %s has no RTSP URL, skipping camera", intercom["id"]
            )

    _LOGGER.info("Setting up %d intercom cameras", len(entities))
    async_add_entities(entities)
