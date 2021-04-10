"""Adds config flow for Nettigo."""
import ipaddress
import re
import logging
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


_LOGGER = logging.getLogger(__name__)

def host_valid(host: str) -> bool:
    """Return True if hostname or IP address is valid."""
    try:
        return ipaddress.ip_address(host).version == (4 or 6)
    except ValueError:
        disallowed = re.compile(r"[^a-zA-Z\d\-]")
        return all(x and not disallowed.search(x) for x in host.split("."))


class NettigoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Nettigo."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    host = None

    async def async_step_user(self, user_input: Optional[dict] = None) -> dict:
        """Handle a flow initialized by the user."""
        errors = {}

        websession = async_get_clientsession(self.hass)

        if user_input is not None:
            host = user_input[CONF_HOST]
            try:
                if not host_valid(host):
                    raise InvalidHost()

                nettigo = Nettigo(websession, host)

                with async_timeout.timeout(5):
                    mac = await nettigo.async_get_mac_address()
            except InvalidHost:
                errors["base"] = "invalid_host"
            except (ApiError, ClientConnectorError):
                errors["base"] = "cannot_connect"
            except CannotGetMac:
                return self.async_abort(reason="device_unsupported")
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:

                await self.async_set_unique_id(format_mac(mac))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=host,
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

    async def async_step_zeroconf(self, zeroconf_info: dict) -> dict:
        """Handle zeroconf discovery."""
        self.host = zeroconf_info[CONF_HOST]
        websession = async_get_clientsession(self.hass)

        try:
            nettigo = Nettigo(websession, self.host)
            with async_timeout.timeout(5):
                mac = await nettigo.async_get_mac_address()
        except (ApiError, ClientConnectorError):
            return self.async_abort(reason="cannot_connect")
        except CannotGetMac:
            return self.async_abort(reason="device_unsupported")

        await self.async_set_unique_id(format_mac(mac))
        self._abort_if_unique_id_configured({CONF_HOST: self.host})

        self.context["title_placeholders"] = {
            "name": zeroconf_info.get("name", "").split(".")[0]
        }

        return await self.async_step_confirm_discovery()

    async def async_step_confirm_discovery(
        self, user_input: Optional[dict] = None
    ) -> dict:
        """Handle discovery confirm."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=self.host,
                data={CONF_HOST: self.host},
            )

        self._set_confirm_only()

        return self.async_show_form(
            step_id="confirm_discovery",
            description_placeholders={CONF_HOST: self.host},
            errors=errors,
        )


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate that hostname/IP address is invalid."""
