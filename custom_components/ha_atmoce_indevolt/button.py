"""Button platform for quick HEMS actions."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATMOCE_REG_BATTERY_FORCE_CONTROL,
    DOMAIN,
    INDEVOLT_MODE_SELF_CONSUMPTION,
)
from .coordinator import HemsCoordinator
from .entity import AtmoceEntity, IndevoltEntity


class IndevoltReturnToSelfConsumptionButton(IndevoltEntity, ButtonEntity):
    _attr_translation_key = "return_self_consumption"

    def __init__(self, coordinator: HemsCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_return_self_consumption"

    async def async_press(self) -> None:
        if self.coordinator.indevolt is None:
            return
        await self.coordinator.indevolt.async_set_working_mode(INDEVOLT_MODE_SELF_CONSUMPTION)
        await self.coordinator.async_request_refresh()


class AtmoceReleaseForcedBatteryButton(AtmoceEntity, ButtonEntity):
    _attr_translation_key = "release_forced_battery"

    def __init__(self, coordinator: HemsCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_release_forced_battery"

    async def async_press(self) -> None:
        if self.coordinator.atmoce is None:
            return
        # 2 = exit forced charge/discharge mode on Atmoce gateways.
        await self.coordinator.atmoce.async_write_uint16(ATMOCE_REG_BATTERY_FORCE_CONTROL, 2)
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HemsCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities: list[ButtonEntity] = []
    if coordinator.indevolt is not None:
        entities.append(IndevoltReturnToSelfConsumptionButton(coordinator, entry.entry_id))
    if coordinator.atmoce is not None:
        entities.append(AtmoceReleaseForcedBatteryButton(coordinator, entry.entry_id))
    async_add_entities(entities)
