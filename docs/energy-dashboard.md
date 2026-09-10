# Energy dashboard mapping

Configure under **Settings → Dashboards → Energy**.

Official troubleshooting if a sensor is missing from the picker:  
[Home Assistant Energy FAQ — Troubleshooting missing entities](https://www.home-assistant.io/docs/energy/faq/#troubleshooting-missing-entities)

## Important: power vs energy

The Energy dashboard uses **different entity types** for different fields:

| Field in Energy UI | Type needed | Example entity |
|--------------------|-------------|----------------|
| Solar production (energy) | `device_class: energy`, `kWh`, `total_increasing` | `sensor.atmoce_gateway_pv_energy_total` |
| Solar production (power, optional) | `device_class: power`, `W`, `measurement` | `sensor.atmoce_gateway_pv_power` |
| Grid **imported** (energy) | `device_class: energy`, `kWh`, `total_increasing` | `sensor.atmoce_gateway_grid_import_energy_total` |
| Grid **returned** (energy) | `device_class: energy`, `kWh`, `total_increasing` | `sensor.atmoce_gateway_grid_export_energy_total` |
| Grid **import** power (optional) | `device_class: power`, `W`, `measurement`, ≥ 0 | `sensor.atmoce_gateway_grid_import_power` |
| Grid **export** power (optional) | `device_class: power`, `W`, `measurement`, ≥ 0 | `sensor.atmoce_gateway_grid_export_power` |

`sensor.atmoce_gateway_grid_power` is the **signed net meter** (+ import, − export). It appears in entity search but is often **not listed** in the Energy grid power picker because it goes negative. Use the import/export power sensors above instead.

## Quick setup (Atmoce only)

1. **Settings → Dashboards → Energy → Electricity grid → Add grid connection**
2. **Energy imported from grid** → `sensor.atmoce_gateway_grid_import_energy_total`
3. **Energy returned to grid** → `sensor.atmoce_gateway_grid_export_energy_total`
4. **Power measurement** (required for Energy Distribution live flow on HA 2026.x):
   - Consumption / import: `sensor.atmoce_gateway_grid_import_power`
   - Return / export: `sensor.atmoce_gateway_grid_export_power`
5. **Solar panels → Add solar production**
   - Energy: `sensor.atmoce_gateway_pv_energy_total`
   - Power: `sensor.atmoce_gateway_pv_power`

## Energy Distribution shows 0 Wh / 0 kWh

Your screenshot (Summary → Energy distribution) means the **card is working**, but Home Assistant has **no live power** and/or **no energy statistics** to plot yet.

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Solar / Grid / Home all **0 Wh** | Power sensors not set in Energy config | Add power sensors in steps 4–5 above (kWh alone is not enough) |
| All **0 Wh** at night | Normal if PV and grid are ~0 W | Check again during daylight |
| **Totals 0 kWh** | Statistics not built yet, or period is empty | Wait 1–2 h after setup; open **Developer tools → Statistics** |
| Totals stay 0 in daylight | kWh sensors read 0 from MC100 | Check `sensor.atmoce_gateway_pv_energy_total` in States |

On **HA Core 2026.9.x** the animated flow uses **power (W)** entities. The **Totals** table uses **energy (kWh)** statistics from the same Energy configuration.

Verify in **Developer tools → States** during the day:

| Entity | Should show |
|--------|-------------|
| `sensor.atmoce_gateway_pv_power` | > 0 W when producing |
| `sensor.atmoce_gateway_grid_import_power` | > 0 W when importing |
| `sensor.atmoce_gateway_home_power` | estimated home load (PV + grid) |

Tabs on HA 2026.9: **Summary** (distribution + totals), **Electricity** (charts), **Now** (live power).

## Entity names (not `pv_power` alone)

Home Assistant entity IDs look like:

```text
sensor.atmoce_gateway_pv_power
```

Search **PV power** on the **Atmoce Gateway** device under **Settings → Devices & services → Entities**.

## Checklist (from HA docs)

Work through these if a sensor is not in the Energy picker:

### 1. Entity exists and is available

**Settings → Developer tools → States** — state must be a number, not `unavailable`.

### 2. Correct attributes

For **energy** sensors (import/export/PV totals):

```yaml
device_class: energy
state_class: total_increasing
unit_of_measurement: kWh
```

For **power** sensors:

```yaml
device_class: power
state_class: measurement
unit_of_measurement: W
```

### 3. Correct dropdown

Do not pick a **power** sensor (W) for an **energy** field (kWh), or vice versa.

### 4. No statistics errors

**Settings → Developer tools → Statistics** — fix any issues for the entity, then reload the integration.

### 5. Reload after update

After updating this integration to v0.2.7+, **reload** the integration so new entities and attributes are registered.

## Grid sign convention

`sensor.atmoce_gateway_grid_power`: positive = import, negative = export.  
`grid_import_power` / `grid_export_power` split this into two always-positive sensors for Energy.

## Battery (when Indevolt is added)

| Field | Entity |
|-------|--------|
| Battery SOC | `sensor.indevolt_storage_battery_soc` |
| Battery power | `sensor.indevolt_storage_battery_power` |

## Home consumption (HEMS, both devices required)

| Entity | Use |
|--------|-----|
| `sensor.home_energy_management_site_consumption` | Estimated / meter-based home load |
| `sensor.home_energy_management_pv_surplus` | Automations |

HEMS sensors appear only when **both** Atmoce and Indevolt are configured.
