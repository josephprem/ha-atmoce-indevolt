# Energy dashboard mapping

Configure under **Settings → Dashboards → Energy**.

Official troubleshooting if a sensor is missing from the picker:  
[Home Assistant Energy FAQ — Troubleshooting missing entities](https://www.home-assistant.io/docs/energy/faq/#troubleshooting-missing-entities)

## Entity names (not `pv_power` alone)

Home Assistant entity IDs look like:

```text
sensor.atmoce_gateway_pv_power
```

The suffix is `pv_power`; the full ID includes the device slug (`atmoce_gateway`).  
In **Settings → Devices & services → Entities**, search **PV power** on the **Atmoce Gateway** device.

| Energy dashboard field | Entity | Required attributes |
|------------------------|--------|---------------------|
| Solar → **Power** | `sensor.atmoce_gateway_pv_power` | `device_class: power`, `state_class: measurement`, unit `W` |
| Solar → **Energy** (optional) | `sensor.atmoce_gateway_pv_energy_total` | `device_class: energy`, `state_class: total_increasing`, unit `kWh` |
| Grid → **Power** | `sensor.atmoce_gateway_grid_power` | `device_class: power`, `state_class: measurement`, unit `W` |
| Grid → **Import energy** | `sensor.atmoce_gateway_grid_import_energy_total` | `device_class: energy`, `state_class: total_increasing` |
| Grid → **Export energy** | `sensor.atmoce_gateway_grid_export_energy_total` | `device_class: energy`, `state_class: total_increasing` |

## Checklist (from HA docs)

Work through these if the sensor is not in the Energy picker:

### 1. Entity exists

**Settings → Devices & services → Integrations → Atmoce + Indevolt HEMS**

| Situation | Action |
|-----------|--------|
| Integration missing | Install `custom_components/ha_atmoce_indevolt`, restart HA, add integration |
| Integration shows **Failed setup** | Open logs (`ha_atmoce_indevolt`), fix MC100 IP / Modbus, reload integration |
| Device exists but no PV sensor | Reload integration or restart HA after updating integration code |

### 2. Correct domain

Must be `sensor.*`. `input_number` or other domains cannot be used directly.

### 3. Correct attributes

**Settings → Developer tools → States** → select `sensor.atmoce_gateway_pv_power` → **Attributes**:

```yaml
device_class: power
state_class: measurement
unit_of_measurement: W
```

If attributes are wrong, update the integration from this repository and restart HA.

### 4. Entity is available

`unavailable` sensors are often hidden from the Energy picker.

- Confirm MC100 IP (`192.168.1.8`) and Modbus TCP enabled in Atmozen
- **Reload** the integration after fixing network issues
- State should show a number (e.g. `1450`), not `unavailable`

### 5. No statistics errors

**Settings → Developer tools → Statistics** → find the entity.

Fix any unit or state-class issues listed there before adding to Energy.

## Grid sign convention

Positive `grid_power` usually means **import**; negative means **export**. Compare with the Atmozen app. Use **Invert** in the Energy UI if the direction is reversed.

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

## SFA3600 packs

`sensor.indevolt_storage_pack_1_soc` … `pack_5_soc` (disable unused packs in Entities).
