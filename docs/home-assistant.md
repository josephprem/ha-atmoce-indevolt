# Home Assistant

Home Assistant runs as a **virtual machine on Freebox Ultra**. It collects data from Atmoce and Indevolt, hosts the Shelly PV emulator add-on, and drives the Energy dashboard.

[![Data paths](diagrams/data-flow.png)](diagrams/data-flow.svg)

## Freebox Ultra VM

| Item | Notes |
|------|--------|
| Hypervisor | Freebox Ultra (Freebox OS) |
| Guest | Home Assistant OS VM |
| UI | `http://<ha-host>:8123` (use your VM’s LAN address) |
| Shelly emulator | HA add-on with **host network** — advertises on `<ha-host>` |

Give the VM a **DHCP reservation** on the Freebox so the address stays stable for Modbus clients, the Indevolt app, and mDNS.

Do not commit `<ha-host>`, API tokens, or Wi‑Fi passwords to this repository.

## Integrations to use

| Device | Integration | Type |
|--------|-------------|------|
| Indevolt SF3000AC | [Indevolt](https://www.home-assistant.io/integrations/indevolt/) | **Core** (built-in) |
| Atmoce MC100 | Community Modbus integration | HACS / manual |
| Shelly emulator | [Shelly Pro 3EM Emulator](https://github.com/bvweerd/shelly_em3pro_emulator) add-on | Add-on |

## Indevolt (core)

1. **Settings → Devices & Services → Add Integration → Indevolt**
2. Enter the SF3000 LAN hostname or address; enable local HTTP API on the device first.
3. Entities include battery SOC, power, AC flow, and `meter_power` when SMD1 is paired.

## Atmoce (community)

| Project | Notes |
|---------|-------|
| [pacorola/Atmoce_battery_HA](https://github.com/pacorola/Atmoce_battery_HA) | Modbus sensors |
| [gfro84/Atmoce_modbus_HA](https://github.com/gfro84/Atmoce_modbus_HA) | Modbus + docs in wiki |
| [evcc](https://docs.evcc.io/en/meters/atmoce-mg100-m-gateway) | If using evcc alongside HA |

Requirements: Modbus TCP enabled on MC100 — see [atmoce-modbus.md](atmoce-modbus.md).

Entity IDs depend on the integration you install. Find them under **Settings → Devices & services → Entities**.

## Shelly emulator add-on

Feeds Atmoce PV into the Indevolt app — see [pv-meter-emulator.md](pv-meter-emulator.md).

The emulator reads HA entity states via the Supervisor API (`homeassistant_api: true`). Set `mdns_host` to the **HA VM’s LAN address**. Map `single_phase_power` to your Atmoce PV power entity.

## Template sensors (optional)

Estimate home load before SMD1 is installed:

```yaml
template:
  - sensor:
      - name: Estimated home power
        unit_of_measurement: W
        device_class: power
        state_class: measurement
        state: >
          {{ (states('sensor.<your_atmoce_pv_power>') | float(0)
              + states('sensor.<your_atmoce_grid_power>') | float(0)) | round(0) }}
```

Replace placeholders with your entity IDs. After SMD1 pairing, prefer Indevolt `meter_power` instead.

## Energy dashboard

See [energy-dashboard.md](energy-dashboard.md) for entity mapping and troubleshooting zero Wh on the distribution card.

## HA version notes

Tested on **Home Assistant Core 2026.9.x**. Energy Distribution requires **power (W)** sensors in addition to **energy (kWh)** totals.
