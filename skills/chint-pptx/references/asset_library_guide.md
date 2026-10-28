# CHINT PPTX Asset Library & Map/Icon Guide (`asset_library_guide.md`)

This guide details the specialized graphic, icon, and map assets bundled in `chint-pptx`, explaining how AI agents and Product Managers should invoke and apply them across presentations.

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
- **Overseas Expansion**: Use `ARCH_13_GLOBAL_FOOTPRINT` to highlight overseas manufacturing bases, regional headquarters (APAC, EMEA, Americas), and localized supply chains.

---

## 3. Specialized Layout Archetypes (`ARCH_12` & `ARCH_13`)

### `ARCH_12_TEAM_PROFILE` — Leadership & Technical Experts
- **When to use**: Presenting R&D core teams, senior technical architects, PM leadership, or project delivery squads.
- **Structure**: 3 or 4 equal-width cards with avatar container, name, official title, academic/industry credentials, and key achievements.

### `ARCH_13_GLOBAL_FOOTPRINT` — Global / National Footprint
- **When to use**: Presenting business network coverage, global sales branches, or regional manufacturing bases.
- **Structure**: Split layout with left network statistics + right branch distribution matrix / regional office cards.

---

## 4. Official 2026 VI Media Assets (`assets/media/`) — and their baked-in artwork

| Asset | Used by | Note |
| :--- | :--- | :--- |
| `cover_26_bg.jpg` | `ARCH_01_COVER` / Mode B cover | Already carries the CHINT lockup **and a copyright line** in the artwork |
| `toc_26_bg.jpg` | `ARCH_02_TOC` / Mode B contents | Dark left panel carries "CONTENTS" |
| `chapter_26_bg_clean.jpg` | `ARCH_03_CHAPTER` / Mode B dividers | **Use this one.** Cleaned copy of the official chapter art |
| `chapter_26_bg.jpg` | — | **Do not use — defective** (see below) |
| `closing_26_bg.jpg` | `ARCH_11_CLOSING` / Mode B closing | Carries THANKS, the CHNT wordmark, **and a copyright line** in the artwork |
| `chint_badge.png` | inner-page corner badge | Single-layer badge; see the layering warning below |

### 4.1 Baked-in "edit-mode" content — verified defects

Some official assets were exported straight from PowerPoint's **edit view**, so editor
chrome was burnt into the pixels. It cannot be removed by editing OpenXML — it is image
content.

| Asset | Baked-in content | Consequence if you also draw it |
| :--- | :--- | :--- |
| `chapter_26_bg.jpg` | the layout prompt text **「添加章节标题」** (x≈803–1198, y≈470–532) **and a CHINT badge** (x≈1711–1914, y≈0–152) | the chapter title collides with ghost text; a second logo appears on every divider |
| `cover_26_bg.jpg` | a light-grey `Copyright © CHINT GROUP 2025-2026` (bottom-left, y≈1025–1100, min luminance ≈182 — easy to miss) | two stacked copyright lines |
| `closing_26_bg.jpg` | the same copyright line (bottom-right) | two stacked copyright lines |

**Rules**

1. Mode B divides only use **`chapter_26_bg_clean.jpg`** (same art, prompt text inpainted by
   column-wise vertical interpolation, badge area painted white). The raw file is retained
   for provenance only.
2. Never add a copyright textbox to the cover or closing page — the artwork already has one.
3. Before drawing any text over an official background, check the asset for baked-in text:
   `tesseract asset.jpg - -l chi_sim+eng --psm 11`.

### 4.2 Logo layering — three places a CHINT badge can hide

A deck can inherit a badge from the **slide master**, from the **layout's group shape**,
and from a **slide-level picture**. Drawing another one produces the classic double-logo
ghost. Before adding a badge:

```bash
unzip -q deck.pptx -d /tmp/chk && grep -l "图片" /tmp/chk/ppt/slideMasters/*.xml
# and inspect layout groups: python-pptx → slide.slide_layout.shapes
```

The shared brand renderer checks slide and master content before adding the badge. Contents,
chapter, and body pages receive one visible upper-right badge. It leaves the cover and closing
artwork's official logo positions intact, and brings an existing matching slide-level badge
above a background image rather than adding a duplicate.
