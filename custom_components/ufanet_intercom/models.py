"""Models for Ufanet api."""

from pydantic import BaseModel, computed_field


class Token(BaseModel):
    """Token model."""

    access: str
    refresh: str
    exp: int


class Role(BaseModel):
    """Role model."""

    id: int
    name: str


class Contract(BaseModel):
    """Contract model."""

    id: int
    title: str
    balance: int


class Intercom(BaseModel):
    """Intercom model."""

    id: int
    contract: str | None
    role: Role
    camera: str | None
    cctv_number: str
    string_view: str
    timeout: int
    disable_button: bool
    no_sound: bool
    open_in_talk: str
    open_type: str
    dtmf_code: str
    inactivity_reason: str | None
    house: int
    frsi: bool
    is_fav: bool
    model: int
    custom_name: str | None
    is_blocked: bool
    supports_key_recording: bool
    ble_support: bool
    scope: str


class Servers(BaseModel):
    """Server model."""

    server: bool
    domain: str
    screenshot_domain: str
    vendor_name: str


class UCamera(BaseModel):
    """Camera model."""

    number: str
    latitude: float
    longitude: float
    title: str
    address: str
    token_l: str
    token_r: str
    servers: Servers
    type: str

    @computed_field
    @property
    def rtsp_url(self) -> str:
        """Get rtsp url from model."""
        return f"rtsp://{self.servers.domain}/{self.number}?token={self.token_l}"
