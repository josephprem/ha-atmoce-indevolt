# Solarman SMD1 — grid meter (LoRa)

The SMD1 clamp meter measures **whole-home load** and pairs to the Home Energy Hub (SF3000) over **LoRa**. In the Indevolt app it is the **smart meter** assigned as the **Grid** data source.

Product: [Solarman LoRa SMD1 (Indevolt France)](https://fr.indevolt.com/products/solarman-lora-compteur-electrique-intelligent-smd1)

See [dual metering diagram](diagrams.md#indevolt-dual-metering).

## Role in this setup

| Meter | Measures | Indevolt app role |
|-------|----------|-----------------|
| **Home Energy Hub** | Battery SOC / power | Native battery source |
| **SMD1** | Home load at main feed | **Smart meter** → Grid |
| **Shelly emulator** | Atmoce PV output | **Simulated Shelly** → Solar |

```text
Atmoce PV ──► grid / home
                 ▲
SMD1 (clamp) ──► SF3000AC ──► SFA3600
       LoRa          │
                     └── OpenData HTTP ──► Home Assistant
```

The SMD1 has **no direct HA integration**. Data arrives via the SF3000 OpenData API (`meter_power` / point `47004`).

## Indevolt app setup

1. Install SMD1 on the **main household feed** (monophase) per manual.
2. **Add Device → Solarman → SMD1**
3. Pair to SF3000 — prefer **LoRa** for stable indoor link.
4. Confirm meter connection status in app.
5. **SF3000 → + Add Sub-Device** → link SMD1.
6. **Profile → Data Source → Grid** → select the SMD1 smart meter.
7. Energy mode: **Self-Consumed Prioritized** with **Smart Meter** load type.

## Home Assistant

With the [official Indevolt integration](home-assistant.md), look for a meter power entity on the SF3000 device (exact name depends on HA version).

Use it for:

- Automations based on real home load
- Template comparisons vs Atmoce-estimated load

Do **not** use the generic [Solarman](https://www.home-assistant.io/integrations/solarman/) integration for the Indevolt-bundled SMD1 — it is paired only to the SF3000.

## vs Atmoce grid CT

| Source | Measures |
|--------|----------|
| Atmoce MC100 grid CT | Net at combiner / PV side |
| SMD1 | Whole-home load at main feed |

For Indevolt zero-export control, **SMD1 is authoritative** for home load.

## Troubleshooting

| Symptom | Check |
|---------|--------|
| No meter in app | LoRa paired, SF3000 firmware updated |
| `meter_power` missing in HA | SMD1 linked, local API enabled on SF3000 |
| Indevolt ignores meter | Grid data source = SMD1 in Profile |
