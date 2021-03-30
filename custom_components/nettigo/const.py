"""Constants for Nettigo integration."""
from datetime import timedelta

from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    PERCENTAGE,
    PRESSURE_HPA,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    TEMP_CELSIUS,
)

ATTR_SENSORS = "sensordatavalues"
DEFAULT_NAME = "Nettigo Air Monitor"
DEFAULT_UPDATE_INTERVAL = timedelta(minutes=5)
DOMAIN = "nettigo"
MANUFACTURER = "Nettigo"

SENSORS = {
    "BME280_humidity": ("BME280 Humidity", PERCENTAGE, DEVICE_CLASS_HUMIDITY, None, True),
    "BME280_pressure": ("BME280 Pressure", PRESSURE_HPA, DEVICE_CLASS_PRESSURE, None, True),
    "BME280_temperature": (
        "BME280 Temperature",
        TEMP_CELSIUS,
        DEVICE_CLASS_TEMPERATURE,
        None, True,
    ),
    "BMP280_pressure": ("BMP280 Pressure", PRESSURE_HPA, DEVICE_CLASS_PRESSURE, None, True),
    "BMP280_temperature": (
        "BMP280 Temperature",
        TEMP_CELSIUS,
        DEVICE_CLASS_TEMPERATURE,
        None, True,
    ),
    "humidity": ("DHT22 Humidity", PERCENTAGE, DEVICE_CLASS_HUMIDITY, None, True),
    "SHT3X_humidity": ("SHT3X Humidity", PERCENTAGE, DEVICE_CLASS_HUMIDITY, None, True),
    "SHT3X_temperature": (
        "SHT3X Temperature",
        TEMP_CELSIUS,
        DEVICE_CLASS_TEMPERATURE,
        None, True,
    ),
    "signal": (
        f"{DEFAULT_NAME} Signal Strength",
        SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        DEVICE_CLASS_SIGNAL_STRENGTH,
        None, False,
    ),
    "temperature": ("DHT22 Temperature", TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE, None, True),
    "SPS30_P0": ("SPS30 Particulate Matter 1.0", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, None, "mdi:blur", True)
}
