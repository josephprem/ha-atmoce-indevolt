"""Config flow for Atmoce + Indevolt HEMS."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_ATMOCE_HOST,
    CONF_ATMOCE_PANEL_COUNT,
    CONF_ATMOCE_PORT,
    CONF_INDEVOLT_HOST,
    CONF_INDEVOLT_PORT,
    DEFAULT_ATMOCE_HOST,
    DEFAULT_ATMOCE_PORT,
    DEFAULT_INDEVOLT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .atmoce import AtmoceModbusClient
from .indevolt import IndevoltApiClient

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ATMOCE_HOST, default=DEFAULT_ATMOCE_HOST): str,
        vol.Optional(CONF_ATMOCE_PORT, default=DEFAULT_ATMOCE_PORT): int,
        vol.Optional(CONF_ATMOCE_PANEL_COUNT, default=18): vol.All(
            int, vol.Range(min=1, max=90)
        ),
        vol.Optional(CONF_INDEVOLT_HOST): str,
        vol.Optional(CONF_INDEVOLT_PORT, default=DEFAULT_INDEVOLT_PORT): int,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=5, max=300)
        ),
    }
)


async def _validate_atmoce(hass: HomeAssistant, host: str, port: int) -> None:
    client = AtmoceModbusClient(host, port)
    try:
        await client.async_get_snapshot()
    finally:
        await client.close()


async def _validate_indevolt(hass: HomeAssistant, host: str, port: int) -> None:
    session = async_get_clientsession(hass)
    client = IndevoltApiClient(session, host, port)
    await client.async_get_snapshot()


class HemsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Atmoce + Indevolt HEMS."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            atmoce_host = (user_input.get(CONF_ATMOCE_HOST) or "").strip()
            indevolt_host = (user_input.get(CONF_INDEVOLT_HOST) or "").strip()

            if not atmoce_host and not indevolt_host:
                errors["base"] = "device_required"
            else:
                if atmoce_host:
                    try:
                        await _validate_atmoce(
                            self.hass,
                            atmoce_host,
                            user_input[CONF_ATMOCE_PORT],
                        )
                    except Exception:  # noqa: BLE001 - show user-friendly validation error
                        errors[CONF_ATMOCE_HOST] = "cannot_connect"

                if indevolt_host and CONF_ATMOCE_HOST not in errors:
                    try:
                        await _validate_indevolt(
                            self.hass,
                            indevolt_host,
                            user_input[CONF_INDEVOLT_PORT],
                        )
                    except Exception:  # noqa: BLE001 - show user-friendly validation error
                        errors[CONF_INDEVOLT_HOST] = "cannot_connect"

            if not errors:
                title = "Atmoce + Indevolt HEMS"
                if atmoce_host and indevolt_host:
                    title = f"HEMS ({atmoce_host} + {indevolt_host})"
                elif atmoce_host:
                    title = f"Atmoce PV ({atmoce_host})"
                else:
                    title = f"Indevolt ({indevolt_host})"

                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return await self.async_step_user(user_input)
