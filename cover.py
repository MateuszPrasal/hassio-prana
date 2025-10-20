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
    async_add_entities([PranaCover(coordinator, config_entry)])


class PranaCover(CoordinatorEntity, CoverEntity):
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
        LOGGER.debug('PranaCover coordinator update')
        self.async_write_ha_state()

    @property
    def unique_id(self) -> str:
        return f"{self.coordinator.mac.replace(':', '')}_cover"

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
        return CoverEntityFeature.SET_POSITION

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

    async def async_set_cover_position(self, **kwargs) -> None:
        position = kwargs.get("position")
        LOGGER.debug('Kwargs for set_cover_position: %s', kwargs)
        if position is None:
            return
        # map 0..100 to speed_in range 1..5
        pct = int(position)
        if pct <= 0:
            target = 1
        else:
            # scale 0..100 to 1..5
            target = min(5, max(1, round(1 + (pct / 100) * 4)))

        LOGGER.debug(f'Setting Prana cover position to {target}')

        # If coordinator already has desired value, nothing to do
        current = self.coordinator.speed_in or 0
        if current == target:
            await self.coordinator.async_request_refresh()
            self.async_write_ha_state()
            return

        await self.coordinator.set_speed(target)
