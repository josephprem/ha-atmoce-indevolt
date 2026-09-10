"""HTTP OpenData client for Indevolt SF3000 / SolidFlex devices."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

import aiohttp

from ..const import (
    INDEVOLT_POINT_AC_INPUT_ENERGY,
    INDEVOLT_POINT_AC_INPUT_POWER,
    INDEVOLT_POINT_AC_OUTPUT_ENERGY,
    INDEVOLT_POINT_AC_OUTPUT_POWER,
    INDEVOLT_POINT_BACKUP_SOC,
    INDEVOLT_POINT_BATTERY_POWER,
    INDEVOLT_POINT_BATTERY_SOC,
    INDEVOLT_POINT_BATTERY_STATE,
    INDEVOLT_POINT_BYPASS_POWER,
    INDEVOLT_POINT_FEED_IN_LIMIT,
    INDEVOLT_POINT_GRID_CHARGING,
    INDEVOLT_POINT_GRID_FREQUENCY,
    INDEVOLT_POINT_GRID_VOLTAGE,
    INDEVOLT_POINT_INVERTER_INPUT_LIMIT,
    INDEVOLT_POINT_MAX_AC_OUTPUT,
    INDEVOLT_POINT_METER_CONNECTION,
    INDEVOLT_POINT_METER_POWER_LEGACY,
    INDEVOLT_POINT_METER_POWER_SF,
    INDEVOLT_POINT_PACK_SOC,
    INDEVOLT_POINT_PACK_TEMP,
    INDEVOLT_POINT_RATED_CAPACITY,
    INDEVOLT_POINT_WORKING_MODE,
    INDEVOLT_SET_BACKUP_SOC,
    INDEVOLT_SET_BYPASS,
    INDEVOLT_SET_FEED_IN_LIMIT,
    INDEVOLT_SET_GRID_CHARGING,
    INDEVOLT_SET_INVERTER_INPUT_LIMIT,
    INDEVOLT_SET_MAX_AC_OUTPUT,
    INDEVOLT_SET_RT_POWER,
    INDEVOLT_SET_RT_STATE,
    INDEVOLT_SET_RT_TARGET_SOC,
    INDEVOLT_SET_WORKING_MODE,
)

_LOGGER = logging.getLogger(__name__)

READ_POINTS: list[int] = sorted(
    {
        INDEVOLT_POINT_WORKING_MODE,
        INDEVOLT_POINT_RATED_CAPACITY,
        INDEVOLT_POINT_GRID_CHARGING,
        INDEVOLT_POINT_INVERTER_INPUT_LIMIT,
        INDEVOLT_POINT_AC_INPUT_POWER,
        INDEVOLT_POINT_AC_OUTPUT_POWER,
        INDEVOLT_POINT_FEED_IN_LIMIT,
        INDEVOLT_POINT_MAX_AC_OUTPUT,
        INDEVOLT_POINT_BACKUP_SOC,
        INDEVOLT_POINT_AC_INPUT_ENERGY,
        INDEVOLT_POINT_AC_OUTPUT_ENERGY,
        INDEVOLT_POINT_BATTERY_POWER,
        INDEVOLT_POINT_BATTERY_STATE,
        INDEVOLT_POINT_BATTERY_SOC,
        INDEVOLT_POINT_GRID_VOLTAGE,
        INDEVOLT_POINT_GRID_FREQUENCY,
        INDEVOLT_POINT_METER_CONNECTION,
        INDEVOLT_POINT_METER_POWER_SF,
        INDEVOLT_POINT_METER_POWER_LEGACY,
        INDEVOLT_POINT_BYPASS_POWER,
        *INDEVOLT_POINT_PACK_SOC.values(),
        *INDEVOLT_POINT_PACK_TEMP.values(),
    }
)


@dataclass(slots=True)
class IndevoltSnapshot:
    """Normalized telemetry from an Indevolt device."""

    values: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str) -> Any:
        return self.values.get(key)


class IndevoltApiClient:
    """Minimal async client for Indevolt OpenData HTTP RPC."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        timeout: int = 10,
    ) -> None:
        self._session = session
        self._host = host
        self._port = port
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    @property
    def base_url(self) -> str:
        return f"http://{self._host}:{self._port}/rpc"

    async def async_get_snapshot(self) -> IndevoltSnapshot:
        raw = await self._get_data(READ_POINTS)
        values: dict[str, Any] = {
            "working_mode": raw.get(str(INDEVOLT_POINT_WORKING_MODE)),
            "rated_capacity_kwh": raw.get(str(INDEVOLT_POINT_RATED_CAPACITY)),
            "grid_charging": raw.get(str(INDEVOLT_POINT_GRID_CHARGING)),
            "inverter_input_limit_w": raw.get(str(INDEVOLT_POINT_INVERTER_INPUT_LIMIT)),
            "ac_input_power_w": raw.get(str(INDEVOLT_POINT_AC_INPUT_POWER)),
            "ac_output_power_w": raw.get(str(INDEVOLT_POINT_AC_OUTPUT_POWER)),
            "feed_in_limit_w": raw.get(str(INDEVOLT_POINT_FEED_IN_LIMIT)),
            "max_ac_output_w": raw.get(str(INDEVOLT_POINT_MAX_AC_OUTPUT)),
            "backup_soc": raw.get(str(INDEVOLT_POINT_BACKUP_SOC)),
            "ac_input_energy_kwh": raw.get(str(INDEVOLT_POINT_AC_INPUT_ENERGY)),
            "ac_output_energy_kwh": raw.get(str(INDEVOLT_POINT_AC_OUTPUT_ENERGY)),
            "battery_power_w": raw.get(str(INDEVOLT_POINT_BATTERY_POWER)),
            "battery_state": raw.get(str(INDEVOLT_POINT_BATTERY_STATE)),
            "battery_soc": raw.get(str(INDEVOLT_POINT_BATTERY_SOC)),
            "grid_voltage_v": raw.get(str(INDEVOLT_POINT_GRID_VOLTAGE)),
            "grid_frequency_hz": raw.get(str(INDEVOLT_POINT_GRID_FREQUENCY)),
            "meter_connection": raw.get(str(INDEVOLT_POINT_METER_CONNECTION)),
            "meter_power_w": (
                raw.get(str(INDEVOLT_POINT_METER_POWER_SF))
                if raw.get(str(INDEVOLT_POINT_METER_POWER_SF)) is not None
                else raw.get(str(INDEVOLT_POINT_METER_POWER_LEGACY))
            ),
            "bypass_power_w": raw.get(str(INDEVOLT_POINT_BYPASS_POWER)),
        }
        for pack_index, point in INDEVOLT_POINT_PACK_SOC.items():
            values[f"pack_{pack_index}_soc"] = raw.get(str(point))
        for pack_index, point in INDEVOLT_POINT_PACK_TEMP.items():
            values[f"pack_{pack_index}_temperature_c"] = raw.get(str(point))
        return IndevoltSnapshot(values=values)

    async def async_set_working_mode(self, mode: int) -> None:
        await self._set_data(INDEVOLT_SET_WORKING_MODE, mode)

    async def async_charge(self, power_w: int, target_soc: int) -> None:
        await self.async_set_working_mode(4)
        await self._set_data(INDEVOLT_SET_RT_STATE, 1)
        await self._set_data(INDEVOLT_SET_RT_POWER, power_w)
        await self._set_data(INDEVOLT_SET_RT_TARGET_SOC, target_soc)

    async def async_discharge(self, power_w: int, target_soc: int) -> None:
        await self.async_set_working_mode(4)
        await self._set_data(INDEVOLT_SET_RT_STATE, 2)
        await self._set_data(INDEVOLT_SET_RT_POWER, power_w)
        await self._set_data(INDEVOLT_SET_RT_TARGET_SOC, target_soc)

    async def async_set_backup_soc(self, value: int) -> None:
        await self._set_data(INDEVOLT_SET_BACKUP_SOC, value)

    async def async_set_grid_charging(self, enabled: bool) -> None:
        await self._set_data(INDEVOLT_SET_GRID_CHARGING, 1 if enabled else 0)

    async def async_set_feed_in_limit(self, watts: int) -> None:
        await self._set_data(INDEVOLT_SET_FEED_IN_LIMIT, watts)

    async def async_set_max_ac_output(self, watts: int) -> None:
        await self._set_data(INDEVOLT_SET_MAX_AC_OUTPUT, watts)

    async def async_set_inverter_input_limit(self, watts: int) -> None:
        await self._set_data(INDEVOLT_SET_INVERTER_INPUT_LIMIT, watts)

    async def async_set_bypass(self, enabled: bool) -> None:
        await self._set_data(INDEVOLT_SET_BYPASS, 1 if enabled else 0)

    async def _get_data(self, points: list[int]) -> dict[str, Any]:
        config = json.dumps({"t": points}, separators=(",", ":"))
        url = f"{self.base_url}/Indevolt.GetData?config={quote(config)}"
        async with self._session.post(url, timeout=self._timeout) as response:
            response.raise_for_status()
            payload = await response.json(content_type=None)
        if not isinstance(payload, dict):
            raise ValueError("Unexpected Indevolt.GetData response")
        return payload

    async def _set_data(self, point: int, value: int | list[int]) -> None:
        if isinstance(value, list):
            config = json.dumps({"f": 16, "t": point, "v": value}, separators=(",", ":"))
        else:
            config = json.dumps({"f": 16, "t": point, "v": [value]}, separators=(",", ":"))
        url = f"{self.base_url}/Indevolt.SetData?config={quote(config)}"
        async with self._session.post(url, timeout=self._timeout) as response:
            response.raise_for_status()
