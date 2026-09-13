# Diagram sources

| PNG (README preview) | SVG | PlantUML source | Description |
|----------------------|-----|-----------------|-------------|
| [system-overview.png](system-overview.png) | [system-overview.svg](system-overview.svg) | [system-overview.puml](system-overview.puml) | Physical layout + data paths |
| [data-flow.png](data-flow.png) | [data-flow.svg](data-flow.svg) | [data-flow.puml](data-flow.puml) | Paths into Home Assistant |
| [dual-metering.png](dual-metering.png) | [dual-metering.svg](dual-metering.svg) | [dual-metering.puml](dual-metering.puml) | Grid (SMD1) + Solar (Shelly) |

Shared styling: [`_theme.puml`](_theme.puml)

## Render

```bash
./render.sh
```

Uses Podman/Docker `plantuml/plantuml` or a local `plantuml` binary. The script inlines `_theme.puml` (required for `-pipe` mode).

## Colours

| Colour | Role |
|--------|------|
| Amber | Atmoce / PV |
| Blue | Home Energy Hub |
| Purple | SMD1 / grid meter |
| Green | Shelly emulator / Home Assistant |
| Dashed lines | Data / control (not AC power) |
