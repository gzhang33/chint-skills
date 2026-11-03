# CHINT PPTX Asset Library & Map/Icon Guide (`asset_library_guide.md`)

This guide details the specialized graphic, icon, and map assets bundled in `chint-pptx`, explaining how AI agents and Product Managers should invoke and apply them across presentations.

**Scope: these assets are placed by hand, not by the engine.** The engine renders text, native tables, and native charts only; its payload has no picture, icon, or map field, and `--edit-config` rejects image objects. Read this guide to tell the user which file to insert, or to describe the layout in words — never to assume a generated deck already contains one of these graphics. The badge and the legacy frame bitmaps listed in section 3 are the two exceptions, since the engines load them directly.

---

## 1. Categorized Vector Icon Library (`assets/icons/`)

All icons are official CHINT 2026 VI aligned vector graphics (`.svg`), categorized by business domain and function:

### 1.1 Smart Electric & Power Distribution (智能电气与配电)
- `electric_grid_01.svg`: Power grid, primary distribution, substation network
- `power_meter_02.svg`: Smart metering, electricity consumption, precision measurement
- `smart_switch_03.svg`: Circuit breakers, switchgear, and remote control
- `transmission_line_13.svg`: High/low voltage transmission lines, grid interconnection
- `power_transformer_21.svg`: Power transformer, substation voltage conversion, grid dispatch
- `circuit_interconnection_22.svg`: Circuit interconnection, busbar tie, grid synchronisation
- `digital_meter_20.svg`: Digital smart meter (AMI), remote metering, load profiling

### 1.2 Green Energy & Clean Power (绿色能源与光储)
- `solar_photovoltaic_07.svg`: PV generation, solar rooftop, green electricity
- `energy_storage_04.svg`: Battery energy storage systems (BESS), PCS inverter, dual-direction power
- `efficiency_leaf_12.svg`: Carbon neutrality, ESG green certification, energy saving rate

### 1.3 Digital Platform & IoT (数智化与物联网)
- `cloud_server_05.svg`: CHINT Cloud (正泰云), PaaS platform, data center server
- `iot_gateway_06.svg`: Smart communication gateway, edge computing unit, Modbus-TCP
- `data_analytics_09.svg`: Big data analytics, AI energy efficiency algorithm, telemetry charts
- `smart_city_19.svg`: Smart building, industrial park, urban microgrid
- `security_shield_10.svg`: Electrical safety, zero-arcing fault protection, data encryption
- `intelligent_sensor_23.svg`: Intelligent sensor, condition monitoring, edge sensing

### 1.4 Business, Operations & Quality (业务、团队与交付)
- `automation_robot_11.svg`: Smart manufacturing, robotic inspection, automated assembly
- `maintenance_gear_14.svg`: Predictive maintenance, lifecycle services, 24/7 hotline
- `building_complex_15.svg`: Commercial complex, hospital/data center facilities
- `global_network_16.svg`: Country coverage, regional service, and global footprint; source every location claim
- `partnership_handshake_17.svg`: Strategic partnership, customer co-creation, channel ecosystem
- `quality_award_18.svg`: Landmark certifications (IEC, UL, KEMA, CE, GB standards)
- `industry_facility_08.svg`: Industrial facility, factory, manufacturing base

---

## 2. Geographic Map Assets (`assets/maps/`)

Vector maps for presenting market reach, service network, and global footprint:

- `china_map_provinces.svg`: High-precision China map with detailed provincial divisions and regional boundaries.
- `china_map_outline.svg`: Minimalist geographic outline of China for clean background overlays.

### Usage in Slides:
- **National Sales / Service Network**: Combine `china_map_provinces.svg` with user-provided regional, warehouse, or response-time information. Verify every count and service commitment from source material.
- **Overseas Expansion**: Use `ARCH_TABLE` with a region column for overseas manufacturing bases, regional headquarters, and localized supply chains.

---

## 3. Official 2026 VI Media Assets (`assets/media/`) — and their baked-in artwork

Frame pages (cover, contents, chapter divider, closing) are **not** pasted bitmaps. Since
2026 改版后引擎改用模板自身的版式（`标题幻灯片`、`目录`、`节标题`,
`末尾幻灯片`), so the KV photo, gradient bands, accent line, marks and copyright line stay
native, editable objects inherited from the layout. The `*_26_bg.jpg` bitmaps below are the
flat exports of that same artwork and are kept only as a legacy fallback for the shell rebuild
path (`scripts/shell_rebuild_engine.py`).

| Asset | Used by | Note |
| :--- | :--- | :--- |
| `cover_26_bg.jpg` | legacy flat cover (shell rebuild) | Already carries the CHINT lockup **and a copyright line** in the artwork |
| `toc_26_bg.jpg` | legacy flat contents | Dark left panel carries "CONTENTS" |
| `chapter_26_bg_clean.jpg` | legacy flat divider (shell rebuild) | **Use this one.** Cleaned copy of the official chapter art |
| `chapter_26_bg.jpg` | — | **Do not use — defective** (see below) |
| `closing_26_bg.jpg` | legacy flat closing (shell rebuild) | Carries THANKS, the CHNT wordmark, **and a copyright line** in the artwork |
| `chint_badge.png` | inner-page corner badge | Single-layer badge; see the layering warning below |

### 4.1 Baked-in "edit-mode" content — verified defects

Some official assets were exported straight from PowerPoint's **edit view**, so editor
chrome was burnt into the pixels. It cannot be removed by editing OpenXML — it is image
content.

| Asset | Baked-in content | Consequence if you also draw it |
| :--- | :--- | :--- |
| `chapter_26_bg.jpg` | the layout prompt text **「添加章节标题」** centred in the band, **and a CHINT badge** in the top-right corner | the chapter title collides with ghost text; a second logo appears on every divider |
| `cover_26_bg.jpg` | a light-grey `Copyright © CHINT GROUP` line at bottom-left, faint enough to miss on screen | two stacked copyright lines |
| `closing_26_bg.jpg` | the same copyright line (bottom-right) | two stacked copyright lines |

These defects are the reason the creation path stopped using the bitmaps. The template
layouts carry the same artwork with every element live, so no prompt text, no duplicate
badge, and no stacked copyright can survive — and the chapter page keeps only the accent
line that belongs to the design, with no extra rule drawn underneath the band.

**Rules**

1. The creation engine uses template layouts for every frame page. Do not reintroduce
   `add_picture(<frame bitmap>)` there; if a requested variation cannot be expressed with the
   layout artwork, report the gap.
2. Never add a copyright textbox to the cover, body or closing page — the layout already has one.
3. Before drawing any text over a legacy bitmap, check the asset for baked-in text:
   `tesseract asset.jpg - -l chi_sim+eng --psm 11`.


### 4.2 Logo layering — three places a CHINT badge can hide

A deck can inherit a badge from the **slide master**, from the **layout's group shape**,
and from a **slide-level picture**. Drawing another one produces the classic double-logo
ghost. Before adding a badge:

```bash
unzip -q deck.pptx -d /tmp/chk && grep -l "图片" /tmp/chk/ppt/slideMasters/*.xml
# and inspect layout groups: python-pptx → slide.slide_layout.shapes
```

The shared brand renderer checks slide and master content before adding the badge. Badge placement across page types — which pages carry one and which omit it — is defined in [quality_and_environment.md](quality_and_environment.md) CHINT assets; this section covers only the layering hazard.
