# 🏛️ Methodology Report: Confidence Score & Classification Calculation

This report details the mathematical formulation, layer-by-layer weights, NLP processing, and logic used to calculate the geological **Confidence Score** and assign World Heritage Sites to their respective **Confidence Tiers** in `classify_monuments_v2.py`.

---

## 📐 Scoring Formulation

The final score is computed hierarchically across four thematic layers using tokenized and lemmatized texts from the **Site Title**, **Brief Description**, and **OUV Statement**.

$$\text{Final Score} = \text{Layer 1 (Criteria)} + \text{Layer 2 (Title)} + \text{Layer 3 (Text Matches)} - \text{Layer 4 (Exclusions)}$$

---

## 🧱 Thematic Layers and Weights

### Layer 1: UNESCO Criterion Weights
UNESCO criteria indicate the architectural and historical significance of the site, serving as a primary signal for human-built stonework.
- **Criterion (iv)** (outstanding example of a type of building, architectural or technological ensemble): **+3 points**
- **Criterion (i)** (masterpiece of human creative genius): **+2 points**
- **Criterion (ii)** (interchange of human values on developments in architecture or monumental arts): **+1 point**

### Layer 2: Site Title Stone Indicators
Keywords found directly in the site title provide strong architectural signals.
* Match of title stone indicators (e.g. *stone, rock, quarry, monolith, megaliath, stele, stela, cave, carved, hewn, granite, marble, sandstone, limestone, basalt, slate, tuff, travertine, dolomite, masonry, ashlar, pyramid, cathedral, fortress, castle, aqueduct*): **+4 points**

### Layer 3: Text Keyword Matching (Mega-Dictionaries)
Keywords matched in the OUV statements and brief descriptions are grouped into dictionaries with progressive thresholds:

#### A. Geological Stone/Rock Types
*Match of igneous, sedimentary, or metamorphic rock groups (e.g. limestone, sandstone, basalt, tuff, granite, slate, marble).*
* $\ge 1$ rock type found: **+4 points**
* $\ge 3$ rock types found: **+3 points** (total +7)
* $\ge 5$ rock types found: **+3 points** (total +10)

#### B. Named / Trade / Regional Stones
*Match of high-precision named stones (e.g., Carrara marble, Portland stone, Bath limestone, Caen stone, Makrana marble).*
* $\ge 1$ named stone found: **+5 points**
* $\ge 3$ named stones found: **+3 points** (total +8)

#### C. Decorative Minerals
*Match of precious/semi-precious minerals (e.g., lapis lazuli, malachite, jasper, jade, onyx).*
* $\ge 1$ mineral found: **+2 points**

#### D. Construction & Masonry Terms
*Match of building/masonry techniques (e.g., ashlar, rubble, voussoir, dressed stone, monolith, dry stone, cyclopean masonry).*
* $\ge 2$ terms found: **+3 points**
* $\ge 5$ terms found: **+2 points** (total +5)

#### E. Building Materials (Non-stone)
*Match of masonry binders or non-stone building materials (e.g., mortar, cement, plaster, clay, brick).*
* $\ge 2$ materials found: **+2 points**

#### G. Architectural Elements & Structures
*Match of structural columns, arches, vaults, domes, or layout indicators (e.g., column, pillar, dome, vault, arch, minaret, facade).*
* $\ge 3$ elements found: **+3 points**
* $\ge 6$ elements found: **+2 points** (total +5)

### Layer 4: Exclusions (Negative Weights)
Keywords indicating non-built heritage, mobile art, or purely natural landscapes trigger deductions.
* Match of exclusion keywords (e.g., *cultural landscape, rock art, cave painting, fossil, hominid, intangible, oral tradition, textile, weaving*): **-3 points** (score bounded at a minimum of 0).

---

## 🏷️ Confidence Tier Thresholds

Tiers are assigned by evaluating the calculated score, the count of explicit stone matches, and title indicators:

### 🟢 HIGH Confidence
Assigned when there is explicit, undeniable evidence of geological construction:
- **Score** $\ge 10$ OR
- **Stone Count** $\ge 2$ (at least two distinct rock types/named stones matched) OR
- **Title Match** $\ge 1$ (explicit stone/quarry terms directly in the site name).

### 🟡 MEDIUM Confidence
Assigned when structural stone/masonry is heavily indicated:
- **Score** $\ge 4$ OR
- **Stone Count** $\ge 1$ (at least one explicit stone matched) OR
- **Construction Terms** $\ge 2$ (at least two masonry terms matched).

### 🔴 LOW Confidence
Assigned when the text has weak, general signals of built heritage:
- **Score** between $1$ and $3$.

### ⚫ NONE
Assigned when no keywords or criteria from the dictionaries are matched.
- **Score** $= 0$.

---

## 🤖 Hybrid LLM Verification (Gemini 3.5 Flash)

To resolve borderline cases without manual intervention, a targeted LLM verification pass was integrated:
- **Scope**: Evaluates candidate sites with a **Score** $\ge 3$ but **Stone Count** $= 0$ (meaning the site title or criteria indicate a monument, but the text lacks specific rock names like "marble" or "limestone").
- **Task**: Gemini analyzes the OUV text to evaluate if the site represents a built stone/masonry structure or rock-cut architecture.
- **Integration**: If Gemini confirms (`has_geological_material = true`), the site is verified as a built monument, and its LLM-extracted stone types and summaries are appended to the dataset.
