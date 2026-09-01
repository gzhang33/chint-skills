# Universal Electrical Parameter & Rating Taxonomy (Global Industry Standard)

Aligned with ABB Formula AIR / Emax2, Schneider Masterpact / EasyPact MVS, and LS ELECTRIC Susol international catalogs.

## 1. Voltage, Current & Breaking Capacity Ratings

| Parameter Symbol | Chinese Term | Standard Global English Term | IEC Standard Basis | Typical Units / Values |
| :--- | :--- | :--- | :--- | :--- |
| **$U_i$** | 额定绝缘电压 | **Rated insulation voltage** | IEC 60947-1 Cl. 4.3.1.2 | $250\text{ V}, 500\text{ V}, 690\text{ V}, 1000\text{ V}$ |
| **$U_{imp}$** | 额定冲击耐受电压 | **Rated impulse withstand voltage** | IEC 60947-1 Cl. 4.3.1.3 | $2.5\text{ kV}, 4\text{ kV}, 6\text{ kV}, 8\text{ kV}, 12\text{ kV}$ |
| **$U_e$** | 额定工作电压 | **Rated operational voltage** | IEC 60947-1 Cl. 4.3.1.1 | $\text{AC } 230/400/415/690\text{ V}, \text{DC } 250/500/1000\text{ V}$ |
| **$I_{th}$** | 约定自由空气发热电流 | **Conventional free air thermal current** | IEC 60947-1 Cl. 4.3.2.1 | $10\text{ A} \sim 125\text{ A}$ |
| **$I_n$** | 额定电流 (额定持续电流) | **Rated current / Rated continuous current** | IEC 60947-2 Cl. 4.3.2.3 | $0.5\text{ A} \sim 6300\text{ A}$ |
| **$I_{nm}$** | 壳架等级额定电流 | **Frame rating / Frame size** | IEC 60947-2 Cl. 4.3.2.4 | $63\text{ AF} \sim 6300\text{ AF}$ |
| **$I_{cu}$** | 额定极限短路分断能力 | **Rated ultimate short-circuit breaking capacity** | IEC 60947-2 Cl. 4.3.5.2.1 | $6\text{ kA} \sim 150\text{ kA}$ |
| **$I_{cs}$** | 额定运行短路分断能力 | **Rated service short-circuit breaking capacity** | IEC 60947-2 Cl. 4.3.5.2.2 | $100\% I_{cu}$ or $75\% I_{cu}$ |
| **$I_{cw}$** | 额定短时耐受电流 | **Rated short-time withstand current** | IEC 60947-2 Cl. 4.3.5.4 | $15\text{ kA} \sim 120\text{ kA} (1\text{ s} / 3\text{ s})$ |
| **$I_{cm}$** | 额定短路接通能力 | **Rated short-circuit making capacity** | IEC 60947-2 Cl. 4.3.5.3 | Peak value ($n \times I_{cu}$) |
| **$I_{cn}$** | 额定短路能力 (家用微断) | **Rated short-circuit capacity** | IEC 60898-1 | $4.5\text{ kA}, 6\text{ kA}, 10\text{ kA}$ |

---

## 2. Endurance, Power Loss & Selectivity

| Item | Chinese Term | Standard Global English Term | Standard Description / Unit |
| :--- | :--- | :--- | :--- |
| **Mechanical Endurance** | 机械寿命 | **Mechanical endurance (operations / cycles)** | Total operating cycles with maintenance ($10,000 \sim 500,000$). |
| **Electrical Endurance** | 电寿命 | **Electrical endurance (operations under load)** | Operating cycles at rated operational current $I_e$ ($1,000 \sim 50,000$). |
| **Power Dissipation** | 功率损耗 / 功耗 | **Power loss / Power dissipation (W / pole)** | Thermal heat dissipation per pole at rated current. |
| **Arcing Distance** | 飞弧距离 (零飞弧) | **Arcing distance / Zero arcing distance** | Safety clearance required above arc chutes ($0 \text{ mm}$). |
| **Utilization Category** | 使用类别 (A类/B类) | **Utilization category (Category A / Category B)** | Cat A: non-selective instantaneous; Cat B: selective with $I_{cw}$. |

---

## 3. Environmental & Protection Ratings

| Item | Chinese Term | Standard Global English Term | Standards & Range |
| :--- | :--- | :--- | :--- |
| **Degree of Protection** | 防护等级 | **Degree of protection (IP rating)** | $\text{IP20}, \text{IP30}, \text{IP40}, \text{IP54}, \text{IP68}$ (IEC 60529) |
| **Pollution Degree** | 污染等级 | **Pollution degree: 3** | IEC 60947-1 / IEC 60664-1 |
| **Ambient Temperature** | 运行环境温度 | **Ambient operating temperature range** | $-5^\circ\text{C} \sim +40^\circ\text{C}$ (Standard), $-45^\circ\text{C} \sim +70^\circ\text{C}$ (Extended) |
| **Altitude Derating** | 高原海拔及降容 | **Altitude & altitude derating factors** | $\le 2000\text{ m}$ (No derating), $>2000\text{ m} \sim 5000\text{ m}$ (Derated) |
| **Tropicalization** | 湿热性能 / 热带化 | **Tropicalization / Damp heat capability** | IEC 60068-2-30 (Treatment TH II) |
| **EMC Compliance** | 电磁兼容性 | **Electromagnetic compatibility (EMC)** | IEC 60947-2 Annex F / Annex J |
