"""Select platform for Indevolt energy mode."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    INDEVOLT_MODE_REALTIME,
    INDEVOLT_MODE_SCHEDULE,
    INDEVOLT_MODE_SELF_CONSUMPTION,
)
from .coordinator import HemsCoordinator
from .entity import IndevoltEntity

MODE_TO_VALUE = {
    "self_consumption": INDEVOLT_MODE_SELF_CONSUMPTION,
    "realtime_control": INDEVOLT_MODE_REALTIME,
    "schedule": INDEVOLT_MODE_SCHEDULE,
}
VALUE_TO_MODE = {value: key for key, value in MODE_TO_VALUE.items()}


class IndevoltEnergyModeSelect(IndevoltEntity, SelectEntity):
    """Expose Indevolt working mode as a select entity."""

    _attr_translation_key = "energy_mode"

    def __init__(self, coordinator: HemsCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_energy_mode"
        self._attr_options = list(MODE_TO_VALUE)

    @property
    def current_option(self) -> str | None:
        if self.coordinator.data.indevolt is None:
            return None
        value = self.coordinator.data.indevolt.get("working_mode")
        return VALUE_TO_MODE.get(value)

    async def async_select_option(self, option: str) -> None:
        if self.coordinator.indevolt is None:
            return
        await self.coordinator.indevolt.async_set_working_mode(MODE_TO_VALUE[option])
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HemsCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    if coordinator.indevolt is None:
        return
    async_add_entities([IndevoltEnergyModeSelect(coordinator, entry.entry_id)])
