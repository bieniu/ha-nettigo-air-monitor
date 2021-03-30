"""Adds config flow for Nettigo."""
import ipaddress
import re
from typing import Optional

from aiohttp.client_exceptions import ClientConnectorError
import async_timeout
from nettigo import ApiError, CannotGetMac, Nettigo
import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac

from .const import DOMAIN  # pylint:disable=unused-import


def host_valid(host):
    """Return True if hostname or IP address is valid."""
    try:
        if ipaddress.ip_address(host).version == (4 or 6):
            return True
    except ValueError:
        disallowed = re.compile(r"[^a-zA-Z\d\-]")
        return all(x and not disallowed.search(x) for x in host.split("."))


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
            try:
                if not host_valid(user_input[CONF_HOST]):
                    raise InvalidHost()

                nettigo = Nettigo(websession, user_input[CONF_HOST])

                with async_timeout.timeout(10):
                    mac = await nettigo.async_get_mac_address()
            except InvalidHost:
                errors["base"] = "invalid_host"
            except (ApiError, ClientConnectorError):
                errors["base"] = "cannot_connect"
            except CannotGetMac:
                return self.async_abort(reason="device_unsupported")
            else:

                await self.async_set_unique_id(format_mac(mac))
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


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate that hostname/IP address is invalid."""