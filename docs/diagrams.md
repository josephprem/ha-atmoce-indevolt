# Diagrams

Mermaid diagrams for this setup. GitHub renders these inline in markdown — no PNG or SVG required.

---

## System overview

Physical layout, data paths, and Indevolt app sources.

```mermaid
flowchart TB
    subgraph pv["Solar"]
        PANELS["18x 500 W panels\n9x microinverters · 9 kWp"]
        MC100["Atmoce MC100\nModbus TCP :502"]
        PANELS -->|AC| MC100
    end

    subgraph hub["Home Energy Hub"]
        SF3000["SF3000AC + SFA3600\nnative battery source"]
    end

    GRID["Utility grid"]
    LOAD["Home load"]

    MC100 -->|AC| SF3000
    SF3000 <-->|AC| GRID
    SF3000 -->|AC| LOAD

    subgraph meters["Indevolt app meters"]
        SMD1["Solarman SMD1\nsmart meter · LoRa"]
        SHELLY["Simulated Shelly 3EM\nHA emulator · HTTP :80"]
    end

    SMD1 -.->|grid source| SF3000
    SHELLY -.->|solar / PV source| SF3000
    SMD1 -.->|measures| LOAD

    subgraph ha["Home Assistant"]
        HA["HA OS VM\nFreebox Ultra"]
    end

    MC100 -.->|Modbus| HA
    SF3000 -.->|OpenData :8080| HA
    HA -.->|pv_power| SHELLY

    classDef ac stroke:#f59e0b,stroke-width:2px
    classDef hub stroke:#38bdf8,stroke-width:2px
    classDef meter stroke:#a78bfa,stroke-width:2px
    classDef solar stroke:#4ade80,stroke-width:2px
    classDef ha stroke:#22c55e,stroke-width:2px

    class PANELS,MC100 ac
    class SF3000 hub
    class SMD1 meter
    class SHELLY solar
    class HA ha
```

**Legend:** solid arrows = AC power · dotted arrows = data / control

**App sources:** Hub (battery) · SMD1 (grid) · Shelly emulator (PV)

---

## Data paths to Home Assistant

```mermaid
flowchart LR
    MC100["Atmoce MC100\nModbus :502"]
    SF3000["Home Energy Hub\nOpenData :8080"]
    EMU["Shelly emulator\nreads HA sensors"]
    HA["Home Assistant\nVM on Freebox Ultra"]
    EDASH["Energy dashboard"]
    IAPP["Indevolt app\nGrid + Solar sources"]
    ATMOZEN["Atmozen app"]

    MC100 -->|Modbus integration| HA
    SF3000 -->|Indevolt integration| HA
    HA -->|hosts add-on| EMU
    HA --> EDASH
    EMU -.->|HTTP :80| IAPP
    MC100 -.-> Atmozen

    classDef src stroke:#f59e0b,stroke-width:2px
    classDef hub stroke:#38bdf8,stroke-width:2px
    classDef ha stroke:#22c55e,stroke-width:2px
    classDef out stroke:#94a3b8,stroke-width:1px

    class MC100 src
    class SF3000 hub
    class HA,EMU ha
    class EDASH,IAPP,ATMOZEN out
```

Shelly emulator bridges Atmoce PV into Indevolt — the SF3000 does not read Atmoce Modbus directly.

---

## Indevolt dual metering

Third-party PV (Atmoce) with separate grid and solar meters. Based on [Indevolt dual metering](https://docs.indevolt.com/docs/hardware/advanced/third-party-inverter-dual-metering).

```mermaid
flowchart LR
    PV["Atmoce PV\nMC100 · 9 kWp"]
    SHELLY["Simulated Shelly 3EM\nSolar / PV source"]
    LOAD["Home load"]
    SMD1["Solarman SMD1\nGrid smart meter"]
    GRID["Utility grid"]
    HUB["Home Energy Hub\nSF3000 + SFA3600\nBattery source"]

    PV -->|AC| LOAD
    PV -.->|pv_power via HA| SHELLY
    SHELLY -.->|solar data| HUB
    LOAD --> SMD1
    SMD1 <-->|net| GRID
    SMD1 -.->|grid data| HUB

    classDef pv stroke:#f59e0b,stroke-width:2px
    classDef solar stroke:#4ade80,stroke-width:2px
    classDef grid stroke:#a78bfa,stroke-width:2px
    classDef hub stroke:#38bdf8,stroke-width:2px

    class PV pv
    class SHELLY solar
    class SMD1 grid
    class HUB hub
```

Without a PV meter, the grid meter alone only sees net import/export — not total solar generation.
