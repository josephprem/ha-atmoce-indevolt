# Home energy setup — Atmoce + Indevolt

Documentation for a hybrid home energy system (HEMS): **Atmoce** solar, **Indevolt** battery storage, **Home Assistant** monitoring, and **dual metering** in the Indevolt app.

This repository is **documentation only** — no integration code. It describes hardware roles, ports, protocols, and data flow. **No real hostnames, IP addresses, or credentials are stored here**; use your own LAN reservations and secrets locally.

[![System overview](docs/diagrams/system-overview.png)](docs/diagrams/system-overview.svg)

Solid arrows = AC power · dashed = data/control. More diagrams: [docs/diagrams.md](docs/diagrams.md).

## Hardware

| Component | Role | Network |
|-----------|------|---------|
| 18× 500 W Atmoce panels + 9× 1000 W microinverters | Solar (9 kWp) | — |
| **Atmoce MC100** combiner | PV aggregation, grid CT, Modbus API | LAN · DHCP reservation |
| **Indevolt SF3000AC** | AC-coupled inverter / storage controller | LAN · DHCP reservation |
| **Indevolt SFA3600** | LiFePO₄ battery pack | via SF3000 |
| **Solarman SMD1** (LoRa) | Whole-home **grid** meter → SF3000 | via Indevolt app |
| **Shelly Pro 3EM emulator** (HA add-on) | **PV** meter for Indevolt app | HTTP **:80** on HA host |
| **Home Assistant** | Monitoring, Energy dashboard, emulator host | **VM on Freebox Ultra** |

## Home Assistant host

Home Assistant runs as a **virtual machine on Freebox Ultra** (Freebox OS). The Shelly PV emulator add-on uses **host networking**, so `mdns_host` and the IP entered in the Indevolt app must be the **VM’s LAN address** assigned by the Freebox router — not a placeholder from this repo.

## Diagrams

Diagrams are [PlantUML](docs/diagrams.md) — PNG previews in README, SVG for zoom, `.puml` sources in git.

| Diagram | Description |
|---------|-------------|
| [System overview](docs/diagrams.md#system-overview) | Full physical + data layout |
| [Data paths to HA](docs/diagrams.md#data-paths-to-home-assistant) | Modbus, OpenData, emulator |
| [Dual metering](docs/diagrams.md#indevolt-dual-metering) | Grid (SMD1) + Solar (Shelly emulator) |

## Documentation

| Guide | Contents |
|-------|----------|
| [Diagrams](docs/diagrams.md) | PlantUML system overview, data flow, dual metering |
| [Setup guide](docs/setup.md) | DHCP reservations, first-time checklist |
| [Atmoce Modbus](docs/atmoce-modbus.md) | Connect clients to MC100 on port 502 |
| [Indevolt SF3000](docs/indevolt-sf3000.md) | Local API, app, battery |
| [PV meter emulator](docs/pv-meter-emulator.md) | Shelly 3EM simulator → Indevolt Solar data source |
| [SMD1 grid meter](docs/smd1-meter.md) | LoRa clamp meter → Indevolt Grid data source |
| [Home Assistant](docs/home-assistant.md) | VM on Freebox Ultra, integrations |
| [Energy dashboard](docs/energy-dashboard.md) | HA Energy UI entity mapping |

## Indevolt app — data sources

In **Profile → Data Source**, this setup uses three distinct inputs:

| App source | Device / role | What it measures |
|------------|---------------|------------------|
| **Home Energy Hub** (native) | SF3000AC + SFA3600 | Battery SOC, charge/discharge — built into the hub |
| **Smart meter** (grid) | Solarman **SMD1** (LoRa) | Whole-home load at the main feed |
| **Simulated Shelly meter** (solar) | **Shelly 3EM emulator** on HA VM | Atmoce PV power (from `pv_power` via emulator) |

The SMD1 and Shelly emulator are added as sub-devices on the hub, then assigned under **Data Source → Grid** and **Data Source → Solar** respectively.

## Quick reference

```text
Atmoce MC100        Modbus TCP  <mc100-host>:502     unit ID 1
Home Energy Hub     native      SF3000AC + SFA3600   battery (app)
SMD1 smart meter    LoRa        via SF3000           grid (app)
Shelly emulator     HTTP        <ha-host>:80         PV / solar (app)
Home Assistant      VM          Freebox Ultra        UI :8123, hosts emulator
```

Replace `<mc100-host>` and `<ha-host>` with addresses from your Freebox device list.

## External references

- [Indevolt OpenData API](https://github.com/INDEVOLT/indevolt-doc/blob/main/docs/hardware/geek/open-data.md)
- [Indevolt dual metering (third-party PV)](https://docs.indevolt.com/docs/hardware/advanced/third-party-inverter-dual-metering)
- [Home Assistant Indevolt integration](https://www.home-assistant.io/integrations/indevolt/)
- [Shelly Pro 3EM emulator](https://github.com/bvweerd/shelly_em3pro_emulator)
- [evcc Atmoce Modbus template](https://github.com/evcc-io/evcc/blob/master/templates/definition/meter/atmoce.yaml)

## License

MIT
