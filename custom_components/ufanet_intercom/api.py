"""API for Ufanet intercoms and video."""

import asyncio
from json import JSONDecodeError
from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientConnectorError, ClientSession, ClientTimeout, ContentTypeError

from .exceptions import (
    ClientConnectorUfanetIntercomAPIError,
    TimeoutUfanetIntercomAPIError,
    UnauthorizedUfanetIntercomAPIError,
    UnknownUfanetIntercomAPIError,
)
from .models import Intercom, Token, UCamera


class UfanetAPI:
    """API for Ufanet."""

    def __init__(
        self, contract: str | Any, password: str | Any, timeout: int = 30
    ) -> None:
        """Init Ufanet API."""
        self._contract = contract
        self._password = password
        self.auth: bool = False
        self._token: str | None = None
        self._base_url: str = "https://dom.ufanet.ru/"
        self.session: ClientSession = ClientSession(
            timeout=ClientTimeout(total=timeout)
        )
        self.auth: bool = False

    async def _send_request(
        self,
        url: str,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        while True:
            headers = {"Authorization": f"JWT {self._token}"} if self._token else {}
            try:
                async with self.session.request(
                    method, url, params=params, json=json, headers=headers
                ) as response:
                    try:
                        json_response = (
                            await response.json()
                            if 199 < response.status < 500
                            else None
                        )
                    except (JSONDecodeError, ContentTypeError):
                        raise UnknownUfanetIntercomAPIError(
                            f"Unknown error: {response.status} {response.reason}"
                        ) from None

                    if response.status == 401:
                        raise UnauthorizedUfanetIntercomAPIError(json_response)  # noqa: TRY301

                    if response.status in (200,):
                        return json_response

                    raise UnknownUfanetIntercomAPIError(json_response)

            except asyncio.exceptions.TimeoutError:
                raise TimeoutUfanetIntercomAPIError("Timeout error") from None

            except ClientConnectorError:
                raise ClientConnectorUfanetIntercomAPIError(
                    "Client connector error"
                ) from None

            except UnauthorizedUfanetIntercomAPIError:
                await self._prepare_token()

    async def _prepare_token(self):
        if self._token is None:
            await self.set_token()
        else:
            try:
                await self.token_verify()
            except UnauthorizedUfanetIntercomAPIError:
                await self.set_token()

    async def set_token(self):
        """Set token."""
        url = urljoin(self._base_url, "api/v1/auth/auth_by_contract/")
        json = {"contract": self._contract, "password": self._password}
        response = await self._send_request(url=url, method="POST", json=json)
        self._token = Token(**response["token"]).refresh  # type: ignore  # noqa: PGH003
        self.auth = True

    async def token_verify(self):
        """Verify token."""
        url = urljoin(self._base_url, "api-token-verify/")
        json = {"token": self._token}
        await self._send_request(url=url, method="POST", json=json)

    async def get_intercoms(self) -> list[Intercom]:
        """Get intercoms."""
        url = urljoin(self._base_url, "api/v0/skud/shared/")
        response = await self._send_request(url=url)
        return [Intercom(**i) for i in response]  # type: ignore  # noqa: PGH003

    async def get_fav_intercom(self):
        """Get favorites intercoms."""
        fav_intercoms: list[Intercom]
        fav_intercoms = []
        intercoms = await self.get_intercoms()
        for intercom in intercoms:
            if intercom.is_fav:
                fav_intercoms.append(intercom)
        return fav_intercoms

    async def get_cameras(self) -> list[UCamera]:
        """Get camera list from API."""
        url = urljoin(self._base_url, "api/v1/cctv")
        response = await self._send_request(url=url)
        return [UCamera(**i) for i in response]  # type: ignore  # noqa: PGH003

    async def open_intercom(self, intercom_id: int) -> bool:
        """Open intercom door."""
        url = urljoin(self._base_url, f"api/v0/skud/shared/{intercom_id}/open/")
        response = await self._send_request(url=url)
        return response["result"]  # type: ignore  # noqa: PGH003

    async def close(self):
        """Close session."""
        await self.session.close()
