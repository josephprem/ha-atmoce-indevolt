# Diagrams

SVG diagrams for the home energy setup. GitHub renders SVG inline; click to open full size.

| File | Description |
|------|-------------|
| [system-overview.svg](system-overview.svg) | Physical layout, IPs, AC power + data paths |
| [data-flow.svg](data-flow.svg) | How data reaches Home Assistant and Indevolt app |
| [dual-metering.svg](dual-metering.svg) | Grid (SMD1) + Solar (Shelly emulator) for third-party PV |

## Embed in markdown

```markdown
[![System overview](diagrams/system-overview.svg)](diagrams/system-overview.svg)
```

## Style

- Dark theme (`#0f172a` / `#111827` background)
- Amber = Atmoce / PV
- Blue = Indevolt / SF3000
- Green = Shelly emulator / HA
- Purple = SMD1 / grid meter
- Dashed lines = data / control (not AC power)
