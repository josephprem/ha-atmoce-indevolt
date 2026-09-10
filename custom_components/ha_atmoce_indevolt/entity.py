"""Shared entity helpers."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATMOCE_DEVICE, DOMAIN, HEMS_DEVICE, INDEVOLT_DEVICE
from .coordinator import HemsCoordinator


class HemsEntity(CoordinatorEntity[HemsCoordinator]):
    """Base entity for the HEMS integration."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HemsCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id, HEMS_DEVICE)},
            name="Home Energy Management",
            manufacturer="ha-atmoce-indevolt",
            model="HEMS Coordinator",
        )


class AtmoceEntity(HemsEntity):
    """Entity attached to the Atmoce gateway device."""

    @property
    def device_info(self) -> DeviceInfo:
        host = self.coordinator.atmoce._host if self.coordinator.atmoce else "unknown"
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id, ATMOCE_DEVICE)},
            name="Atmoce Gateway",
            manufacturer="Atmoce",
            model="MG100 / MC100",
            configuration_url=f"http://{host}",
        )


class IndevoltEntity(HemsEntity):
    """Entity attached to the Indevolt storage device."""

    @property
    def device_info(self) -> DeviceInfo:
        host = self.coordinator.indevolt._host if self.coordinator.indevolt else "unknown"
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id, INDEVOLT_DEVICE)},
            name="Indevolt Storage",
            manufacturer="Indevolt",
            model="SF3000AC + SFA3600",
            configuration_url=f"http://{host}:{self.coordinator.indevolt._port if self.coordinator.indevolt else 8080}",
        )
