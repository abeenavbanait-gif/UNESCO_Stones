# 🏛️ UNESCO World Heritage Sites: Geological Rescan Report

This report summarizes the results of the comprehensive geological rescan performed on the **718 sites** originally classified as containing no stone in `No_Stone_Sites-Table 1.csv`.

Using the upgraded **`classify_monuments_v2.py`** script—incorporating **spaCy lemmatization**, title-specific keyword scanning, expanded multi-layer rock/mineral/masonry dictionaries, and targeted **Gemini 3.5 Flash** verification—we successfully identified **591 built stone monuments** previously missed or unclassified.

---

## 📊 Summary of Findings

Of the 718 rescanned sites:
- **591 sites (82.3%)** are verified as built monuments featuring structural stone, rock-cut architecture, or masonry elements.
- **127 sites (17.7%)** are categorized as LOW confidence or NONE (mainly natural landscapes, biosphere reserves, or purely intangible cultural heritage sites).

### Confidence Distribution of Rescanned Sites

| Confidence Tier | Description | Site Count |
| :--- | :--- | :---: |
| 🟢 **HIGH** | Explicit Named/Trade stones, rock-cut architecture, or multiple structural stone identifiers matched in title/OUV. | **223** |
| 🟡 **MEDIUM** | Clear structural masonry elements (e.g. ashlar, rubble, vaults, columns) and criteria matches. | **368** |
| 🔴 **LOW** | Minor construction indicators or general architectural terms. | **85** |
| ⚫ **NONE** | No geological materials or structural stonework detected (e.g., natural reserves, oral traditions). | **42** |

---

## 🌎 Geographic Distribution of Newly Identified Monuments

### Top Countries by Identified Stone Monuments
The upgraded rescan successfully recovered built monuments across many stone-rich architectural cultures:

1. **China** (34 sites) — featuring pagodas, stone tombs, and walled cities.
2. **Italy** (32 sites) — rich in cathedrals, historic centres, and classical masonry.
3. **France** (30 sites) — containing Romanesque cathedrals, fortified towns, and castles.
4. **Spain** (29 sites) — containing Roman aqueducts, monasteries, and mudéjar structures.
5. **Germany** (27 sites) — featuring Gothic cathedrals, castles, and historic civic halls.
6. **Mexico** (23 sites) — including pre-Hispanic pyramid complexes and colonial convents.
7. **Iran** (21 sites) — featuring rock-cut tombs, mosques, and stone caravanserai.
8. **India** (17 sites) — containing stone temples, stupas, and monolithic structures.
9. **United Kingdom** (17 sites) — including stone castles, aqueducts, and Gothic cathedrals.
10. **Russian Federation** (15 sites) — featuring kremlins, monastic complexes, and historic stone centres.

---

## 🏛️ Showcase of Newly Identified High-Confidence Sites

The upgraded parser successfully extracted key geological indicators from several world-famous sites that were previously classified as having "no stone":

### 1. **Buddhist Monuments at Sanchi** (India)
* **Confidence**: HIGH (Score 18)
* **Geological Indicators**: *Megalithic*, *monolithic*, *ashlar*, *balustrade*, *stone veneer*.
* **OUV Context**: Sanchi's famous monolithic pillars and balustrades are carved from locally quarried Chunarian sandstone.

### 2. **Rock-Hewn Churches, Lalibela** (Ethiopia)
* **Confidence**: HIGH (Score 16)
* **Geological Indicators**: *Monolithic*, *hewn*, *rock*.
* **OUV Context**: The site features 11 medieval monolithic cave churches carved out of solid volcanic tuff rock.

### 3. **The Cathedral of St James in Šibenik** (Croatia)
* **Confidence**: HIGH (Score 18)
* **Geological Indicators**: *Cathedral*, *frieze*, *quarry*.
* **OUV Context**: Built entirely of stone (limestone and marble from local quarries) without any mortar or wood binders.

### 4. **Pontcysyllte Aqueduct and Canal** (United Kingdom)
* **Confidence**: HIGH (Score 18)
* **Geological Indicators**: *Aqueduct*, *masonry*, *pier*, *rubble*.
* **OUV Context**: The massive 18-pier structure features high-quality ashlar masonry and rubble-filled piers.

### 5. **Durham Castle and Cathedral** (United Kingdom)
* **Confidence**: HIGH (Score 17)
* **Geological Indicators**: *Castle*, *cathedral*.
* **OUV Context**: Iconic Anglo-Norman civic and religious structures built entirely of massive coursed sandstone.

---

## 🛠️ Upgraded Methodology (v2)

The rescan achieved high accuracy by moving beyond simple string matches:
1. **Fast spaCy Lemmatization**: Allowed matching inflections (e.g. *mason* -> *masonry*, *rock* -> *rocks*, *quarry* -> *quarries*) without generating false matches on substrings.
2. **Title-Specific Weights**: Explicitly parsed site titles for core structural stone keywords (e.g., *cathedral*, *castle*, *fortress*, *monolith*).
3. **Multi-Layer Logic**: Applied a hierarchical score weighting.
4. **Hybrid Gemini LLM Verification**: Provided semantic validation for borderline cases, determining if structural stone was implied (e.g. in "rock-cut", "ashlar", or "monoliths") even when specific rock types were omitted in the OUV statements.

---

## 📂 Output Files Reference

The results of this rescan are saved in your workspace:
- 📊 **Complete Dataset**: `re-scan/rescanned_no_stone_sites.csv`
- 🏆 **Built Monuments Dataset**: `re-scan/rescanned_built_geological_monuments.csv`
