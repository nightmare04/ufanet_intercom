"""Config flow for My Intercom integration."""

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .api import UfanetAPI
from .const import DOMAIN, CONF_HOST, CONF_CONTRACT, CONF_PASSWORD


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for My Intercom."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                api = UfanetAPI(
                    hass=self.hass,
                    contract=user_input[CONF_CONTRACT],
                    password=user_input[CONF_PASSWORD],
                )

                await api.async_authenticate()

                await self.async_set_unique_id(user_input[CONF_CONTRACT])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Ufanet {user_input[CONF_CONTRACT]}", data=user_input
                )

            except Exception as err:
                errors["base"] = "invalid_auth"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_CONTRACT): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
