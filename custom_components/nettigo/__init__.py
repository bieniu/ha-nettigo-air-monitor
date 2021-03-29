"""The Nettigo component."""
import asyncio
import logging
from typing import Any, Optional

from aiohttp.client_exceptions import ClientConnectorError
from async_timeout import timeout
from nettigo import ApiError, Nettigo

from homeassistant.const import CONF_HOST
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_NAME, DEFAULT_UPDATE_INTERVAL, DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["air_quality", "sensor"]


async def async_setup(  # pylint:disable=unused-argument
    hass: HomeAssistant, config: Config
) -> bool:
    """"Old way of setting up Nettigo integrations."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: Config) -> bool:
    """Set up Nettigo as config entry."""
    host = entry.data[CONF_HOST]

    websession = async_get_clientsession(hass)

    coordinator = NettigoUpdateCoordinator(hass, websession, host, entry.unique_id)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: Config) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class NettigoUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Nettigo data."""

    def __init__(self, hass, session, host, unique_id):
        """Initialize."""
        self.host = host
        self.nettigo = Nettigo(session, host)
        self._unique_id = unique_id

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=DEFAULT_UPDATE_INTERVAL
        )

    async def _async_update_data(self) -> Optional[Any]:
        """Update data via library."""
        try:
            with timeout(10):
                data = await self.nettigo.async_update()
        except (ApiError, ClientConnectorError) as error:
            raise UpdateFailed(error) from error

        return data

    @property
    def unique_id(self):
        """Return a unique_id."""
        return self._unique_id

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "connections": {(CONNECTION_NETWORK_MAC, self._unique_id)},
            "name": DEFAULT_NAME,
            "sw_version": self.data["software_version"],
            "manufacturer": MANUFACTURER,
        }
