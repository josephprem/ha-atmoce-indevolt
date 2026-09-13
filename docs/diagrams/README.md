# Diagrams

SVG source files plus **PNG previews** for GitHub README rendering (GitHub does not inline SVG images in markdown).

| PNG (inline preview) | SVG (zoomable source) | Description |
|----------------------|------------------------|-------------|
| [system-overview.png](system-overview.png) | [system-overview.svg](system-overview.svg) | Physical layout, AC power + data paths |
| [data-flow.png](data-flow.png) | [data-flow.svg](data-flow.svg) | Data paths to Home Assistant and Indevolt |
| [dual-metering.png](dual-metering.png) | [dual-metering.svg](dual-metering.svg) | Grid (SMD1) + Solar (Shelly emulator) |

Diagrams omit LAN addresses, hostnames, and credentials. Home Assistant is shown as a **VM on Freebox Ultra**.

## Embed in markdown

```markdown
[![System overview](diagrams/system-overview.png)](diagrams/system-overview.svg)
```

## Regenerate PNG from SVG

```bash
python3 -m venv .venv-svg && .venv-svg/bin/pip install cairosvg
.venv-svg/bin/python -c "
import cairosvg
for name, w in [('system-overview', 1100), ('data-flow', 1000), ('dual-metering', 960)]:
    cairosvg.svg2png(url=f'docs/diagrams/{name}.svg', write_to=f'docs/diagrams/{name}.png', output_width=w)
"
```

## Style

- Dark theme (`#0f172a` / `#111827` background)
- Amber = Atmoce / PV
- Blue = Indevolt / SF3000
- Green = Shelly emulator / HA
- Purple = SMD1 / grid meter
- Dashed lines = data / control (not AC power)
