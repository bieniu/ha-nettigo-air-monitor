"""Support for the Nettigo air_quality service."""
from typing import Callable, Optional

from homeassistant.components.air_quality import AirQualityEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import ATTR_SENSORS, DEFAULT_NAME, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable
) -> None:
    """Add a Nettigo entities from a config_entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for sensor in ["SDS", "SPS30"]:
        if f"{sensor}_P1" in coordinator.data[ATTR_SENSORS]:
            entities.append(NettigoAirQuality(coordinator, sensor))

    async_add_entities(entities, False)


def round_state(func):
    """Round state."""

    def _decorator(self):
        res = func(self)
        if isinstance(res, float):
            return round(res)
        return res

    return _decorator


class NettigoAirQuality(CoordinatorEntity, AirQualityEntity):
    """Define an Nettigo air quality."""

    def __init__(self, coordinator: DataUpdateCoordinator, sensor_type: str):
        """Initialize."""
        super().__init__(coordinator)
        self.sensor_type = sensor_type

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{DEFAULT_NAME} {self.sensor_type}"

    @property
    @round_state
    def particulate_matter_2_5(self) -> Optional[int]:
        """Return the particulate matter 2.5 level."""
        return self.coordinator.data[ATTR_SENSORS].get(f"{self.sensor_type}_P2")

    @property
    @round_state
    def particulate_matter_10(self) -> Optional[int]:
        """Return the particulate matter 10 level."""
        return self.coordinator.data[ATTR_SENSORS].get(f"{self.sensor_type}_P1")

    @property
    @round_state
    def carbon_dioxide(self) -> Optional[int]:
        """Return the particulate matter 10 level."""
        return self.coordinator.data[ATTR_SENSORS].get("conc_co2_ppm")

    @property
    def unique_id(self) -> str:
        """Return a unique_id for this entity."""
        return f"{self.coordinator.unique_id}-{self.sensor_type}"

    @property
    def device_info(self) -> dict:
        """Return the device info."""
        return self.coordinator.device_info
