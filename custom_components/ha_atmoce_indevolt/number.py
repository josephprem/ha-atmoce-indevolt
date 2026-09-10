"""Number platform for Indevolt limits."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HemsCoordinator
from .entity import IndevoltEntity


class IndevoltBackupSocNumber(IndevoltEntity, NumberEntity):
    _attr_translation_key = "backup_soc"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_native_min_value = 5
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: HemsCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_backup_soc"

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data.indevolt is None:
            return None
        value = self.coordinator.data.indevolt.get("backup_soc")
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        if self.coordinator.indevolt is None:
            return
        await self.coordinator.indevolt.async_set_backup_soc(int(value))
        await self.coordinator.async_request_refresh()


class IndevoltFeedInLimitNumber(IndevoltEntity, NumberEntity):
    _attr_translation_key = "feed_in_limit"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_native_min_value = 50
    _attr_native_max_value = 3000
    _attr_native_step = 50
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: HemsCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_feed_in_limit"

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data.indevolt is None:
            return None
        value = self.coordinator.data.indevolt.get("feed_in_limit_w")
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        if self.coordinator.indevolt is None:
            return
        await self.coordinator.indevolt.async_set_feed_in_limit(int(value))
        await self.coordinator.async_request_refresh()


class IndevoltMaxAcOutputNumber(IndevoltEntity, NumberEntity):
    _attr_translation_key = "max_ac_output"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_native_min_value = 50
    _attr_native_max_value = 3000
    _attr_native_step = 50
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: HemsCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_max_ac_output"

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data.indevolt is None:
            return None
        value = self.coordinator.data.indevolt.get("max_ac_output_w")
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        if self.coordinator.indevolt is None:
            return
        await self.coordinator.indevolt.async_set_max_ac_output(int(value))
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HemsCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    if coordinator.indevolt is None:
        return
    async_add_entities(
        [
            IndevoltBackupSocNumber(coordinator, entry.entry_id),
            IndevoltFeedInLimitNumber(coordinator, entry.entry_id),
            IndevoltMaxAcOutputNumber(coordinator, entry.entry_id),
        ]
    )
