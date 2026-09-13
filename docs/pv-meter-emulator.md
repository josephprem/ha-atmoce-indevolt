# PV meter — Shelly Pro 3EM emulator

When solar comes from a third-party inverter (Atmoce), the Indevolt app needs a **Solar** data source. This setup uses a **simulated Shelly Pro 3EM** on the Home Assistant VM: it repackages Atmoce `pv_power` as a fake Shelly smart meter for the app.

Battery and grid use separate native sources (Home Energy Hub + SMD1) — see [indevolt-sf3000.md](indevolt-sf3000.md).

See [dual metering diagram](diagrams.md#indevolt-dual-metering).

Source: [Indevolt dual metering for third-party inverters](https://docs.indevolt.com/docs/hardware/advanced/third-party-inverter-dual-metering)

> Use your HA VM’s LAN address (`<ha-host>`) locally. Do not publish it in this repo.

## Why not Modbus from Atmoce?

Indevolt only supports specific meter brands (Shelly, Solarman, etc.) over **local HTTP/LoRa** — not Atmoce Modbus. The bridge is:

```text
Atmoce MC100 ──Modbus──► HA VM (pv_power sensor)
                              │
                              ▼
                    Shelly emulator (HTTP :80)
                              │
                              ▼
                    Indevolt app (Solar data source)
```

## Install emulator (HA add-on)

1. **Settings → Add-ons → Add-on Store → Repositories**  
   Add: `https://github.com/bvweerd/shelly_em3pro_emulator`
2. Install **Shelly Pro 3EM Emulator**, enable **host network**.
3. Configuration:

| Option | Value |
|--------|--------|
| `http_port` | **`80`** ← required for Indevolt |
| `auto_discover` | `false` |
| `mdns_host` | `<ha-host>` (HA VM LAN address on Freebox) |
| `mdns_enabled` | `true` |
| `http_enabled` | `true` |
| `udp_enabled` | `true` |
| `device_name` | Descriptive name (e.g. `PV Meter`) |
| `single_phase_power` | Your Atmoce PV power entity |
| `energy_delivered` | Your Atmoce PV energy total entity |

Replace entity IDs with yours from **Developer tools → States** (community Atmoce integration names vary).

4. Start add-on and check logs for `HTTP server listening on ...:80`.

> **Port 80 fix:** Default add-on port `8812` causes **offline** in Indevolt. Indevolt connects to Shelly on port **80** only.

## Get Device ID

From a device on the same LAN:

```bash
curl -s http://<ha-host>/rpc/Shelly.GetDeviceInfo
```

Use the `"id"` field from the JSON response in the Indevolt app.

## Indevolt app pairing

1. **Add Device → Shelly → Pro 3EM**
2. Enter `<ha-host>` and the Device ID from curl
3. **SF3000 → + Add Sub-Device** → link meter
4. **Profile → Data Source → Solar** → select the simulated Shelly meter

## Verify

| Check | Expected |
|-------|----------|
| Phone browser `http://<ha-host>/rpc/EM.GetStatus` | JSON with power > 0 in daylight |
| Indevolt device card | Online, live watts |
| Solar data source | Shows emulator name |

## Second emulator for grid (optional)

If not using SMD1, a **second** emulator instance (unique MAC, port 80 on another host) can map `grid_power` for **Grid** data source. One add-on cannot represent two Shelly devices.

## References

- [Shelly emulator repo](https://github.com/bvweerd/shelly_em3pro_emulator)
- [Indevolt Shelly Pro 3EM guide](https://blog.indevolt.com/en/how-to-integrate-the-shelly-pro-3em-electricity-meter-into-the-indevolt-app/)
