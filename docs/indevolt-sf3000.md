# Indevolt SF3000AC + SFA3600

The SF3000AC is the network gateway for the battery system. The SFA3600 pack(s) connect through it — there is no separate IP for the pack.

## Local API (Home Assistant)

| Setting | Value |
|---------|--------|
| Protocol | **HTTP** (not HTTPS for local OpenData) |
| Port | `8080` (default) |
| Discovery | UDP port `8099` / `AT+IGDEVICEIP` |

### Verify API

```bash
curl -g -X POST -H "Content-Type: application/json" \
  "http://192.168.1.51:8080/rpc/Indevolt.GetData?config={\"t\":[6002,6004,47004]}"
```

| Point | Meaning |
|-------|---------|
| `6002` | Battery SOC (%) |
| `6004` | Battery power (W) |
| `47004` | Meter power from SMD1 (W), when paired |

Enable in app: **Profile → direct device connection → Local API → HTTP**.

## Indevolt app — energy modes

For whole-home optimisation with external meters:

1. **Device → SF3000 → Energy mode → Self-Consumed Prioritized**
2. Load type: **Smart Meter** (when SMD1 or Shelly grid meter is linked)
3. Recommended: feed-in limit `0` (zero export)

## Linking sub-devices

**Device → SF3000 → + Add Sub-Device** → link:

- **SMD1** — grid / home load ([smd1-meter.md](smd1-meter.md))
- **Shelly Pro 3EM** — PV or grid meter ([pv-meter-emulator.md](pv-meter-emulator.md))

## Data sources (dual metering)

**Profile → Data Source**:

| Source | Device in this setup |
|--------|----------------------|
| **Grid** | Solarman SMD1 |
| **Solar** | Shelly Pro 3EM emulator (Atmoce PV) |

See [Indevolt dual metering docs](https://docs.indevolt.com/docs/hardware/advanced/third-party-inverter-dual-metering).

## Firmware

- App **V1.1.0+** for local Shelly meters
- Update SF3000 when app prompts (Shelly 3EM support added in recent firmware)

## References

- [OpenData API](https://github.com/INDEVOLT/indevolt-doc/blob/main/docs/hardware/geek/open-data.md)
- [Link devices](https://docs.indevolt.com/docs/hardware/advanced/link-device)
- [Self-consumption mode](https://docs.indevolt.com/docs/hardware/energy-mode/self-consumption)
