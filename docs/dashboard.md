# Atmozen-style dashboard — setup guide

A mobile-friendly Home Assistant dashboard: dark theme, energy flow, live kW chips, and a 24h chart.

[![Data flow](diagrams/data-flow.png)](diagrams/data-flow.svg)

## What you are installing

Three separate pieces work together:

| Piece | File in this repo | What it does |
|-------|-------------------|--------------|
| **Template sensors** | `packages/atmozen_dashboard.yaml` | Computes home power, kW chips, daily totals |
| **Dashboard layout** | `dashboards/atmozen.yaml` | The actual Lovelace UI (cards, tabs) |
| **Theme** | `themes/atmozen.yaml` | Dark/light colours |

The **integration** (`ha_atmoce_indevolt`) must already be installed and showing Atmoce sensors before the dashboard will work.

---

## Step 0 — Integration working first

1. Install **Atmoce + Indevolt HEMS** (HACS or manual copy of `custom_components/ha_atmoce_indevolt`).
2. Add the integration: **Settings → Devices & services → Add integration**.
3. Enter Atmoce IP `192.168.1.8` (Indevolt can stay empty for now).
4. Confirm you see a **PV power** sensor under **Developer tools → States**.

Expected entity ID: `sensor.atmoce_gateway_pv_power` (friendly name **PV power** — not the literal string `pv_power`).

If you set up before the gateway rename, yours may be `sensor.atmoce_mc100_combiner_pv_power`.

For the **Energy dashboard** picker requirements, see [`energy-dashboard.md`](energy-dashboard.md).

If no Atmoce sensors exist at all, fix the integration before continuing (see [Troubleshooting missing sensors](#troubleshooting-missing-sensors) below).

---

## Step 1 — HACS frontend cards

The dashboard uses custom cards. Install from **HACS → Frontend** (search each name):

| Card | Required? |
|------|-----------|
| [power-flow-card-plus](https://github.com/flixlix/power-flow-card-plus) | Yes (centre flow graphic) |
| [Mushroom](https://github.com/piitaya/lovelace-mushroom) | Yes (kW chips) |
| [apexcharts-card](https://github.com/RomRider/apexcharts-card) | Yes (24h chart) |
| [card-mod](https://github.com/thomasloven/lovelace-card-mod) | Optional (rounded corners) |

After installing, **restart Home Assistant** once.

---

## Step 2 — Copy 3 files into `/config`

Your Home Assistant config folder is usually `/config` (HA OS, Supervised, Container).

Copy from this git repo:

```text
ha-atmoce-indevolt/packages/atmozen_dashboard.yaml  →  /config/packages/atmozen_dashboard.yaml
ha-atmoce-indevolt/dashboards/atmozen.yaml          →  /config/dashboards/atmozen.yaml
ha-atmoce-indevolt/themes/atmozen.yaml              →  /config/themes/atmozen.yaml
```

**How to copy** (pick one):

- **Samba / Studio Code Server** — drag files in the file browser
- **File Editor** add-on — create folders `packages`, `dashboards`, `themes` if missing, paste file contents
- **SSH** — `scp` the three files to the paths above

Create any folder that does not exist yet (`packages`, `dashboards`, `themes`).

---

## Step 3 — Edit `configuration.yaml`

Open `/config/configuration.yaml`. **Add** these blocks (merge with what you already have — do not delete existing config).

```yaml
homeassistant:
  packages:
    atmozen_dashboard: !include packages/atmozen_dashboard.yaml

frontend:
  themes: !include_dir_merge_named themes

lovelace:
  dashboards:
    atmozen:
      mode: yaml
      title: Atmozen
      icon: mdi:solar-power-variant
      show_in_sidebar: true
      filename: dashboards/atmozen.yaml
```

**If you already use `packages:`** — only add the `atmozen_dashboard:` line under it.

**If you already use `lovelace: dashboards:`** — only add the `atmozen:` block under `dashboards:`.

**If you already use `frontend: themes:`** — keep one `themes:` line; `!include_dir_merge_named themes` loads all YAML files in `/config/themes/`.

---

## Step 4 — Check config and restart

1. **Developer tools → YAML → Check configuration** — must show *Configuration valid!*
2. **Restart Home Assistant** (Settings → System → Restart).

After restart:

1. **Settings → Devices & services → Entities** — search `atmozen` — you should see `sensor.atmozen_home_power`, etc.
2. Sidebar — new item **Atmozen** (solar icon).

---

## Step 5 — Apply the theme (optional)

**Profile** (bottom-left avatar) → **Theme** → choose **atmozen**.

The dashboard view already sets `theme: atmozen`; this step sets it globally if you want.

---

## Entity IDs

Default Atmoce device slug: **`atmoce_gateway`**

| Dashboard uses | Entity |
|----------------|--------|
| Solar | `sensor.atmoce_gateway_pv_power` |
| Grid | `sensor.atmoce_gateway_grid_power` |
| Home (computed) | `sensor.atmozen_home_power` |
| Battery (later) | `sensor.indevolt_storage_battery_power` |

If your names differ (e.g. `sensor.atmoce_mc100_pv_power`), update entity IDs in:

- `packages/atmozen_dashboard.yaml`
- `dashboards/atmozen.yaml`

Then reload templates or restart HA.

---

## Atmoce-only vs full HEMS

| Setup | What you see |
|-------|----------------|
| **Atmoce only** (now) | Solar → home ↔ grid. Battery card hidden. |
| **+ Indevolt later** | Uncomment battery lines in `dashboards/atmozen.yaml` |

---

## Troubleshooting missing sensors

Work through this list if you do not see `sensor.atmoce_gateway_pv_power` (or any Atmoce sensor).

### A. Is the integration installed?

1. **Settings → Devices & services → Integrations**
2. Search for **Atmoce + Indevolt HEMS**

| What you see | What to do |
|--------------|------------|
| Not listed | Install via HACS or copy `custom_components/ha_atmoce_indevolt` into `/config/custom_components/`, then **restart HA** |
| Listed | Open it → confirm **Atmoce Gateway** device exists |

### B. Find your real entity names

**Developer tools → States**, filter by:

- `atmoce`
- `pv_power`
- `hems`

Common PV sensor entity IDs:

| Situation | Example entity |
|-----------|----------------|
| Default (device name *Atmoce Gateway*) | `sensor.atmoce_gateway_pv_power` |
| Older install (*Atmoce MC100 Combiner*) | `sensor.atmoce_mc100_combiner_pv_power` |

Copy the exact ID you see into `packages/atmozen_dashboard.yaml` and `dashboards/atmozen.yaml`.

You can also rename entities in **Settings → Devices & services → Entities** (pencil icon) without editing YAML.

### C. Sensors exist but show `unavailable`

| Check | Action |
|-------|--------|
| MC100 IP | Integration config must be `192.168.1.8` (or your combiner IP) |
| Modbus enabled | Atmozen app → enable Modbus TCP on the MC100 |
| Same network | HA and MC100 on the same LAN |
| Port | Default `502` |
| Logs | **Settings → System → Logs**, filter `ha_atmoce_indevolt` for connection errors |

### D. Reload after fixing

**Settings → Devices & services → Atmoce + Indevolt HEMS → Reload**, or restart HA.

---

## Other dashboard issues

| Problem | Fix |
|---------|-----|
| No **Atmozen** in sidebar | Check `lovelace:` block in `configuration.yaml`, restart HA |
| *Configuration invalid* | YAML indentation — `atmozen:` must be under `dashboards:` |
| *Entity not found* on cards | Fix entity IDs (Step 5 / section B above) |
| *Custom element doesn't exist* | Install missing HACS card, restart HA |
| Flow card empty / unknown | Integration not polling — PV sensor must show a number in States |
| Template sensors missing | Confirm `packages/atmozen_dashboard` is in `configuration.yaml` |

---

## No HACS / minimal setup

Without custom cards you cannot use this YAML dashboard as-is. Alternatives:

- Use **Settings → Dashboards → Energy** for history (map Atmoce sensors there).
- Install only `packages/atmozen_dashboard.yaml` and build your own dashboard in the UI using `sensor.atmozen_*` entities.

---

## Customisation

- **Site text** — markdown card at bottom of `dashboards/atmozen.yaml`
- **Colours** — `themes/atmozen.yaml`
