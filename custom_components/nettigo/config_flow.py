"""Adds config flow for Nettigo."""
from typing import Optional

from aiohttp.client_exceptions import ClientConnectorError
import async_timeout
from nettigo import ApiError, CannotGetMac, Nettigo
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN  # pylint:disable=unused-import


class NettigoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Nettigo."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input: Optional[dict] = None) -> dict:
        """Handle a flow initialized by the user."""
        errors = {}

        websession = async_get_clientsession(self.hass)

        if user_input is not None:
            device = Nettigo(websession, user_input[CONF_HOST])
            try:
                with async_timeout.timeout(5):
                    mac = await device.async_get_mac()
            except (ApiError, ClientConnectorError):
                errors["base"] = "cannot_connect"
            except CannotGetMac:
                errors["base"] = "device_unsupported"
            else:

                await self.async_set_unique_id(mac)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_HOST],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=""): str,
                }
            ),
            errors=errors,
        )
