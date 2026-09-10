# Atmozen-style dashboard

A mobile-friendly Home Assistant dashboard inspired by the **Atmozen** app: dark theme, central energy flow, live kW chips, and daily production stats.

## 1. HACS cards (recommended)

Install these from **HACS → Frontend**:

| Card | Repository |
|------|----------------|
| [power-flow-card-plus](https://github.com/flixlix/power-flow-card-plus) | Energy flow (solar / home / grid / battery) |
| [Mushroom](https://github.com/piitaya/lovelace-mushroom) | Stat chips |
| [apexcharts-card](https://github.com/RomRider/apexcharts-card) | 24h power chart |
| [card-mod](https://github.com/thomasloven/lovelace-card-mod) | Rounded cards / dark styling (optional) |

Restart Home Assistant after installing.

## 2. Copy files into Home Assistant

From this repository into your HA `/config` folder:

```text
config/
├── packages/atmozen_dashboard.yaml    ← from packages/
├── dashboards/atmozen.yaml            ← from dashboards/
└── themes/atmozen.yaml                ← from themes/
```

## 3. Enable package, theme, and dashboard

`configuration.yaml`:

```yaml
homeassistant:
  packages:
    atmozen_dashboard: !include packages/atmozen_dashboard.yaml

frontend:
  themes: !include_dir_merge_named themes

lovelace:
  dashboards:
    atmozen:
      mode: yaml
      title: Atmozen
      icon: mdi:solar-power-variant
      show_in_sidebar: true
      filename: dashboards/atmozen.yaml
```

Reload **Template entities** (or restart HA), then open **Atmozen** in the sidebar.

## 4. Entity IDs

The dashboard assumes the default integration device slug **`atmoce_gateway`**:

| Dashboard use | Entity |
|---------------|--------|
| Solar power | `sensor.atmoce_gateway_pv_power` |
| Grid power | `sensor.atmoce_gateway_grid_power` |
| Home (computed) | `sensor.atmozen_home_power` |
| Battery (later) | `sensor.indevolt_storage_battery_power` |

If your entities differ, check **Developer Tools → States** and update:

- `packages/atmozen_dashboard.yaml`
- `dashboards/atmozen.yaml`

## 5. Atmoce-only vs full HEMS

| Setup | What you see |
|-------|----------------|
| **Atmoce only** (your case now) | Flow: solar → home ↔ grid. Battery node idle/hidden. |
| **+ Indevolt later** | Battery SOC/power and controls appear on **Details** tab. |

## 6. Built-in fallback (no HACS)

If you prefer zero custom cards, use the Energy dashboard for history and keep only `packages/atmozen_dashboard.yaml` for template sensors. The YAML flow card requires **power-flow-card-plus**.

## 7. Customisation

- **Light mode:** Profile → Theme → `atmozen` (supports light/dark).
- **Panel count:** edit the markdown card in `dashboards/atmozen.yaml`.
- **Colours:** edit `themes/atmozen.yaml` (solar amber `#f59e0b`, home green `#22c55e`).
