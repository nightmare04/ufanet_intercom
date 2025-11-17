"""Constants for My Intercom integration."""

DOMAIN = "ufanet_intercom"
PLATFORMS = ["camera"]

# Configuration
CONF_HOST = "host"
CONF_CONTRACT = "contract"
CONF_PASSWORD = "password"

# Defaults
UPDATE_INTERVAL = 60

# API endpoints
API_BASE_URL = "https://dom.ufanet.ru/"
API_AUTH = "api/v1/auth/auth_by_contract/"
API_INTERCOMS = "api/v0/skud/shared/"
API_CAMERAS = "api/v1/cctv"
API_CONTRACT = "/api/v0/contract"
API_OPEN_DOOR = "api/v0/skud/shared/{intercom_id}/open/"

# Attributes
ATTR_CAMERA_NUMBER = "intercom_id"
ATTR_RTSP_URL = "rtsp_url"
ATTR_LAST_UPDATE = "last_update"
