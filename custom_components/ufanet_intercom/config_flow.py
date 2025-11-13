"""Config flow for Ufanet intercom."""

import logging

import voluptuous as vol

from homeassistant import config_entries

from .api import UfanetAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class UfanetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # noqa: D101
    VERSION = 1

    async def async_step_user(self, user_input=None):  # noqa: D102
        errors = {}
        if user_input is not None:
            api = UfanetAPI(user_input["contract"], user_input["password"])
            await api.set_token()
            if api.auth:
                return self.async_create_entry(
                    title=f"Домофон {user_input['contract']}", data=user_input
                )
            errors["base"] = "auth_error"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("contract"): str, vol.Required("password"): str}
            ),
            errors=errors,
        )
