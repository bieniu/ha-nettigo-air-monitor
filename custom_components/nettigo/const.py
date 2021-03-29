"""Constants for Nettigo integration."""
from datetime import timedelta

from homeassistant.const import (
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    PERCENTAGE,
    PRESSURE_HPA,
    TEMP_CELSIUS,
)

DEFAULT_NAME = "Nettigo Air Monitor"
DEFAULT_UPDATE_INTERVAL = timedelta(minutes=5)
DOMAIN = "nettigo"
MANUFACTURER = "Nettigo"

SENSORS = {
    "BME280_humidity": (PERCENTAGE, DEVICE_CLASS_HUMIDITY, "BME280 Humidity"),
    "BME280_pressure": (PRESSURE_HPA, DEVICE_CLASS_PRESSURE, "BME280 Pressure"),
    "BME280_temperature": (
        TEMP_CELSIUS,
        DEVICE_CLASS_TEMPERATURE,
        "BME280 Temperature",
    ),
}
