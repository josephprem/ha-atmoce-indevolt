# Energy dashboard mapping

After installing the integration, open **Settings → Dashboards → Energy** and configure:

## Production

- **Solar panels**: entity `sensor.<entry>_pv_power` from the Atmoce device

## Grid

- **Grid consumption**: `sensor.<entry>_grid_power`
- Positive values typically mean import; confirm against your Atmozen app and invert in Energy settings if needed.

## Battery

- **Battery SOC**: `sensor.<entry>_battery_soc`
- Optional statistics: `sensor.<entry>_ac_input_energy`, `sensor.<entry>_ac_output_energy`

## Home consumption (optional)

When both devices are connected, use:

- `sensor.<entry>_site_consumption` for estimated whole-home load
- `sensor.<entry>_pv_surplus` to drive automations

## SFA3600 packs

Monitor individual modules:

- `sensor.<entry>_pack_1_soc` (primary SFA3600)
- `sensor.<entry>_pack_2_soc` … up to pack 5 if expanded

Disable unused pack entities in **Settings → Devices & Services → Entities** to reduce clutter.
