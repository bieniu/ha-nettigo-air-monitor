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

    if (
        "SDS_P1" in coordinator.data[ATTR_SENSORS]
        or "SPS30_P1" in coordinator.data[ATTR_SENSORS]
    ):
        async_add_entities([NettigoAirQuality(coordinator)], False)


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

    def __init__(self, coordinator: DataUpdateCoordinator):
        """Initialize."""
        super().__init__(coordinator)

    @property
    def name(self) -> str:
        """Return the name."""
        return DEFAULT_NAME

    @property
    @round_state
    def particulate_matter_2_5(self) -> Optional[int]:
        """Return the particulate matter 2.5 level."""
        return self.coordinator.data[ATTR_SENSORS].get(
            "SDS_P2"
        ) or self.coordinator.data[ATTR_SENSORS].get("SPS30_P2")

    @property
    @round_state
    def particulate_matter_10(self) -> Optional[int]:
        """Return the particulate matter 10 level."""
        return self.coordinator.data[ATTR_SENSORS].get(
            "SDS_P1"
        ) or self.coordinator.data[ATTR_SENSORS].get("SDS_P1")

    @property
    @round_state
    def carbon_dioxide(self) -> Optional[int]:
        """Return the particulate matter 10 level."""
        return self.coordinator.data[ATTR_SENSORS].get("conc_co2_ppm")

    @property
    def unique_id(self) -> str:
        """Return a unique_id for this entity."""
        return self.coordinator.unique_id

    @property
    def device_info(self) -> dict:
        """Return the device info."""
        return self.coordinator.device_info
