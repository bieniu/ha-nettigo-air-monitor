"""Support for the Nettigo service."""
from typing import Callable, Optional
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

from .const import DEFAULT_NAME, DOMAIN, SENSORS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable
) -> None:
    """Add a Nettigo entities from a config_entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    for sensor in SENSORS:
        if sensor in coordinator.data["sensordatavalues"]:
            sensors.append(NettigoSensor(coordinator, sensor, entry.unique_id))

    async_add_entities(sensors, False)


class NettigoSensor(CoordinatorEntity):
    """Define an Nettigo sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, sensor_type: str, unique_id: str):
        """Initialize."""
        super().__init__(coordinator)
        self.sensor_type = sensor_type
        self._unique_id = unique_id

    @property
    def name(self) -> str:
        """Return the name."""
        return SENSORS[self.sensor_type][2]

    @property
    def state(self) -> Optional[str]:
        """Return the state."""
        if self.sensor_type == "BME280_pressure":
            _LOGGER.debug
            return round(self.coordinator.data["sensordatavalues"][self.sensor_type] / 100)
        return round(self.coordinator.data["sensordatavalues"][self.sensor_type], 1)

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit the value is expressed in."""
        return SENSORS[self.sensor_type][0]

    @property
    def icon(self) -> str:
        """Return the icon."""
        return None

    @property
    def device_class(self) -> str:
        """Return the class of this sensor."""
        return SENSORS[self.sensor_type][1]

    @property
    def unique_id(self) -> str:
        """Return a unique_id for this entity."""
        return f"{self._unique_id}-{self.sensor_type}"

    @property
    def device_info(self) -> dict:
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "connections": {(CONNECTION_NETWORK_MAC, self._unique_id)},
            "name": DEFAULT_NAME,
        }
