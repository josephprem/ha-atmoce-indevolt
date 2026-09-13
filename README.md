# Home energy setup — Atmoce + Indevolt

Documentation for my hybrid home energy system (HEMS): **Atmoce** solar, **Indevolt** battery storage, **Home Assistant** monitoring, and **dual metering** in the Indevolt app.

This repository is **documentation only** — no custom integration code. It records how the hardware is wired, which IPs and ports to use, and how data flows between devices.

[![System overview](docs/diagrams/system-overview.svg)](docs/diagrams/system-overview.svg)

## Hardware

| Component | Role | LAN address (example) |
|-----------|------|------------------------|
| 18× 500 W Atmoce panels + 9× 1000 W microinverters | Solar (9 kWp) | — |
| **Atmoce MC100** combiner | PV aggregation, grid CT, Modbus API | `192.168.1.8` |
| **Indevolt SF3000AC** | AC-coupled inverter / storage controller | DHCP reservation |
| **Indevolt SFA3600** | LiFePO₄ battery pack | via SF3000 |
| **Solarman SMD1** (LoRa) | Whole-home **grid** meter → SF3000 | via Indevolt app |
| **Shelly Pro 3EM emulator** (HA add-on) | **PV** meter for Indevolt app | `192.168.1.75` HTTP **:80** |
| **Home Assistant** | Monitoring, Energy dashboard, emulator host | `192.168.1.75` |

## Diagrams

| Diagram | Description |
|---------|-------------|
| [System overview](docs/diagrams/system-overview.svg) | Full physical + data layout |
| [Data paths to HA](docs/diagrams/data-flow.svg) | Modbus, OpenData, emulator |
| [Dual metering](docs/diagrams/dual-metering.svg) | Grid (SMD1) + Solar (Shelly emulator) |

## Documentation

| Guide | Contents |
|-------|----------|
| [Setup guide](docs/setup.md) | Static IPs, first-time checklist |
| [Atmoce Modbus](docs/atmoce-modbus.md) | Connect clients to MC100 on port 502 |
| [Indevolt SF3000](docs/indevolt-sf3000.md) | Local API, app, battery |
| [PV meter emulator](docs/pv-meter-emulator.md) | Shelly 3EM simulator → Indevolt Solar data source |
| [SMD1 grid meter](docs/smd1-meter.md) | LoRa clamp meter → Indevolt Grid data source |
| [Home Assistant](docs/home-assistant.md) | Official Indevolt + community Atmoce integrations |
| [Energy dashboard](docs/energy-dashboard.md) | HA Energy UI entity mapping |

## Quick reference

```text
Atmoce MC100     Modbus TCP  192.168.1.8:502   unit ID 1
Indevolt SF3000  HTTP        :8080             OpenData API
Shelly emulator  HTTP        :80               Indevolt app (not :8812)
Indevolt app     Data Source Grid  → SMD1
                 Data Source Solar → Shelly emulator (Atmoce pv_power)
```

## External references

- [Indevolt OpenData API](https://github.com/INDEVOLT/indevolt-doc/blob/main/docs/hardware/geek/open-data.md)
- [Indevolt dual metering (third-party PV)](https://docs.indevolt.com/docs/hardware/advanced/third-party-inverter-dual-metering)
- [Home Assistant Indevolt integration](https://www.home-assistant.io/integrations/indevolt/)
- [Shelly Pro 3EM emulator](https://github.com/bvweerd/shelly_em3pro_emulator)
- [evcc Atmoce Modbus template](https://github.com/evcc-io/evcc/blob/master/templates/definition/meter/atmoce.yaml)

## License

MIT
