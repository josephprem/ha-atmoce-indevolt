"""Data coordinators for Atmoce, Indevolt, and HEMS aggregation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .atmoce import AtmoceModbusClient, AtmoceSnapshot
from .const import DEFAULT_SCAN_INTERVAL
from .indevolt import IndevoltApiClient, IndevoltSnapshot

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class HemsData:
    """Combined site telemetry used by HEMS sensors."""

    atmoce: AtmoceSnapshot | None = None
    indevolt: IndevoltSnapshot | None = None
    computed: dict[str, Any] = field(default_factory=dict)


class HemsCoordinator(DataUpdateCoordinator[HemsData]):
    """Poll Atmoce and Indevolt devices and compute HEMS metrics."""

    def __init__(
        self,
        hass: HomeAssistant,
        atmoce: AtmoceModbusClient | None,
        indevolt: IndevoltApiClient | None,
        scan_interval: int,
        panel_count: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="ha_atmoce_indevolt",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.atmoce = atmoce
        self.indevolt = indevolt
        self.panel_count = panel_count

    async def _async_update_data(self) -> HemsData:
        data = HemsData()
        errors: list[str] = []

        if self.atmoce is not None:
            try:
                data.atmoce = await self.atmoce.async_get_snapshot()
            except Exception as err:  # noqa: BLE001 - surface upstream device errors
                errors.append(f"Atmoce: {err}")

        if self.indevolt is not None:
            try:
                data.indevolt = await self.indevolt.async_get_snapshot()
            except Exception as err:  # noqa: BLE001 - surface upstream device errors
                errors.append(f"Indevolt: {err}")

        if data.atmoce is None and data.indevolt is None:
            raise UpdateFailed("; ".join(errors) or "No device data available")

        data.computed = self._compute_hems_metrics(data)
        if errors:
            _LOGGER.warning("Partial update: %s", "; ".join(errors))
        return data

    def _compute_hems_metrics(self, data: HemsData) -> dict[str, Any]:
        pv_power = data.atmoce.pv_power_w if data.atmoce else None
        grid_power = data.atmoce.grid_power_w if data.atmoce else None
        battery_power = None
        if data.indevolt is not None:
            battery_power = data.indevolt.get("battery_power_w")
        elif data.atmoce is not None:
            battery_power = data.atmoce.battery_power_w

        site_consumption = None
        pv_surplus = None
        self_consumption_rate = None

        if pv_power is not None and grid_power is not None:
            # Positive grid import means the site is drawing from the grid.
            site_consumption = pv_power + grid_power
            if site_consumption < 0:
                site_consumption = 0.0
            pv_surplus = max(pv_power - site_consumption, 0.0)
            if pv_power > 0:
                self_consumption_rate = min(
                    max((pv_power - max(grid_power, 0.0)) / pv_power * 100.0, 0.0), 100.0
                )

        return {
            "panel_count": self.panel_count,
            "pv_power_w": pv_power,
            "grid_power_w": grid_power,
            "battery_power_w": battery_power,
            "site_consumption_w": site_consumption,
            "pv_surplus_w": pv_surplus,
            "self_consumption_rate": self_consumption_rate,
        }
