# Home Assistant Energy dashboard

Configure under **Settings → Dashboards → Energy**.

Official FAQ: [Troubleshooting missing entities](https://www.home-assistant.io/docs/energy/faq/#troubleshooting-missing-entities)

## Power vs energy

| Energy UI field | Sensor type | Example |
|-----------------|-------------|---------|
| Solar production (energy) | `device_class: energy`, kWh, `total_increasing` | Atmoce PV energy total |
| Solar production (power) | `device_class: power`, W, `measurement` | Atmoce PV power |
| Grid import (energy) | energy, kWh | Grid import energy total |
| Grid export (energy) | energy, kWh | Grid export energy total |
| Grid import (power) | power, W, ≥ 0 | Grid import power |
| Grid export (power) | power, W, ≥ 0 | Grid export power |

Signed net grid power (+ import / − export) is often **excluded** from the Energy power picker. Use separate import/export power sensors if your Atmoce integration provides them.

## Atmoce mapping

Entity IDs depend on your community integration. Search **Developer tools → States** for PV and grid entities.

Typical mapping:

1. **Electricity grid → Add grid connection**
   - Energy imported → `*_grid_import_energy_total` or equivalent
   - Energy returned → `*_grid_export_energy_total`
   - Power consumption → `*_grid_import_power`
   - Power export → `*_grid_export_power`
2. **Solar panels → Add solar production**
   - Energy → `*_pv_energy_total`
   - Power → `*_pv_power`

## Indevolt battery (optional)

If the core Indevolt integration exposes compatible energy sensors:

- **Home battery storage** → battery SOC and power entities from SF3000 device.

## Energy Distribution shows 0 Wh

The card needs **live power (W)** sensors, not only kWh totals.

| Symptom | Fix |
|---------|-----|
| All 0 Wh | Add power sensors in Energy config |
| 0 at night | Normal if PV and grid ≈ 0 W |
| Totals stay 0 | Wait 1–2 h for statistics; check kWh entities in States |

On **HA 2026.9+**, verify during daylight in **Developer tools → States**:

- PV power > 0 W when producing
- Grid import/export power respond to load

## Checklist

1. Entity exists and is not `unavailable`
2. Energy sensors: `device_class: energy`, `state_class: total_increasing`, unit kWh
3. Power sensors: `device_class: power`, `state_class: measurement`, unit W
4. Statistics: **Developer tools → Statistics** — no gaps for new entities

## Indevolt app vs HA Energy

| System | Purpose |
|--------|---------|
| **HA Energy** | Atmoce Modbus data (PV, grid) |
| **Indevolt app** | Hub (battery) + SMD1 (grid) + Shelly emulator (PV) for optimisation |

They use different data paths — see [data-flow diagram](diagrams/data-flow.svg).
