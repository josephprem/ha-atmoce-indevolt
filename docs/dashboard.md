# Atmozen-style dashboard

A mobile-friendly Home Assistant dashboard: dark theme, energy flow, live kW chips, and a 24h chart.

[![Data flow](diagrams/data-flow.png)](diagrams/data-flow.svg)

## Automatic install (disabled)

Automatic Atmozen dashboard install is **disabled from v0.2.7** while core entity support is stabilised. Use the manual YAML path below if you want the Lovelace dashboard later.

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
| No **Atmozen** in sidebar | Update to v0.2.3+, restart HA. Or run service **ha_atmoce_indevolt.install_dashboard** from Developer tools → Actions |
| *Custom element doesn't exist* | Install HACS cards above, restart HA |
| Empty / unavailable cards | Fix Atmoce Modbus — see integration logs |
| Duplicate `atmozen_*` sensors | Remove manual `packages/atmozen_dashboard.yaml` from `configuration.yaml` |

---

## Customisation

Edit the dashboard in **Settings → Dashboards → Atmozen** (UI editor).

Bundled source (reference): `custom_components/ha_atmoce_indevolt/dashboard/atmozen.yaml`
