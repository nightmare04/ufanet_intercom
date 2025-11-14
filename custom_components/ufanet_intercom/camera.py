"""Camera platform for My Integration."""

import logging
from typing import Optional

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import UfanetDataCoordinator

_LOGGER = logging.getLogger(__name__)

class MyIntegrationCamera(CoordinatorEntity, Camera):
    """Representation of My Integration Camera."""
    
    def __init__(self, coordinator: UfanetDataCoordinator, device_id: str):
        """Initialize the camera."""
        super().__init__(coordinator)
        Camera.__init__(self)
        
        self._device_id = device_id
        self._attr_name = "My Integration Camera"
        self._attr_unique_id = f"{device_id}_camera"
        
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
        }
        
    async def async_camera_image(
        self, width: Optional[int] = None, height: Optional[int] = None
    ) -> Optional[bytes]:
        """Return camera image."""
        return self.coordinator.data.get("camera")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up camera platform."""
    coordinator: UfanetDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        MyIntegrationCamera(coordinator, entry.data["device_id"])
    ])



# """Camera for ufanet intercom."""

# from datetime import timedelta
# import logging

# from homeassistant.components.camera import Camera
# from homeassistant.config_entries import ConfigEntry
# from homeassistant.core import HomeAssistant
# from homeassistant.helpers.aiohttp_client import async_get_clientsession
# from homeassistant.helpers.entity_platform import AddEntitiesCallback

# from .api import UfanetIntercomAPI
# from .const import DOMAIN
# from .models import UCamera

# _LOGGER = logging.getLogger(__name__)
# SCAN_INTERVAL = timedelta(seconds=15)


# async def async_setup_entry(
#     hass: HomeAssistant,
#     entry: ConfigEntry,
#     async_add_entities: AddEntitiesCallback,
# ) -> bool:
#     """Set up camera from a config entry."""
#     api = hass.data[DOMAIN][entry.entry_id]
#     session = async_get_clientsession(hass)
#     cameras = await api.get_cameras()

#     for camera in cameras:
#         async_add_entities([UfanetCamera(session, api, camera)], update_before_add=True)
#     return True


# class UfanetCamera(Camera):
#     """Representation of Ufanet Camera."""

#     def __init__(self, session, api: UfanetIntercomAPI, camera: UCamera) -> None:
#         """Initialize the camera."""
#         super().__init__()
#         self._api = api
#         self.camera = camera
#         self.session = session

#     async def async_camera_image(
#         self, width: int | None = None, height: int | None = None
#     ) -> bytes | None:
#         """Return a still image from the camera."""
#         try:
#             # Implement image capture logic if API provides snapshots
#             # Or use stream to generate still
#             return await super().async_camera_image(width, height)
#         except Exception as ex:
#             _LOGGER.error("Failed to get camera image: %s", ex)
#             return None

#     async def stream_source(self) -> str | None:
#         """Get stream link for Ufanet camera."""
#         return self.camera.rtsp_url

#     async def async_update(self) -> None:
#         """Update camera state."""
#         try:
#             cameras = await self._api.get_cameras()
#             for camera in cameras:
#                 if camera.number == self.camera.number:
#                     self.camera = camera
#                     self._stream_source = camera.rtsp_url
#                     self._attr_available = True
#                     break
#         except Exception as ex:
#             _LOGGER.error("Failed to update camera %s: %s", self.camera.number, ex)
#             self._attr_available = False

#     @property
#     def unique_id(self) -> str:
#         """Return the unique ID of the sensor."""
#         return f"{self.camera.number}"

#     # @property
#     # def suggested_object_id(self) -> str:
#     #     """Return the suggested object ID."""
#     #     # Ensure this returns a string
#     #     return f"{self.camera.title}"
