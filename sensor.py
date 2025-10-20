from datetime import date, datetime
from decimal import Decimal

from homeassistant.helpers.typing import StateType, UndefinedType
import logging
from .const import DOMAIN
from .coordinator import PranaCoordinator
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import device_registry

LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = [
        PranaSensor(
            hass,
            coordinator,
            "Temperature In Sensor",
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

    async_add_entities(sensors)

class PranaSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Prana sensor."""

    def __init__(self, hass, coordinator: PranaCoordinator, name: str, entry_id: str, sensor_type: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        _attr_has_entity_name = True
        self._hass = hass
        self.coordinator = coordinator
        self._name = name
        self._entry_id = entry_id
        self._sensor_type = sensor_type

        LOGGER.warning(f"Initialized sensor: {self._name} of type {self._sensor_type}")

    @property
    def device_info(self):
        """Return device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.coordinator.mac)
            },
            name=self.name,
            connections={(device_registry.CONNECTION_NETWORK_MAC, self.coordinator.mac)},
        )

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        return self.coordinator.get_value(self._sensor_type)

    @property
    def native_unit_of_measurement(self) -> str | None:
        return self.coordinator.get_unit(self._sensor_type)

    @property
    def name(self) -> str | UndefinedType | None:
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self.coordinator.mac.replace(":", "") + "_" + self._sensor_type