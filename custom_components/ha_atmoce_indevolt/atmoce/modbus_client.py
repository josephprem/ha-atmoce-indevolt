"""Local Modbus TCP client for Atmoce MG100 / MC100 gateways."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from pymodbus.client import AsyncModbusTcpClient

from ..const import (
    ATMOCE_REG_BATTERY_DISCHARGE_ENERGY_TOTAL,
    ATMOCE_REG_BATTERY_POWER,
    ATMOCE_REG_BATTERY_SOC,
    ATMOCE_REG_GRID_CURRENT_A,
    ATMOCE_REG_GRID_CURRENT_B,
    ATMOCE_REG_GRID_CURRENT_C,
    ATMOCE_REG_GRID_EXPORT_ENERGY_TOTAL,
    ATMOCE_REG_GRID_IMPORT_ENERGY_TOTAL,
    ATMOCE_REG_GRID_POWER,
    ATMOCE_REG_GRID_VOLTAGE_A,
    ATMOCE_REG_GRID_VOLTAGE_B,
    ATMOCE_REG_GRID_VOLTAGE_C,
    ATMOCE_REG_PV_ENERGY_TOTAL,
    ATMOCE_REG_PV_POWER,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class AtmoceSnapshot:
    """Normalized telemetry from the Atmoce gateway."""

    pv_power_w: float | None = None
    grid_power_w: float | None = None
    battery_power_w: float | None = None
    battery_soc: float | None = None
    grid_voltage_a_v: float | None = None
    grid_voltage_b_v: float | None = None
    grid_voltage_c_v: float | None = None
    grid_current_a_a: float | None = None
    grid_current_b_a: float | None = None
    grid_current_c_a: float | None = None
    pv_energy_total_kwh: float | None = None
    grid_import_energy_total_kwh: float | None = None
    grid_export_energy_total_kwh: float | None = None
    battery_discharge_energy_total_kwh: float | None = None


class AtmoceModbusClient:
    """Thin async wrapper around pymodbus for Atmoce register map."""

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._client: AsyncModbusTcpClient | None = None

    async def connect(self) -> None:
        if self._client is None:
            self._client = AsyncModbusTcpClient(host=self._host, port=self._port)
        if not self._client.connected:
            connected = await self._client.connect()
            if not connected:
                raise ConnectionError(
                    f"Unable to connect to Atmoce gateway at {self._host}:{self._port}"
                )

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    async def async_get_snapshot(self) -> AtmoceSnapshot:
        await self.connect()
        assert self._client is not None

        power_block = await self._read_holding(register=ATMOCE_REG_PV_POWER, count=6)
        grid_block = await self._read_holding(register=ATMOCE_REG_GRID_VOLTAGE_A, count=7)
        energy_block = await self._read_holding(register=ATMOCE_REG_PV_ENERGY_TOTAL, count=30)

        return AtmoceSnapshot(
            pv_power_w=self._decode_int32(power_block, ATMOCE_REG_PV_POWER, ATMOCE_REG_PV_POWER),
            battery_power_w=self._decode_int32(
                power_block, ATMOCE_REG_BATTERY_POWER, ATMOCE_REG_PV_POWER
            ),
            grid_power_w=self._decode_int32(
                power_block, ATMOCE_REG_GRID_POWER, ATMOCE_REG_PV_POWER
            ),
            grid_voltage_a_v=self._decode_uint16(
                grid_block, ATMOCE_REG_GRID_VOLTAGE_A, ATMOCE_REG_GRID_VOLTAGE_A, 0.1
            ),
            grid_voltage_b_v=self._decode_uint16(
                grid_block, ATMOCE_REG_GRID_VOLTAGE_B, ATMOCE_REG_GRID_VOLTAGE_A, 0.1
            ),
            grid_voltage_c_v=self._decode_uint16(
                grid_block, ATMOCE_REG_GRID_VOLTAGE_C, ATMOCE_REG_GRID_VOLTAGE_A, 0.1
            ),
            grid_current_a_a=self._decode_int16(
                grid_block, ATMOCE_REG_GRID_CURRENT_A, ATMOCE_REG_GRID_VOLTAGE_A, 0.01
            ),
            grid_current_b_a=self._decode_int16(
                grid_block, ATMOCE_REG_GRID_CURRENT_B, ATMOCE_REG_GRID_VOLTAGE_A, 0.01
            ),
            grid_current_c_a=self._decode_int16(
                grid_block, ATMOCE_REG_GRID_CURRENT_C, ATMOCE_REG_GRID_VOLTAGE_A, 0.01
            ),
            battery_soc=self._decode_uint16(
                grid_block, ATMOCE_REG_BATTERY_SOC, ATMOCE_REG_GRID_VOLTAGE_A, 1.0
            ),
            pv_energy_total_kwh=self._decode_uint64(
                energy_block, ATMOCE_REG_PV_ENERGY_TOTAL, ATMOCE_REG_PV_ENERGY_TOTAL, 0.01
            ),
            battery_discharge_energy_total_kwh=self._decode_uint64(
                energy_block,
                ATMOCE_REG_BATTERY_DISCHARGE_ENERGY_TOTAL,
                ATMOCE_REG_PV_ENERGY_TOTAL,
                0.01,
            ),
            grid_export_energy_total_kwh=self._decode_uint64(
                energy_block,
                ATMOCE_REG_GRID_EXPORT_ENERGY_TOTAL,
                ATMOCE_REG_PV_ENERGY_TOTAL,
                0.01,
            ),
            grid_import_energy_total_kwh=self._decode_uint64(
                energy_block,
                ATMOCE_REG_GRID_IMPORT_ENERGY_TOTAL,
                ATMOCE_REG_PV_ENERGY_TOTAL,
                0.01,
            ),
        )

    async def async_write_uint32(self, register: int, value: int) -> None:
        await self.connect()
        assert self._client is not None
        high = (value >> 16) & 0xFFFF
        low = value & 0xFFFF
        result = await self._client.write_registers(register, [high, low])
        if result.isError():
            raise OSError(f"Modbus write failed for register {register}: {result}")

    async def async_write_uint16(self, register: int, value: int) -> None:
        await self.connect()
        assert self._client is not None
        result = await self._client.write_register(register, value)
        if result.isError():
            raise OSError(f"Modbus write failed for register {register}: {result}")

    async def _read_holding(self, register: int, count: int) -> list[int]:
        assert self._client is not None
        response = await self._client.read_holding_registers(
            address=register, count=count, device_id=1
        )
        if response.isError():
            raise OSError(
                f"Modbus read failed for register {register} (count={count}): {response}"
            )
        return list(response.registers)

    @staticmethod
    def _offset(register: int, base_register: int) -> int:
        return register - base_register

    @staticmethod
    def _decode_uint16(
        block: list[int], register: int, base_register: int, scale: float
    ) -> float | None:
        offset = AtmoceModbusClient._offset(register, base_register)
        if offset < 0 or offset >= len(block):
            return None
        return float(block[offset]) * scale

    @staticmethod
    def _decode_int16(
        block: list[int], register: int, base_register: int, scale: float
    ) -> float | None:
        offset = AtmoceModbusClient._offset(register, base_register)
        if offset < 0 or offset >= len(block):
            return None
        raw = block[offset]
        if raw > 0x7FFF:
            raw -= 0x10000
        return float(raw) * scale

    @staticmethod
    def _decode_int32(
        block: list[int], register: int, base_register: int
    ) -> float | None:
        offset = AtmoceModbusClient._offset(register, base_register)
        if offset < 0 or offset + 1 >= len(block):
            return None
        high = block[offset]
        low = block[offset + 1]
        raw = (high << 16) + low
        if raw & 0x80000000:
            raw -= 0x100000000
        return float(raw)

    @staticmethod
    def _decode_uint64(
        block: list[int], register: int, base_register: int, scale: float
    ) -> float | None:
        offset = AtmoceModbusClient._offset(register, base_register)
        if offset < 0 or offset + 3 >= len(block):
            return None
        value = 0
        for index in range(4):
            value = (value << 16) + block[offset + index]
        return float(value) * scale
