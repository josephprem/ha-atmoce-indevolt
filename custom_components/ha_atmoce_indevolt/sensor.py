"""Sensor platform for Atmoce + Indevolt HEMS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfElectricPotential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, INDEVOLT_POINT_PACK_SOC
from .coordinator import HemsCoordinator, HemsData
from .atmozen_setup import async_add_atmozen_entities
from .entity import AtmoceEntity, HemsEntity, IndevoltEntity


@dataclass(frozen=True, kw_only=True)
class HemsSensorDescription(SensorEntityDescription):
    """Sensor description with source selector."""

    source: str
    value_key: str


ATMOCE_SENSORS: tuple[HemsSensorDescription, ...] = (
    HemsSensorDescription(
        key="pv_power",
        translation_key="pv_power",
        source="atmoce",
        value_key="pv_power_w",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HemsSensorDescription(
        key="grid_power",
        translation_key="grid_power",
        source="atmoce",
        value_key="grid_power_w",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HemsSensorDescription(
        key="grid_voltage_a",
        translation_key="grid_voltage_a",
        source="atmoce",
        value_key="grid_voltage_a_v",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    HemsSensorDescription(
        key="grid_voltage_b",
        translation_key="grid_voltage_b",
        source="atmoce",
        value_key="grid_voltage_b_v",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    HemsSensorDescription(
        key="grid_voltage_c",
        translation_key="grid_voltage_c",
        source="atmoce",
        value_key="grid_voltage_c_v",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    HemsSensorDescription(
        key="grid_current_a",
        translation_key="grid_current_a",
        source="atmoce",
        value_key="grid_current_a_a",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    HemsSensorDescription(
        key="grid_current_b",
        translation_key="grid_current_b",
        source="atmoce",
        value_key="grid_current_b_a",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    HemsSensorDescription(
        key="grid_current_c",
        translation_key="grid_current_c",
        source="atmoce",
        value_key="grid_current_c_a",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    HemsSensorDescription(
        key="pv_energy_total",
        translation_key="pv_energy_total",
        source="atmoce",
        value_key="pv_energy_total_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    HemsSensorDescription(
        key="grid_import_energy_total",
        translation_key="grid_import_energy_total",
        source="atmoce",
        value_key="grid_import_energy_total_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    HemsSensorDescription(
        key="grid_export_energy_total",
        translation_key="grid_export_energy_total",
        source="atmoce",
        value_key="grid_export_energy_total_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
)

INDEVOLT_SENSORS: tuple[HemsSensorDescription, ...] = (
    HemsSensorDescription(
        key="battery_soc",
        translation_key="battery_soc",
        source="indevolt",
        value_key="battery_soc",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HemsSensorDescription(
        key="battery_power",
        translation_key="battery_power",
        source="indevolt",
        value_key="battery_power_w",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HemsSensorDescription(
        key="ac_input_power",
        translation_key="ac_input_power",
        source="indevolt",
        value_key="ac_input_power_w",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HemsSensorDescription(
        key="ac_output_power",
        translation_key="ac_output_power",
        source="indevolt",
        value_key="ac_output_power_w",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HemsSensorDescription(
        key="rated_capacity",
        translation_key="rated_capacity",
        source="indevolt",
        value_key="rated_capacity_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HemsSensorDescription(
        key="grid_voltage",
        translation_key="grid_voltage",
        source="indevolt",
        value_key="grid_voltage_v",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    HemsSensorDescription(
        key="grid_frequency",
        translation_key="grid_frequency",
        source="indevolt",
        value_key="grid_frequency_hz",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    HemsSensorDescription(
        key="meter_power",
        translation_key="meter_power",
        source="indevolt",
        value_key="meter_power_w",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    HemsSensorDescription(
        key="bypass_power",
        translation_key="bypass_power",
        source="indevolt",
        value_key="bypass_power_w",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    HemsSensorDescription(
        key="ac_input_energy",
        translation_key="ac_input_energy",
        source="indevolt",
        value_key="ac_input_energy_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    HemsSensorDescription(
        key="ac_output_energy",
        translation_key="ac_output_energy",
        source="indevolt",
        value_key="ac_output_energy_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
)

HEMS_SENSORS: tuple[HemsSensorDescription, ...] = (
    HemsSensorDescription(
        key="site_consumption",
        translation_key="site_consumption",
        source="hems",
        value_key="site_consumption_w",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HemsSensorDescription(
        key="pv_surplus",
        translation_key="pv_surplus",
        source="hems",
        value_key="pv_surplus_w",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HemsSensorDescription(
        key="self_consumption_rate",
        translation_key="self_consumption_rate",
        source="hems",
        value_key="self_consumption_rate",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HemsSensorDescription(
        key="panel_count",
        translation_key="panel_count",
        source="hems",
        value_key="panel_count",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    HemsSensorDescription(
        key="microinverter_count",
        translation_key="microinverter_count",
        source="hems",
        value_key="microinverter_count",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
)


class _BaseDescriptionSensor(SensorEntity):
    """Shared sensor behavior."""

    entity_description: HemsSensorDescription

    def __init__(
        self,
        coordinator: HemsCoordinator,
        entry_id: str,
        description: HemsSensorDescription,
    ) -> None:
        self.entity_description = description
        self.coordinator = coordinator
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_translation_key = description.translation_key
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self.entity_registry_enabled_default = description.entity_registry_enabled_default

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    def _read_value(self, data: HemsData) -> Any:
        if self.entity_description.source == "atmoce":
            if data.atmoce is None:
                return None
            return getattr(data.atmoce, self.entity_description.value_key, None)
        if self.entity_description.source == "indevolt":
            if data.indevolt is None:
                return None
            return data.indevolt.get(self.entity_description.value_key)
        return data.computed.get(self.entity_description.value_key)


class AtmoceSensor(AtmoceEntity, _BaseDescriptionSensor):
    """Atmoce gateway sensor with stable entity IDs (sensor.atmoce_gateway_*)."""

    def __init__(
        self,
        coordinator: HemsCoordinator,
        entry_id: str,
        description: HemsSensorDescription,
    ) -> None:
        AtmoceEntity.__init__(self, coordinator, entry_id)
        _BaseDescriptionSensor.__init__(self, coordinator, entry_id, description)

    @property
    def suggested_object_id(self) -> str:
        return f"atmoce_gateway_{self.entity_description.key}"

    @property
    def native_value(self) -> Any:
        return self._read_value(self.coordinator.data)


class IndevoltSensor(IndevoltEntity, _BaseDescriptionSensor):
    """Indevolt storage sensor with stable entity IDs (sensor.indevolt_storage_*)."""

    def __init__(
        self,
        coordinator: HemsCoordinator,
        entry_id: str,
        description: HemsSensorDescription,
    ) -> None:
        IndevoltEntity.__init__(self, coordinator, entry_id)
        _BaseDescriptionSensor.__init__(self, coordinator, entry_id, description)

    @property
    def suggested_object_id(self) -> str:
        return f"indevolt_storage_{self.entity_description.key}"

    @property
    def native_value(self) -> Any:
        return self._read_value(self.coordinator.data)


class HemsComputedSensor(HemsEntity, _BaseDescriptionSensor):
    def __init__(
        self,
        coordinator: HemsCoordinator,
        entry_id: str,
        description: HemsSensorDescription,
    ) -> None:
        HemsEntity.__init__(self, coordinator, entry_id)
        _BaseDescriptionSensor.__init__(self, coordinator, entry_id, description)

    @property
    def native_value(self) -> Any:
        return self._read_value(self.coordinator.data)


class PackSocSensor(IndevoltEntity, SensorEntity):
    """Per-pack SOC for SFA battery modules."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HemsCoordinator, entry_id: str, pack_index: int) -> None:
        super().__init__(coordinator, entry_id)
        self._pack_index = pack_index
        self._attr_unique_id = f"{entry_id}_pack_{pack_index}_soc"
        self._attr_translation_key = "pack_soc"
        self._attr_translation_placeholders = {"pack": str(pack_index)}
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self.entity_registry_enabled_default = pack_index == 1

    @property
    def suggested_object_id(self) -> str:
        return f"indevolt_storage_pack_{self._pack_index}_soc"

    @property
    def native_value(self) -> Any:
        if self.coordinator.data.indevolt is None:
            return None
        return self.coordinator.data.indevolt.get(f"pack_{self._pack_index}_soc")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HemsCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities: list[SensorEntity] = []

    if coordinator.atmoce is not None:
        entities.extend(
            AtmoceSensor(coordinator, entry.entry_id, description)
            for description in ATMOCE_SENSORS
        )

    if coordinator.indevolt is not None:
        entities.extend(
            IndevoltSensor(coordinator, entry.entry_id, description)
            for description in INDEVOLT_SENSORS
        )
        entities.extend(
            PackSocSensor(coordinator, entry.entry_id, pack_index)
            for pack_index in INDEVOLT_POINT_PACK_SOC
        )

    if coordinator.atmoce is not None and coordinator.indevolt is not None:
        entities.extend(
            HemsComputedSensor(coordinator, entry.entry_id, description)
            for description in HEMS_SENSORS
        )

    async_add_entities(entities)
    await async_add_atmozen_entities(hass, entry.entry_id, async_add_entities)
