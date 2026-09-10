# Solarman SMD1 smart meter (LoRa)

Your full stack:

| Device | Role in HEMS |
|--------|----------------|
| **Atmoce** (18 panels + MG100) | Solar production + grid CT via Modbus |
| **Indevolt SF3000AC** | AC battery inverter, local OpenData API |
| **Indevolt SFA3600** | Battery pack(s) |
| **Solarman SMD1** | Whole-home consumption meter (LoRa → SF3000) |

Product page: [Solarman LoRa SMD1 on Indevolt France](https://fr.indevolt.com/products/solarman-lora-compteur-electrique-intelligent-smd1)

## How it fits together

The SMD1 is **not a standalone HA device**. Per Indevolt:

- Compatible only with the **Indevolt ecosystem**
- **LoRa** pairing is for the **SolidFlex / SF3000** range (your SF3000AC)
- Also supports Wi‑Fi and Bluetooth for commissioning
- Measures **real household load** so the SF3000 can do zero-export / self-consumption

```text
Atmoce PV ──► grid / home
                 ▲
SMD1 (clamp) ──► SF3000AC ──► SFA3600
       LoRa          │
                     └── OpenData HTTP ──► Home Assistant
```

Home Assistant reads meter data **through the SF3000AC**, not directly from the SMD1.

## Indevolt app setup

1. Install the SMD1 on the **main household feed** (monophase) per the manual.
2. In the **Indevolt app** on the SF3000AC:
   - Add meter → **Solarman SMD1**
   - Prefer **LoRa** for stable link to the SF3000 (recommended indoors)
   - Confirm **Meter connection status** shows connected
3. Set load mode to **Meter** (OpenData point `47005` / app “meter” strategy) for whole-home optimisation.
4. Enable **Local API → HTTP** on the SF3000 (unchanged).

## Home Assistant entities

Once Indevolt is configured in `ha_atmoce_indevolt`:

| Entity | Source |
|--------|--------|
| `sensor.indevolt_storage_meter_power` | SMD1 whole-home load (W) |
| `sensor.indevolt_storage_battery_soc` | Battery |
| `sensor.atmoce_gateway_pv_power` | Solar |

HEMS sensors (`site_consumption`, `pv_surplus`, `self_consumption_rate`) **prefer the SMD1 meter** when available, instead of estimating from Atmoce PV + grid.

The Atmozen dashboard package does the same for **Home power**.

## Phased rollout

| Phase | Hardware | Home power source |
|-------|----------|-------------------|
| **Now** | Atmoce only | Estimated: `PV + grid` |
| **+ SF3000 / SFA3600** | Battery control | Still estimated until SMD1 |
| **+ SMD1** | Accurate load | `meter_power` from SF3000 |

## Do not use the Solarman HA integration for SMD1

The core [**Solarman**](https://www.home-assistant.io/integrations/solarman/) integration targets other Solarman dongles/plugs (SP-2W, P1, MR1). The **SMD1 sold by Indevolt** is paired to the SF3000 and exposed via **Indevolt OpenData** only.

## Troubleshooting

| Symptom | Check |
|---------|--------|
| `meter_power` unavailable | SMD1 paired in app, LoRa linked, meter enabled |
| Home power still estimated | Indevolt host configured in HA integration |
| Values differ from Atmozen | Atmoce grid CT vs SMD1 clamp — SMD1 is authoritative for **home load** |
