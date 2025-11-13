"""Config flow for Ufanet intercom."""

import voluptuous as vol

from homeassistant import config_entries

from .api import UfanetIntercomAPI
from .const import DOMAIN


class UfanetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            api = UfanetIntercomAPI(user_input["contract"], user_input["password"])
            if await api.set_token():
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
