"""Support for Prana cover (mapped to device brightness).
"""
from . import DOMAIN

from datetime import datetime, timedelta
import logging

from homeassistant.components.cover import (
    CoverEntity,
    CoverEntityFeature
)

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.core import callback
from homeassistant.helpers import device_registry

from .coordinator import PranaCoordinator

LOGGER = logging.getLogger(__name__)

MAX_BRIGHTNESS = 6

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        SpeedInPranaCover(coordinator, config_entry),
        SpeedOutPranaCover(coordinator, config_entry)
    ])


class BasePranaCover(CoordinatorEntity, CoverEntity):
    """Representation of a Prana cover (using brightness as position)."""

    def __init__(self, coordinator: PranaCoordinator, config_entry):
        super().__init__(coordinator)
        # Annotate with concrete coordinator type so attributes are recognized by linters
        self.coordinator: PranaCoordinator = coordinator
        self._name = config_entry.data.get("name")
        self._entry_id = f"{config_entry.entry_id}_cover"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self.coordinator.lastRead is not None and (
            self.coordinator.lastRead > datetime.now() - timedelta(minutes=5)
        )

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.mac)},
            name=self.name,
            connections={(device_registry.CONNECTION_NETWORK_MAC, self.coordinator.mac)},
        )

    @property
    def supported_features(self) -> int:
        return CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE

class SpeedInPranaCover(BasePranaCover):
    @property
    def name(self) -> str:
        return self._name + " Speed In"

    @property
    def unique_id(self) -> str:
        return f"{self.coordinator.mac.replace(':', '')}speed_in_cover"

    @property
    def current_cover_position(self) -> int | None:
        """Return current position of the cover (0-100).

        Mapping: coordinator.speed_in (1-5) -> 0-100 percent.
        """
        s = self.coordinator.speed_in
        if s is None:
            return None
        # speed_in expected in range 1..5 -> map to 0..100
        try:
            pos = round(((s - 1) / 4) * 100)
        except Exception:
            return None
        return int(pos)

    @property
    def is_closed(self) -> bool | None:
        # Consider the cover closed when device is off
        if self.coordinator.is_on is None:
            return None
        return not self.coordinator.is_on

    @property
    def extra_state_attributes(self):
        return {
            "last_updated": self.coordinator.lastRead,
        }

    async def async_open_cover(self, **kwargs) -> None:
        current = self.coordinator.speed_in or 0
        await self.coordinator.set_speed_in(current + 1)

        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs) -> None:
        current = self.coordinator.speed_in or 0
        await self.coordinator.set_speed_in(current - 1 if current > 1 else 0)

        self.async_write_ha_state()

class SpeedOutPranaCover(BasePranaCover):
    @property
    def name(self) -> str:
        return self._name + " Speed Out"

    @property
    def unique_id(self) -> str:
        return f"{self.coordinator.mac.replace(':', '')}speed_out_cover"

    @property
    def current_cover_position(self) -> int | None:
        """Return current position of the cover (0-100).

        Mapping: coordinator.speed_in (1-5) -> 0-100 percent.
        """
        s = self.coordinator.speed_out
        if s is None:
            return None
        # speed_in expected in range 1..5 -> map to 0..100
        try:
            pos = round(((s - 1) / 4) * 100)
        except Exception:
            return None
        return int(pos)

    @property
    def is_closed(self) -> bool | None:
        # Consider the cover closed when device is off
        if self.coordinator.is_on is None:
            return None
        return not self.coordinator.is_on

    @property
    def extra_state_attributes(self):
        return {
            "last_updated": self.coordinator.lastRead,
        }

    async def async_open_cover(self, **kwargs) -> None:
        current = self.coordinator.speed_out or 0
        await self.coordinator.set_speed_out(current + 1)

        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs) -> None:
        current = self.coordinator.speed_out or 0
        await self.coordinator.set_speed_out(current - 1 if current > 1 else 0)

        self.async_write_ha_state()
