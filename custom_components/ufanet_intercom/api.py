import asyncio
import logging
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Union
from urllib.parse import urljoin
from uuid import UUID, uuid4
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from aiohttp.client_exceptions import ClientConnectorError, ContentTypeError

from .exceptions import (
    ClientConnectorUfanetIntercomAPIError,
    TimeoutUfanetIntercomAPIError,
    UnauthorizedUfanetIntercomAPIError,
    UnknownUfanetIntercomAPIError,
)
from .safe_logger import SafeLogger
from .models import Intercom, Token, UCamera, Contract


class UfanetIntercomAPI:
    def __init__(
        self,
        contract: str,
        password: str,
        hass: HomeAssistant,
        timeout: int = 30,
        level: logging = logging.INFO,
    ):
        self._timeout = timeout
        self._contract = contract
        self._password = password
        self._session = None
        self._token: Union[str, None] = None
        self._base_url: str = "https://dom.ufanet.ru/"
        self._logger = SafeLogger("UfanetIntercomAPI")
        self._logger.setLevel(level)
        self._session = async_get_clientsession(hass)


    async def _send_request(
        self,
        url: str,
        method: str = "GET",
        params: Dict[str, Any] = None,
        json: Dict[str, Any] = None,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        while True:
            headers = {"Authorization": f"JWT {self._token}"}
            request_id = uuid4().hex
            self._logger.info(
                "Request=%s method=%s url=%s params=%s json=%s",
                request_id,
                method,
                url,
                params,
                json,
            )
            try:
                async with self._session.request(
                    method, url, params=params, json=json, headers=headers
                ) as response:
                    try:
                        json_response = (
                            await response.json()
                            if 199 < response.status < 500
                            else None
                        )
                    except (JSONDecodeError, ContentTypeError) as e:
                        raw_response = await response.text()
                        self._logger.error(
                            "Response=%s unsuccessful request status=%s reason=%s raw=%s error=%s",
                            request_id,
                            response.status,
                            response.reason,
                            raw_response,
                            e,
                        )
                        raise UnknownUfanetIntercomAPIError(
                            f"Unknown error: {response.status} {response.reason}"
                        )
                    if response.status == 401:
                        raise UnauthorizedUfanetIntercomAPIError(json_response)

                    if response.status in (200,):
                        self._logger.info(
                            "Response=%s json_response=%s", request_id, json_response
                        )
                        return json_response

                    self._logger.error(
                        "Response=%s unsuccessful request json_response=%s status=%s reason=%s",
                        request_id,
                        json_response,
                        response.status,
                        response.reason,
                    )
                    raise UnknownUfanetIntercomAPIError(json_response)

            except asyncio.exceptions.TimeoutError:
                self._logger.error(
                    "Response=%s TimeoutUfanetIntercomAPIError", request_id
                )
                raise TimeoutUfanetIntercomAPIError("Timeout error")

            except ClientConnectorError:
                self._logger.error(
                    "Response=%s ClientConnectorUfanetIntercomAPIError", request_id
                )
                raise ClientConnectorUfanetIntercomAPIError("Client connector error")

            except UnauthorizedUfanetIntercomAPIError as e:
                self._logger.warning(
                    "Response=%s UnauthorizedUfanetIntercomAPIError=%s, trying get jwt",
                    request_id,
                    e,
                )
                await self._prepare_token()

    async def _prepare_token(self):
        if self._token is None:
            await self.set_token()
        else:
            try:
                await self.token_verify()
            except UnauthorizedUfanetIntercomAPIError:
                await self.set_token()

    async def token_verify(self):
        url = urljoin(self._base_url, "api-token-verify/")
        json = {"token": self._token}
        await self._send_request(url=url, method="POST", json=json)

    async def set_token(self) -> bool:
        url = urljoin(self._base_url, "api/v1/auth/auth_by_contract/")
        json = {"contract": self._contract, "password": self._password}
        response = await self._send_request(url=url, method="POST", json=json)
        self._token = Token(**response["token"]).refresh
        if self._token:
            return True

    async def get_intercoms(self) -> List[Intercom]:
        url = urljoin(self._base_url, "api/v0/skud/shared/")
        response = await self._send_request(url=url)
        return [Intercom(**i) for i in response]

    async def open_intercom(self, intercom_id: int) -> bool:
        url = urljoin(self._base_url, f"api/v0/skud/shared/{intercom_id}/open/")
        response = await self._send_request(url=url)
        return response["result"]

    async def get_cameras(self) -> List[UCamera]:
        url = urljoin(self._base_url, "api/v1/cctv")
        response = await self._send_request(url=url)
        return [UCamera(**i) for i in response]
    
    async def get_contract(self) -> Contract:
        url = urljoin(self._base_url, "api/v0/contract/")
        response = await self._send_request(url=url)
        return Contract(**response[0])