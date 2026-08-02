# 🏛️ Geological Rescan & Analysis Report: UNESCO Stone Sites (v2)

This report details the results of the geological rescan performed on the **254 sites** originally flagged as containing stone/rock mentions in `stone_sites-Table 1.csv`.

Using the upgraded **`classify_monuments_v2.py`** pipeline, we evaluated these sites to calculate refined confidence scores, extract construction terms and architectural elements, and compile statistical frequencies.

---

## 📊 Summary of Findings

Of the 254 stone-bearing sites:
* **228 sites (89.8%)** are verified as built monuments featuring structural stonework or rock-cut architecture.
* **26 sites (10.2%)** are categorized as LOW confidence or NONE (typically represent natural landscapes with minor stone names, geological descriptions, or fossil layers).

### Confidence Distribution

| Confidence Tier | Description | Site Count | Percentage |
| :--- | :--- | :---: | :---: |
| 🟢 **HIGH** | Explicit rock type matches directly in title/description with high architectural indicators. | **182** | 71.7% |
| 🟡 **MEDIUM** | Moderate structural indicators, specific masonry terms, or singular rock matches. | **46** | 18.1% |
| 🔴 **LOW** | Weak structural cues or general stone words in description. | **17** | 6.7% |
| ⚫ **NONE** | No geological materials or structural stonework matched (e.g., natural landscapes). | **9** | 3.5% |

---

## 🧱 Site-Term Relations & Extraction Statistics

We flattened (exploded) the semicolon-separated list of matches from the 254 sites to compile exact frequencies:

### 1. Construction & Masonry Terms
* **Total Occurrences (Exploded Rows)**: **273 rows**
* **Unique Terms Found**: 36 unique terms
* **Top Matched Terms**:
  1. `capital` (65 occurrences) — signature column capitals.
  2. `quarry` (27 occurrences) — indicating direct mentions of local stone sourcing.
  3. `masonry` (25 occurrences) — general stone construction.
  4. `megalithic` (9 occurrences) — ancient large-stone masonry.
  5. `rubble` (8 occurrences) — uncoursed stone filling.

### 2. Architectural Elements
* **Total Occurrences (Exploded Rows)**: **1,380 rows**
* **Unique Elements Found**: 80 unique elements
* **Top Matched Elements**:
  1. `wall` (116 occurrences) — masonry walls.
  2. `base` (97 occurrences) — structural column bases/pedestals.
  3. `capital` (65 occurrences) — column crowns.
  4. `church` (64 occurrences) — ecclesiastical masonry complexes.
  5. `tower` (54 occurrences) — towers and civic belfries.
  6. `palace` (53 occurrences) — royal/civic stone palaces.
  7. `temple` (53 occurrences) — stone temples and shrines.
  8. `foundation` (43 occurrences) — substructure masonry.

---

## 💡 Key Comparative Insights: Stone Sites vs. No-Stone Sites

### 1. The "Lithological Baseline"
* **No-Stone Sites**: Represent the **geological nomenclature gap**—sites that are structurally built of stone (cathedrals, fortresses) but completely omit specific rock names in the text.
* **Stone Sites**: Represent the **lithological baseline**—sites where UNESCO has successfully documented the actual rock type (e.g. *limestone*, *sandstone*, *basalt*, *granite*, *marble*) alongside the structure. 

### 2. Quarry Documentation and Sourcing
In the stone sites dataset, **27 sites** explicitly document **local quarries** (e.g. Sibenik Cathedral, Modena Cathedral, Pont du Gard). This shows that when UNESCO documentation is geologically mature, it records the complete value chain from raw geological source (quarry) to final cultural artifact (built monument).

### 3. Highly Complex Stonework Matches
The stone sites exhibit a much higher concentration of specialized carving terms like `pietra forte`, `cipollino marble`, `pietra serena`, and `istrian stone`, representing advanced historical trade networks and highly specific geological sourcing.

---

## 📂 Output Files Reference

All outputs are saved in your workspace at:
📂 **`re-scan/256_opps_on_rescanned_stone_sites/`**

* 📊 **Rescanned Stone Database**: `rescanned_stone_sites.csv`
* 🏆 **Built Monuments Database**: `rescanned_built_geological_monuments.csv`
* 🔗 **Exploded Construction Terms**: `site-term relations/exploded_construction_terms.csv`
* 🔗 **Exploded Architectural Elements**: `site-term relations/exploded_architectural_elements.csv`
* 📈 **Construction Term Frequencies**: `site-term relations/construction_term_frequency.csv`
* 📈 **Architectural Element Frequencies**: `site-term relations/architectural_element_frequency.csv`
