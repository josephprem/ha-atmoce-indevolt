# Atmozen-style dashboard

A mobile-friendly Home Assistant dashboard: dark theme, energy flow, live kW chips, and a 24h chart.

[![Data flow](diagrams/data-flow.png)](diagrams/data-flow.svg)

## Automatic install (v0.2.0+)

When you add **Atmoce + Indevolt HEMS**, the integration automatically:

| Installed for you | Details |
|-------------------|---------|
| **Atmozen dashboard** | Sidebar entry **Atmozen** at `/ha-atmoce-indevolt` |
| **atmozen theme** | Dark/light theme used by the dashboard |
| **Helper sensors** | `sensor.atmozen_home_power`, `sensor.atmozen_pv_daily`, etc. |

No manual copy of `packages/`, `dashboards/`, or `themes/` into `/config` is required.

After adding the integration:

1. **Restart Home Assistant** once (after updating to v0.2.0).
2. Open **Atmozen** in the sidebar.

The dashboard is created in **storage mode** (editable in the HA UI).

---

## HACS frontend cards (still required)

The dashboard uses custom cards. Install from **HACS → Frontend**, then restart HA:

| Card | Required? |
|------|-----------|
| [power-flow-card-plus](https://github.com/flixlix/power-flow-card-plus) | Yes |
| [Mushroom](https://github.com/piitaya/lovelace-mushroom) | Yes |
| [apexcharts-card](https://github.com/RomRider/apexcharts-card) | Yes |
| [card-mod](https://github.com/thomasloven/lovelace-card-mod) | Optional |

Without these, the dashboard appears but cards show *Custom element doesn't exist*.

---

## Manual YAML install (optional / legacy)

The repo still contains `packages/atmozen_dashboard.yaml`, `dashboards/atmozen.yaml`, and `themes/atmozen.yaml` for advanced users who prefer YAML-mode Lovelace. **Do not use both** automatic and manual installs — you would get duplicate sensors.

---

## Entity IDs

| Dashboard uses | Entity |
|----------------|--------|
| Solar | `sensor.atmoce_gateway_pv_power` |
| Grid | `sensor.atmoce_gateway_grid_power` |
| Home (computed) | `sensor.atmozen_home_power` |
| Battery (later) | `sensor.indevolt_storage_battery_power` |

See [`energy-dashboard.md`](energy-dashboard.md) if sensors are missing.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No **Atmozen** in sidebar | Update integration to v0.2.0+, restart HA, reload integration |
| *Custom element doesn't exist* | Install HACS cards above, restart HA |
| Empty / unavailable cards | Fix Atmoce Modbus — see integration logs |
| Duplicate `atmozen_*` sensors | Remove manual `packages/atmozen_dashboard.yaml` from `configuration.yaml` |

---

## Customisation

Edit the dashboard in **Settings → Dashboards → Atmozen** (UI editor).

Bundled source (reference): `custom_components/ha_atmoce_indevolt/dashboard/atmozen.yaml`
