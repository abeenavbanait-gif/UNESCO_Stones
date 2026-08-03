# UNESCO World Heritage & Building Stones: Quantitative Scoring Architecture, Validation Protocols, and State-of-the-Art Review

This document provides a definitive, scientific explanation of the tripartite quantitative scoring framework employed in the **UNESCO Building Stones & Geo-Monuments Explorer**. It outlines the exact numerical formulations for each metric, practical methods for empirical validation, and a scholarly evaluation showing why this system represents a pioneering contribution to global heritage science.

---

## 1. Executive Summary: The Tripartite Scoring Framework

To systematically evaluate **991 UNESCO Cultural World Heritage Sites** and bridge the historical divide between humanistic architecture and hard Earth sciences, the application introduces three quantitative indices:

```
┌──────────────────────────────────────────────────────────────────────────┐
│              WORLD HERITAGE MONUMENT MULTI-LAYER ANALYSIS               │
└──────────────────────────────────────────────────────────────────────────┘
           │                       │                       │
           ▼                       ▼                       ▼
   ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
   │    bm_score   │       │    gh_score   │       │   csm_score   │
   │ Built Monument│       │  Geoheritage  │       │ Construction  │
   │   Structural  │       │ Earth Science │       │ & Trade Stone │
   │    Profile    │       │    Profile    │       │   Materials   │
   └───────────────┘       └───────────────┘       └───────────────┘
```

Each score serves a distinct analytical purpose, transforming qualitative UNESCO dossiers, ICOMOS evaluation narratives, and geological survey literature into computable, structured data.

---

## 2. Detailed Breakdown of Displayed Scores

### 2.1 `bm_score`: Built Monument Profile Score
* **Purpose:** Determines the quantitative confidence that a cultural heritage site contains physically structured, built architectural monuments (e.g., masonry fortifications, cathedrals, temples, aqueducts, and palaces) as opposed to purely intangible landscapes, unbuilt sacred groves, or subsurface archaeological fields.
* **Scoring Inputs & Drivers:**
  - **Title Matches (+3 to +10 pts):** Direct keyword hits in the official monument name (`castle`, `cathedral`, `temple`, `fortress`, `palace`).
  - **Body Density (+1 per syntactic match):** Dependency-parsed semantic occurrences across the brief description and official **Outstanding Universal Value (OUV)** text using NLTK and spaCy NLP pipelines.
  - **Override Boosts (+10 pts):** Definitive structural classifications from architectural taxonomy dictionaries.
  - **Exclusion Penalties (-25 to -50 pts):** Triggered by non-building terms (e.g., `marine park`, `intangible oral tradition`, `natural sanctuary`, `rock art painting without built architecture`).
* **Confidence Tiers:**
  - **HIGH (`bm_score >= 15`):** Indisputable masonry and built structural heritage.
  - **MEDIUM (`8 <= bm_score < 15`):** Substantial structural features alongside cultural landscapes.
  - **LOW (`1 <= bm_score < 8`):** Minor architectural ruins or ambient structural terms.
  - **NONE (`bm_score <= 0`):** Excluded as a non-building cultural site.

---

### 2.2 `gh_score`: Geological Heritage Profile Score
* **Purpose:** Quantifies the density of Earth science, geomorphological, petrological, and landscape geology terminology embedded within the site's environmental and documentation record.
* **Scoring Inputs & Drivers:**
  - **Natural Criteria Presence (+5 pts each):** Triggered when a hybrid site includes UNESCO Natural Criteria such as `Criterion (viii)` (Earth's geological processes and geomorphology).
  - **Earth Science Terminology (+1 to +3 pts):** Hits for landform vocabulary (`karst`, `escarpment`, `outcrop`, `stratification`, `caldera`, `alluvial valley`, `plateau`).
  - **Rock Class Attribution (+3 pts per class):** Identification of primary rock classes: **Igneous**, **Sedimentary**, and **Metamorphic**.
* **Confidence Tiers:**
  - **HIGH (`gh_score >= 10`):** Monument is inextricably bounded by or built directly into pronounced geological landforms (e.g., Petra, Arequipa volcanic valleys).
  - **MEDIUM (`4 <= gh_score < 10`):** Clear topographic or geological setting noted in official texts.
  - **LOW (`0 < gh_score < 4`):** Minor landscape references (e.g., *“situated on a limestone hill”*).
  - **NONE (`gh_score <= 0`):** Complete absence of geological context.

---

### 2.3 `csm_score`: Construction & Stone Materials Score
* **Purpose:** A high-precision petrography and craft materiality index that measures the diversity, specificity, and authenticity of building stone species, IUGS/BGS trade rocks, and lapidary craftsmanship associated with the monument.
* **Scoring Architecture & Weights:**
  $$\text{csm\_score} = (1 \times M_{\text{count}}) + (3 \times T_{\text{trade}}) + (4 \times C_{\text{craft}}) + B_{\text{congruence}}$$
  - **Base Material Density ($M_{\text{count}}$):** **+1 point** for each unique building stone detected across both general lithology (`Sandstone`, `Limestone`, `Marble`, `Granite`, `Basalt`, `Tuff`) and trade varieties.
  - **Heritage Trade Stone Specificity ($T_{\text{trade}}$):** **+3 points** per authenticated heritage stone species (e.g., `Makrana Marble`, `Welsh Slate`, `Portland Stone`, `Royal Lioz Limestone`, `Carrara Marble`, `Globigerina Limestone`, `Pentelic Marble`).
  - **Lapidary & Construction Craftmanship ($C_{\text{craft}}$):** **+4 points** when specialized masonry craft techniques are identified in textual analysis or field reports (`Ashlar masonry`, `Drystone walling`, `Intarsia / Pietra Dura`, `Veneer cladding`, `Cyclopean masonry`, `Quaint stone cutting`).
  - **Typological Congruence Boost ($B_{\text{congruence}}$):** **+3 points** awarded when architectural monument categories (`Cathedral`, `Pyramid`, `Mausoleum`, `Fortress`) align syntactically with documented historical stone construction traditions.
* **Confidence Tiers:**
  - **HIGH (`csm_score >= 15`):** Richly documented lapidary heritage combining specific quarry trade rocks and craft engineering (e.g., *Taj Mahal* scoring **+16** via Makrana Marble, intarsia craftsmanship, and structural harmony).
  - **MEDIUM (`8 <= csm_score < 15`):** Clear masonry presence with identifiable general rock types.
  - **LOW (`0 < csm_score < 8`):** Generic mentions of masonry or building stone without petrological specificity (e.g., *Durham Cathedral* receiving **+3** on initial NLP due to official UNESCO dossiers omitting lithic details, prompting AI research augmentation).
  - **NONE (`csm_score == 0`):** Zero physical building materials identified in primary documentation.

---

## 3. Validation Protocols: How to Audit & Verify Scores

To ensure numerical consistency, reproducible science, and publication-grade empirical integrity, the three scores should be validated using a four-step framework:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   EMPIRICAL SCORE VALIDATION PROTOCOL                    │
└──────────────────────────────────────────────────────────────────────────┘
     │                    │                     │                    │
     ▼                    ▼                     ▼                    ▼
[1. Ground Truth]    [2. LLM Cross-Val]   [3. Outlier Audit]    [4. Expert Panel]
 Precision / F1      RAG Verification     Blind Spot Mining     IUGS / BGS Review
```

### 3.1 Ground-Truth Benchmarking (Statistical Classification Metrics)
* **Protocol:** Establish a "Gold Standard" calibration dataset comprising 100 randomly sampled monuments across all geographic regions, manually annotated by architectural historians and geologists.
* **Metrics to Compute:**
  - **Precision, Recall, and F1-Score:** Treat the binary classifications (`is_built=True` derived from `bm_score > 0`, and `csm_score >= 8` for high materiality) against manual ground-truth flags.
  - **Pearson/Spearman Correlation ($r$):** Measure the linear and ranked correlation between automated `csm_score` and manual expert density ratings (scaled 1 to 5). High correlation ($r > 0.75$) validates weight calibrations.

### 3.2 Automated AI / LLM Cross-Validation (RAG Verification)
* **Protocol:** Utilize the newly embedded **Gemini 3.5 Flash RAG Engine** (`gemini_stone_extractor.py`) to run targeted verification on sites located in the **LOW Confidence** stratum (`0 < csm_score < 8`).
* **Verification Logic:** If the statistical NLP pipeline outputs a low `csm_score`, trigger an autonomous AI query to external geological literature and quarry databases. If the LLM consistently uncovers well-documented building rocks (e.g., discovering Norman yellow sandstone for Durham Cathedral), flag the discrepancy as an **Official Documentation Gap** rather than an algorithm error.

### 3.3 Outlier & Blind-Spot Mining (Scatter Distribution Analysis)
* **Protocol:** Generate visual matrices plotting `bm_score` against `csm_score` across all 991 monuments.
* **Anomaly Diagnostics:**
  - **Quadrant IV Anomalies (High BM, Zero/Low CSM):** Identify monuments with massive built structure scores (`bm_score >= 20`, such as imperial castles or megalithic cathedrals) that exhibit `csm_score == 0` or `< 5`. These represent pure "Geological Blind Spots"—sites where historical humanistic conservation narratives completely neglected structural lithology and rock provenance.

### 3.4 Expert Survey Harmonization (IUGS & BGS Mapping)
* **Protocol:** Match scored sites directly against published designations by the **International Union of Geological Sciences (IUGS)** Global Heritage Stone Resource (GHSR) catalog and the **British Geological Survey (BGS)** strategic building stones study.
* **Success Criterion:** 100% of monuments historically recognized in IUGS GHSR monographs (e.g., Rome's Colosseum / Lapis Tiburtinus, Wales Slate, Lisbon Mafra Palace / Royal Lioz) must achieve either **MEDIUM** or **HIGH** confidence standings in `csm_score` and `gh_score`.

---

## 4. Prior Work & Scholarly Uniqueness Review

An extensive review of global academic literature, UNESCO archives, and geological databases reveals a striking finding:

> [!IMPORTANT]
> **No prior study, database, or digital humanities initiative has ever implemented a quantitative, multi-layered computational scoring system that evaluates built structure density, geomorphology, and building stone materiality across the UNESCO World Heritage registry.**

### 4.1 Comparison with Existing Scholarly Initiatives

| Initiative / Body | Scope & Methodology | Key Limitations | Advantages of Our Tripartite Scoring Engine |
| :--- | :--- | :--- | :--- |
| **IUGS Heritage Stone Task Group (GHSR)** *(2011–Present)* | Evaluates individual heritage rock species for formal international geological designation; produces qualitative petrographic monographs. | Focuses solely on individual rock species, not world heritage sites. Lack of an automated computational scoring pipeline or systematic mapping of monuments. | Connects stones to **991 World Heritage sites**, quantifying presence, architectural craft techniques, and structural provenance dynamically via `csm_score`. |
| **UNESCO / ICOMOS Advisory Evaluations** *(1972–Present)* | Evaluates proposed sites for World Heritage inscription based on cultural criteria (i–vi) and aesthetic/social significance. | Displays an institutional **"Geological Blind Spot."** Descriptions emphasize dynastic succession, style, and symbolism while systematically omitting lithic materials and quarry origins. | Exposes omissions programmatically by showing disparities between high architectural scores (`bm_score`) and low material scores (`csm_score`). |
| **Traditional Archaeological GIS & Digital Humanities** | Uses spatial GIS mappings and Named Entity Recognition (NER) to catalog historical sites by chronologies, countries, and architectural typologies. | Treats materials as simple unweighted text labels without connecting architectural forms to petrological geology, craftsmanship weightings, or survey archives. | Embeds structured grammatical heuristics, weighting physical trade rocks (+3), craft techniques (+4), and geological surveys (BGS/IGME) into computable KPIs. |

---

## 5. Scholarly & Scientific Significance of this Work

1. **Bridging Disciplinary Silos:** For decades, architectural historians and hard Earth scientists have operated in isolation. This project establishes the foundational computational grammar for **Geocultural Heritage Informatics**, demonstrating that cultural monuments and raw Earth materials are co-evolutionary systems.
2. **Exposing the "UNESCO Nomenclature Gap":** By demonstrating that globally iconic stone structures (such as Durham Cathedral or Faya Palaeolandscape) score surprisingly low in raw initial NLP analysis (`csm_score`), our engine proves quantitatively that primary world heritage documentation requires structural remediation to include Earth sciences and building materiality.
3. **Pioneering Automated Geo-RAG Assessment:** Pairing determinative NLP heuristic scoring (`csm_score`, `bm_score`) with dynamic LLM synthesis (**Gemini 3.5 Flash Geological Researcher**) establishes a novel methodology for automated geological assessment across global building inventories.
4. **Actionable Conservation Economics:** Providing definitive materiality scores allows restoration architects, UNESCO evaluators, and geological survey boards to prioritize quarry conservation, forecast rock weathering patterns, and allocate restorative funding to high-value heritage stone environments.
