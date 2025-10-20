from datetime import date, datetime
from decimal import Decimal

from homeassistant.helpers.typing import StateType

from .const import DOMAIN

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_devices):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = [
        PranaSensor(
            hass,
            coordinator,
            "Temperatur In Sensor",
            f"{config_entry.entry_id}_temperature_in",
            "temperature_in",
        ),
        PranaSensor(
            hass,
            coordinator,
            "Temperatur Out Sensor",
            f"{config_entry.entry_id}_temperature_out",
            "temperature_out",
        ),
        PranaSensor(
            hass,
            coordinator,
            "Humidity Sensor",
            f"{config_entry.entry_id}_humidity",
            "humidity",
        ),
        PranaSensor(
            hass,
            coordinator,
            "Pressure Sensor",
            f"{config_entry.entry_id}_pressure",
            "pressure",
        ),
        PranaSensor(
            hass,
            coordinator,
            "VOC Sensor",
            f"{config_entry.entry_id}_voc",
            "voc",
        ),
        PranaSensor(
            hass,
            coordinator,
            "CO2 Sensor",
            f"{config_entry.entry_id}_co2",
            "co2",
        ),
        PranaSensor(
            hass,
            coordinator,
            "Speed In Sensor",
            f"{config_entry.entry_id}_speed_in",
            "speed_in",
        ),
        PranaSensor(
            hass,
            coordinator,
            "Speed Out Sensor",
            f"{config_entry.entry_id}_speed_out",
            "speed_out",
        ),
    ]

    async_add_devices(sensors)

class PranaSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Prana sensor."""

    def __init__(self, hass, coordinator, name: str, entry_id: str, sensor_type: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        _attr_has_entity_name = True
        self._hass = hass
        self.coordinator = coordinator
        self._name = name
        self._entry_id = entry_id
        self._sensor_type = sensor_type

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        return self.coordinator.get_sensor_value(self._sensor_type)

    @property
    def native_unit_of_measurement(self) -> str | None:
        return self.coordinator.get_sensor_unit(self._sensor_type)