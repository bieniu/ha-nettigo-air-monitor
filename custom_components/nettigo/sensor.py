"""Support for the Nettigo service."""
from typing import Callable, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, SENSORS


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable
) -> None:
    """Add a Nettigo entities from a config_entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    for sensor in SENSORS:
        if sensor in coordinator.data["sensordatavalues"]:
            sensors.append(NettigoSensor(coordinator, sensor))

    async_add_entities(sensors, False)


class NettigoSensor(CoordinatorEntity):
    """Define an Nettigo sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, sensor_type: str):
        """Initialize."""
        super().__init__(coordinator)
        self.sensor_type = sensor_type

    @property
    def name(self) -> str:
        """Return the name."""
        return SENSORS[self.sensor_type][2]

    @property
    def state(self) -> Optional[str]:
        """Return the state."""
        if self.sensor_type == "BME280_pressure":
            return round(
                self.coordinator.data["sensordatavalues"][self.sensor_type] / 100
            )
        return round(self.coordinator.data["sensordatavalues"][self.sensor_type], 1)

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit the value is expressed in."""
        return SENSORS[self.sensor_type][0]

    @property
    def device_class(self) -> str:
        """Return the class of this sensor."""
        return SENSORS[self.sensor_type][1]

    @property
    def unique_id(self) -> str:
        """Return a unique_id for this entity."""
        return f"{self.coordinator.unique_id}-{self.sensor_type}"

    @property
    def device_info(self) -> dict:
        """Return the device info."""
        return self.coordinator.device_info
