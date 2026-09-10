"""Switch platform for Indevolt toggles."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, INDEVOLT_GRID_CHARGING_ENABLED
from .coordinator import HemsCoordinator
from .entity import IndevoltEntity


class IndevoltGridChargingSwitch(IndevoltEntity, SwitchEntity):
    _attr_translation_key = "grid_charging"

    def __init__(self, coordinator: HemsCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_grid_charging"

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data.indevolt is None:
            return None
        value = self.coordinator.data.indevolt.get("grid_charging")
        if value is None:
            return None
        return int(value) == INDEVOLT_GRID_CHARGING_ENABLED

    async def async_turn_on(self, **kwargs) -> None:
        if self.coordinator.indevolt is None:
            return
        await self.coordinator.indevolt.async_set_grid_charging(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        if self.coordinator.indevolt is None:
            return
        await self.coordinator.indevolt.async_set_grid_charging(False)
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HemsCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    if coordinator.indevolt is None:
        return
    async_add_entities([IndevoltGridChargingSwitch(coordinator, entry.entry_id)])
