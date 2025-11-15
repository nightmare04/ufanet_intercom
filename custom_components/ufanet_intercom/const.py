"""Constants for My Intercom integration."""

from homeassistant.const import Platform
from datetime import timedelta

DOMAIN = "ufanet_intercom"
PLATFORMS = [Platform.CAMERA, Platform.BUTTON]

# Configuration
CONF_HOST = "host"
CONF_CONTRACT = "contract"
CONF_PASSWORD = "password"

# Defaults
DEFAULT_SCAN_INTERVAL = 30
UPDATE_INTERVAL = 30

# API endpoints
API_AUTH = "api/v1/auth/auth_by_contract/"
API_INTERCOMS = "api/v0/skud/shared/"
API_CAMERAS = "api/v1/cctv"
API_CONTRACT = "/api/v0/contract"
API_OPEN_DOOR = "api/v0/skud/shared/{intercom_id}/open/"

# Attributes
ATTR_CAMERA_NUMBER = "intercom_id"
ATTR_RTSP_URL = "rtsp_url"
ATTR_LAST_UPDATE = "last_update"
