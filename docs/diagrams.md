# Diagrams

[PlantUML](https://plantuml.com/) sources with a shared dark theme. GitHub shows **PNG** previews; click through to **SVG** for full resolution.

**Regenerate** after editing `.puml` files:

```bash
./docs/diagrams/render.sh
```

Requires [Podman](https://podman.io/) or Docker (`docker.io/plantuml/plantuml`), or a local `plantuml` install.

---

## System overview

Physical layout, data paths, and Indevolt app sources.

[![System overview](diagrams/system-overview.png)](diagrams/system-overview.svg)

Source: [`diagrams/system-overview.puml`](diagrams/system-overview.puml)

**Legend:** solid arrows = AC power · dashed arrows = data / control

**App sources:** Hub (battery) · SMD1 (grid) · Shelly emulator (PV)

---

## Data paths to Home Assistant

[![Data paths](diagrams/data-flow.png)](diagrams/data-flow.svg)

Source: [`diagrams/data-flow.puml`](diagrams/data-flow.puml)

Shelly emulator bridges Atmoce PV into Indevolt — the SF3000 does not read Atmoce Modbus directly.

---

## Indevolt dual metering

Third-party PV (Atmoce) with separate grid and solar meters. Based on [Indevolt dual metering](https://docs.indevolt.com/docs/hardware/advanced/third-party-inverter-dual-metering).

[![Dual metering](diagrams/dual-metering.png)](diagrams/dual-metering.svg)

Source: [`diagrams/dual-metering.puml`](diagrams/dual-metering.puml)

Without a PV meter, the grid meter alone only sees net import/export — not total solar generation.
