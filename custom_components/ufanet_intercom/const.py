"""Constants for My Intercom integration."""

from homeassistant.const import Platform
from datetime import timedelta

DOMAIN = "ufanet_intercom"
PLATFORMS = [Platform.CAMERA]

# Configuration
CONF_HOST = "https://dom.ufanet.ru/"

# Defaults
DEFAULT_SCAN_INTERVAL = 30
UPDATE_INTERVAL = 30
TOKEN_REFRESH_BEFORE_EXPIRY = timedelta(hours=24)
SNAPSHOT_TIMEOUT = 10  # Timeout for RTSP snapshot

# API endpoints
API_AUTH = "api/v1/auth/auth_by_contract/"
API_INTERCOMS = "api/v0/skud/shared/"
API_CAMERAS = "api/v1/cctv"
API_CONTRACT = "/api/v0/contract"
API_OPEN_DOOR = "api/v0/skud/shared/{intercom_id}/open/"

# Attributes
ATTR_INTERCOM_ID = "intercom_id"
ATTR_RTSP_URL = "rtsp_url"
ATTR_LAST_UPDATE = "last_update"
