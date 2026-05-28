import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_HOST

CONF_PORT = "port"
CONF_TIMEOUT = "timeout"
DEFAULT_HOST = "homeassistant.local"
DEFAULT_TIMEOUT = 120

DOMAIN = "orefree"

class OreFreeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OreFree."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Default host if empty
            if not user_input.get(CONF_HOST):
                user_input[CONF_HOST] = DEFAULT_HOST
            return self.async_create_entry(title="OreFree", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_PORT, default=8000): int,
            vol.Optional(CONF_HOST, default=DEFAULT_HOST): str,
            vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
        })
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
