"""Atmoce + Indevolt HEMS integration for Home Assistant."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_ATMOCE_HOST,
    CONF_ATMOCE_PANEL_COUNT,
    CONF_ATMOCE_PORT,
    CONF_INDEVOLT_HOST,
    CONF_INDEVOLT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
from .atmoce import AtmoceModbusClient
from .coordinator import HemsCoordinator
from .indevolt import IndevoltApiClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Atmoce + Indevolt HEMS from a config entry."""
    data = entry.data
    atmoce_host = (data.get(CONF_ATMOCE_HOST) or "").strip()
    indevolt_host = (data.get(CONF_INDEVOLT_HOST) or "").strip()

    atmoce_client = (
        AtmoceModbusClient(atmoce_host, data.get(CONF_ATMOCE_PORT, 502))
        if atmoce_host
        else None
    )
    indevolt_client = None
    if indevolt_host:
        session = async_get_clientsession(hass)
        indevolt_client = IndevoltApiClient(
            session,
            indevolt_host,
            data.get(CONF_INDEVOLT_PORT, 8080),
        )

    coordinator = HemsCoordinator(
        hass,
        atmoce_client,
        indevolt_client,
        data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        data.get(CONF_ATMOCE_PANEL_COUNT, 18),
    )
    await coordinator.async_config_entry_first_refresh()

    _register_services(hass)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "atmoce_host": atmoce_host,
        "indevolt_host": indevolt_host,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        domain_data = hass.data[DOMAIN].pop(entry.entry_id)
        coordinator: HemsCoordinator = domain_data["coordinator"]
        if coordinator.atmoce is not None:
            await coordinator.atmoce.close()
    return unload_ok


@callback
def _register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, "charge_battery"):
        return

    async def charge_battery(call: ServiceCall) -> None:
        await _run_battery_action(hass, call, charging=True)

    async def discharge_battery(call: ServiceCall) -> None:
        await _run_battery_action(hass, call, charging=False)

    hass.services.async_register(
        DOMAIN,
        "charge_battery",
        charge_battery,
        schema=vol.Schema(
            {
                vol.Required("power"): cv.positive_int,
                vol.Required("target_soc"): vol.All(int, vol.Range(min=5, max=100)),
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        "discharge_battery",
        discharge_battery,
        schema=vol.Schema(
            {
                vol.Required("power"): cv.positive_int,
                vol.Required("target_soc"): vol.All(int, vol.Range(min=5, max=100)),
            }
        ),
    )


async def _run_battery_action(hass: HomeAssistant, call: ServiceCall, charging: bool) -> None:
    power = call.data["power"]
    target_soc = call.data["target_soc"]
    for entry_data in hass.data.get(DOMAIN, {}).values():
        coordinator: HemsCoordinator = entry_data["coordinator"]
        if coordinator.indevolt is None:
            continue
        if charging:
            await coordinator.indevolt.async_charge(power, target_soc)
        else:
            await coordinator.indevolt.async_discharge(power, target_soc)
        await coordinator.async_request_refresh()
