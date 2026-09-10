"""Install Atmozen theme, dashboard, and helper sensors from the integration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.components.frontend import async_register_theme
from homeassistant.components.lovelace.const import (
    CONF_ICON,
    CONF_MODE,
    CONF_SHOW_IN_SIDEBAR,
    CONF_TITLE,
    CONF_URL_PATH,
    DATA_DASHBOARDS,
    DOMAIN as LOVELACE_DOMAIN,
    MODE_STORAGE,
)
from homeassistant.components.lovelace.dashboard import LovelaceStorage
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from datetime import timedelta

from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower
from homeassistant.core import CoreState, Event, HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_point_in_time, async_track_state_change_event
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util
from homeassistant.util import yaml as ha_yaml

from .const import DOMAIN, HEMS_DEVICE

_LOGGER = logging.getLogger(__name__)

DASHBOARD_URL_PATH = "ha-atmoce-indevolt"
DASHBOARD_DIR = Path(__file__).parent / "dashboard"
DATA_ATMOZEN_INSTALLED = "atmozen_installed"

SOURCE_PV_POWER = "sensor.atmoce_gateway_pv_power"
SOURCE_GRID_POWER = "sensor.atmoce_gateway_grid_power"
SOURCE_METER_POWER = "sensor.indevolt_storage_meter_power"
SOURCE_PV_ENERGY = "sensor.atmoce_gateway_pv_energy_total"
SOURCE_GRID_IMPORT_ENERGY = "sensor.atmoce_gateway_grid_import_energy_total"
SOURCE_GRID_EXPORT_ENERGY = "sensor.atmoce_gateway_grid_export_energy_total"


def _float_state(hass: HomeAssistant, entity_id: str) -> float | None:
    state = hass.states.get(entity_id)
    if state is None or state.state in ("unknown", "unavailable", "none"):
        return None
    try:
        return float(state.state)
    except (TypeError, ValueError):
        return None


async def async_setup_atmozen(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register theme and create the storage-mode Lovelace dashboard once."""

    async def _install(_event: Event | None = None) -> None:
        if hass.data.get(DOMAIN, {}).get(DATA_ATMOZEN_INSTALLED):
            return
        await _async_register_theme(hass)
        await _async_install_dashboard(hass)
        hass.data.setdefault(DOMAIN, {})[DATA_ATMOZEN_INSTALLED] = True
        _LOGGER.info("Atmozen dashboard installed at /%s", DASHBOARD_URL_PATH)

    if hass.state == CoreState.running:
        await _install()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _install)


async def _async_register_theme(hass: HomeAssistant) -> None:
    """Register the atmozen theme in frontend theme storage."""
    if DATA_THEMES not in hass.data:
        _LOGGER.debug("Frontend themes not ready; skip atmozen theme")
        return

    theme_file = DASHBOARD_DIR / "atmozen_theme.yaml"
    if not theme_file.is_file():
        return

    data = await hass.async_add_executor_job(load_yaml, str(theme_file))
    theme = data.get("atmozen") if isinstance(data, dict) else None
    if not theme:
        return

    hass.data[DATA_THEMES]["atmozen"] = theme
    hass.bus.async_fire(EVENT_THEMES_UPDATED)


async def _async_install_dashboard(hass: HomeAssistant) -> None:
    from homeassistant.components.lovelace.const import (
        CONF_ICON,
        CONF_MODE,
        CONF_SHOW_IN_SIDEBAR,
        CONF_TITLE,
        CONF_URL_PATH,
        DATA_DASHBOARDS,
        DOMAIN as LOVELACE_DOMAIN,
        MODE_STORAGE,
    )
    from homeassistant.components.lovelace.dashboard import LovelaceStorage

    if LOVELACE_DOMAIN not in hass.data:
        _LOGGER.debug("Lovelace not loaded; skip dashboard install")
        return

    dashboards = hass.data[LOVELACE_DOMAIN][DATA_DASHBOARDS]
    dashboard_file = DASHBOARD_DIR / "atmozen.yaml"
    if not dashboard_file.is_file():
        return

    config = await hass.async_add_executor_job(load_yaml, str(dashboard_file))
    if not isinstance(config, dict):
        _LOGGER.warning("Invalid Atmozen dashboard YAML")
        return

    dashboard_id: str | None = None
    for item in dashboards.async_items():
        if item.get(CONF_URL_PATH) == DASHBOARD_URL_PATH:
            dashboard_id = item["id"]
            break

    if dashboard_id is None:
        created = await dashboards.async_create_item(
            {
                CONF_TITLE: "Atmozen",
                CONF_ICON: "mdi:solar-power-variant",
                CONF_URL_PATH: DASHBOARD_URL_PATH,
                CONF_SHOW_IN_SIDEBAR: True,
                "require_admin": False,
                CONF_MODE: MODE_STORAGE,
            }
        )
        dashboard_id = created["id"]

    storage = LovelaceStorage(
        hass, {CONF_URL_PATH: DASHBOARD_URL_PATH, "id": dashboard_id}
    )
    await storage.async_load()
    await storage.async_save(config)


class _AtmozenBase(SensorEntity):
    _attr_has_entity_name = False

    def __init__(self, entry_id: str, object_id: str, name: str) -> None:
        self._entry_id = entry_id
        self._object_id = object_id
        self._attr_unique_id = f"{entry_id}_{object_id}"
        self._attr_name = name

    @property
    def suggested_object_id(self) -> str:
        return self._object_id

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id, HEMS_DEVICE)},
            name="Home Energy Management",
            manufacturer="ha-atmoce-indevolt",
            model="Atmozen Dashboard",
        )


class AtmozenHomePowerSensor(_AtmozenBase):
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:home-lightning-bolt"

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        super().__init__(entry_id, "atmozen_home_power", "Atmozen Home Power")
        self._hass = hass
        self._unsub: Any = None

    async def async_added_to_hass(self) -> None:
        entities = (SOURCE_METER_POWER, SOURCE_PV_POWER, SOURCE_GRID_POWER)
        self._unsub = async_track_state_change_event(
            self._hass, entities, self._async_handle_update
        )
        self._async_update()

    @callback
    def _async_handle_update(self, _event: Event) -> None:
        self._async_update()
        self.async_write_ha_state()

    @callback
    def _async_update(self) -> None:
        meter = _float_state(self._hass, SOURCE_METER_POWER)
        if meter is not None:
            self._attr_native_value = max(meter, 0.0)
            return
        pv = _float_state(self._hass, SOURCE_PV_POWER) or 0.0
        grid = _float_state(self._hass, SOURCE_GRID_POWER) or 0.0
        self._attr_native_value = max(pv + grid, 0.0)

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None


class AtmozenDerivedPowerSensor(_AtmozenBase):
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        unique_id: str,
        name: str,
        source: str,
        icon: str,
    ) -> None:
        super().__init__(entry_id, unique_id, name)
        self._hass = hass
        self._source = source
        self._attr_icon = icon
        self._unsub: Any = None

    async def async_added_to_hass(self) -> None:
        self._unsub = async_track_state_change_event(
            self._hass, [self._source], self._async_handle_update
        )
        self._async_update()

    @callback
    def _async_handle_update(self, _event: Event) -> None:
        self._async_update()
        self.async_write_ha_state()

    @callback
    def _async_update(self) -> None:
        value = _float_state(self._hass, self._source)
        self._attr_native_value = round((value or 0.0) / 1000, 2)

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None


class AtmozenHomePowerKwSensor(_AtmozenBase):
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:home-lightning-bolt"

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        super().__init__(entry_id, "atmozen_home_power_kw", "Atmozen Home Power kW")
        self._hass = hass
        self._unsub: Any = None

    async def async_added_to_hass(self) -> None:
        self._unsub = async_track_state_change_event(
            self._hass, ["sensor.atmozen_home_power"], self._async_handle_update
        )
        self._async_update()

    @callback
    def _async_handle_update(self, _event: Event) -> None:
        value = _float_state(self._hass, "sensor.atmozen_home_power")
        self._attr_native_value = round((value or 0.0) / 1000, 2)
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None


class AtmozenSelfConsumptionSensor(_AtmozenBase):
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:percent"

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        super().__init__(entry_id, "atmozen_self_consumption_pct", "Atmozen Self Consumption")
        self._hass = hass
        self._unsub: Any = None

    async def async_added_to_hass(self) -> None:
        self._unsub = async_track_state_change_event(
            self._hass, [SOURCE_PV_POWER, SOURCE_GRID_POWER], self._async_handle_update
        )
        self._async_update()

    @callback
    def _async_handle_update(self, _event: Event) -> None:
        pv = _float_state(self._hass, SOURCE_PV_POWER) or 0.0
        grid = _float_state(self._hass, SOURCE_GRID_POWER) or 0.0
        if pv > 0:
            self._attr_native_value = round(max((pv - max(grid, 0.0)) / pv * 100.0, 0.0), 0)
        else:
            self._attr_native_value = 0.0
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None


class AtmozenGridStatusSensor(_AtmozenBase):
    _attr_icon = "mdi:transmission-tower"

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        super().__init__(entry_id, "atmozen_grid_status", "Atmozen Grid Status")
        self._hass = hass
        self._unsub: Any = None

    async def async_added_to_hass(self) -> None:
        self._unsub = async_track_state_change_event(
            self._hass, [SOURCE_GRID_POWER], self._async_handle_update
        )
        self._async_update()

    @callback
    def _async_handle_update(self, _event: Event) -> None:
        grid = _float_state(self._hass, SOURCE_GRID_POWER) or 0.0
        if grid > 20:
            self._attr_native_value = "Importing"
        elif grid < -20:
            self._attr_native_value = "Exporting"
        else:
            self._attr_native_value = "Balanced"
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None


class AtmozenSiteStatusSensor(_AtmozenBase):
    _attr_icon = "mdi:solar-power-variant"

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        super().__init__(entry_id, "atmozen_site_status", "Atmozen Site Status")
        self._hass = hass
        self._unsub: Any = None

    async def async_added_to_hass(self) -> None:
        self._unsub = async_track_state_change_event(
            self._hass, [SOURCE_PV_POWER], self._async_handle_update
        )
        self._async_update()

    @callback
    def _async_handle_update(self, _event: Event) -> None:
        pv = _float_state(self._hass, SOURCE_PV_POWER) or 0.0
        if pv > 100:
            self._attr_native_value = "Producing"
        elif pv > 0:
            self._attr_native_value = "Low production"
        else:
            self._attr_native_value = "Idle"
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None


class AtmozenDailyEnergySensor(_AtmozenBase, RestoreEntity):
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        unique_id: str,
        name: str,
        source: str,
    ) -> None:
        super().__init__(entry_id, unique_id, name)
        self._hass = hass
        self._source = source
        self._baseline: float | None = None
        self._unsub_state: Any = None
        self._unsub_midnight: Any = None

    async def async_added_to_hass(self) -> None:
        restored = await self.async_get_last_state()
        if restored and restored.state not in ("unknown", "unavailable"):
            try:
                self._attr_native_value = float(restored.state)
            except (TypeError, ValueError):
                self._attr_native_value = 0.0
        else:
            self._attr_native_value = 0.0

        self._baseline = await self._read_source_total()
        self._unsub_state = async_track_state_change_event(
            self._hass, [self._source], self._async_handle_source
        )
        self._schedule_midnight_reset()

    async def _read_source_total(self) -> float | None:
        return _float_state(self._hass, self._source)

    @callback
    def _async_handle_source(self, _event: Event) -> None:
        total = _float_state(self._hass, self._source)
        if total is None:
            return
        if self._baseline is None:
            self._baseline = total
        self._attr_native_value = max(total - self._baseline, 0.0)
        self.async_write_ha_state()

    @callback
    def _schedule_midnight_reset(self) -> None:
        next_midnight = dt_util.start_of_local_day() + timedelta(days=1)
        self._unsub_midnight = async_track_point_in_time(
            self._hass, self._async_midnight_reset, next_midnight
        )

    @callback
    def _async_midnight_reset(self, _now: Any) -> None:
        self._baseline = _float_state(self._hass, self._source)
        self._attr_native_value = 0.0
        self.async_write_ha_state()
        self._schedule_midnight_reset()

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub_state:
            self._unsub_state()
            self._unsub_state = None
        if self._unsub_midnight:
            self._unsub_midnight()
            self._unsub_midnight = None


async def async_add_atmozen_entities(
    hass: HomeAssistant,
    entry_id: str,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Atmozen helper sensors (replaces packages/atmozen_dashboard.yaml)."""
    entities: list[SensorEntity] = [
        AtmozenHomePowerSensor(hass, entry_id),
        AtmozenDerivedPowerSensor(
            hass, entry_id, "atmozen_pv_power_kw", "Atmozen PV Power kW", SOURCE_PV_POWER, "mdi:solar-power"
        ),
        AtmozenDerivedPowerSensor(
            hass,
            entry_id,
            "atmozen_grid_power_kw",
            "Atmozen Grid Power kW",
            SOURCE_GRID_POWER,
            "mdi:transmission-tower",
        ),
        AtmozenHomePowerKwSensor(hass, entry_id),
        AtmozenSelfConsumptionSensor(hass, entry_id),
        AtmozenGridStatusSensor(hass, entry_id),
        AtmozenSiteStatusSensor(hass, entry_id),
        AtmozenDailyEnergySensor(hass, entry_id, "atmozen_pv_daily", "Atmozen PV today", SOURCE_PV_ENERGY),
        AtmozenDailyEnergySensor(
            hass,
            entry_id,
            "atmozen_grid_import_daily",
            "Atmozen grid import today",
            SOURCE_GRID_IMPORT_ENERGY,
        ),
        AtmozenDailyEnergySensor(
            hass,
            entry_id,
            "atmozen_grid_export_daily",
            "Atmozen grid export today",
            SOURCE_GRID_EXPORT_ENERGY,
        ),
    ]
    async_add_entities(entities)
