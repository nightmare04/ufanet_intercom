"""Camera for ufanet intercom."""

from datetime import timedelta
import logging

from homeassistant.components.camera import (
    Camera,
    CameraEntityDescription,
    CameraEntityFeature,
    StreamType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import UfanetAPI
from .const import DOMAIN
from .models import UCamera

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=15)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up camera from a config entry."""
    api = hass.data[DOMAIN][entry.entry_id]
    session = async_get_clientsession(hass)
    cameras = await api.get_cameras()

    for camera in cameras:
        async_add_entities([UfanetCamera(session, api, camera)], update_before_add=True)
    return True


class UfanetCamera(Camera):
    """Representation of Ufanet Camera."""

    _attr_supported_features = CameraEntityFeature.STREAM
    _attr_frontend_stream_type = StreamType.HLS
    _attr_motion_detection_enabled = False

    entity_description = CameraEntityDescription(
        key="camera",
        icon="mdi:doorbell-video",
    )

    def __init__(self, session, api: UfanetAPI, camera: UCamera) -> None:
        """Initialize the camera."""
        super().__init__()
        self._api = api
        self._camera = camera
        self.session = session

    async def stream_source(self) -> str | None:
        """Get stream link for Ufanet camera."""
        return self._camera.rtsp_url

    async def async_update(self):
        """Update intercom camera."""
        await self.stream_source()

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return f"{self._camera.number}"

    @property
    def use_stream_for_stills(self) -> bool:
        """Use stream to generate stills."""
        return True

    @property
    def suggested_object_id(self) -> str:
        """Return the suggested object ID."""
        # Ensure this returns a string
        return f"{self._camera.title}"

    @property
    def name(self) -> str:
        """Return the suggested object ID."""
        # Ensure this returns a string
        return f"{self._camera.title}"
