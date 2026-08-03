# Computational Linguistics and Syntactic Dependency Parsing for World Heritage Materiality Verification

**Version:** 3.0 (Living Document)  
**Location:** `methodology/01_Syntactic_Dependency_Parsing_Methodology.md`  
**Primary Implementation Script:** `classify_monuments_v3.py`  
**Framework Status:** Active / Production Academic Specification  

---

## 1. Executive Abstract & Theoretical Motivation

Traditional evaluation of textual cultural heritage records—such as official **UNESCO Outstanding Universal Value (OUV)** statements and dossier descriptions—has historically relied on Bag-of-Words (BoW) semantic density models and additive numerical point weighting (e.g., scoring models v1 and v2). While effective at establishing macro-level thematic relevance, additive point systems suffer from a core empirical vulnerability: **spurious sentence co-occurrence**. 

For example, a historical dossier might state:
> *"The medieval wooden cathedral was tragically destroyed by fire; however, the surrounding limestone cliffs and ancient karst formations preserve unique biological diversity."*

Under a legacy additive keyword engine, this text triggers positive hits for architectural monuments (*cathedral*) and geological lithology (*limestone*, *karst*), generating a misleadingly high architectural stone confidence score despite the lack of structural material linkage.

To establish **empirical proof of physical craftsmanship and architectural materiality**, our Diagnostic Engine employs an advanced **Computational Linguistics & Syntactic Dependency Parsing (v3)** protocol. By constructing formal grammatical dependency graphs of primary texts using natural language processing (`spaCy`), this methodology transcends token word counts to measure the explicit syntactical proximity and semantic modification between **Geological Materials** and **Architectural Heritage Actions**.

---

## 2. Statutory Foundation: Alignment with Article 1 of the 1972 UNESCO Convention

Under **Article 1 of the 1972 UNESCO World Heritage Convention**, cultural heritage is legally codified across three distinct typologies:
1. **Monuments:** Architectural works, works of monumental sculpture and painting, elements or structures of an archaeological nature, inscriptions, cave dwellings and combinations of features, which are of Outstanding Universal Value from the point of view of history, art or science;
2. **Groups of buildings:** Groups of separate or connected buildings which, because of their architecture, their homogeneity or their place in the landscape, are of Outstanding Universal Value from the point of view of history, art or science;
3. **Sites:** Works of man or the combined works of nature and of man, and areas including archaeological sites which are of Outstanding Universal Value from the point of view of the historical, aesthetic, ethnological or anthropological point of view.

The **Syntactic Dependency Parsing (v3)** protocol provides rigorous, publication-ready proof of physical authenticity for **Monuments** and **Groups of buildings**. By confirming that active construction verbs and masonry nouns (*quarried, carved, hewn, ashlar masonry, built*) are syntactically bound to explicit geological petrologies (*marble, granite, limestone, basalt, sandstone*), the methodology scientifically verifies when a property's universal value is fundamentally grounded in Earth science georesources and tangible lithic engineering.

---

## 3. Mathematical and Linguistic Mechanism

### 3.1 Formal Representation of Sentence Syntax
Each sentence $S$ extracted from an OUV or brief descriptive narrative is tokenized and transformed into a directed grammatical dependency graph $G = (V, E)$, where:
* $V$ represents the set of linguistic words or punctuation tokens $t_i$.
* $E$ represents directed dependency arcs $(t_i, t_j, r)$ representing a structural grammatical relationship $r$ (e.g., nominal subject `nsubj`, direct object `dobj`, prepositional modifier `prep`, adjective modifier `amod`) directed from head token $t_i$ to child dependent $t_j$.

### 3.2 Defined Token Vocabularies
The parser maps all lemmatized tokens against two specialized canonical ontologies:
* **Geological & Material Set ($\mathcal{G}$):** Covers explicit petrological classifications across major lithic families—including **Sedimentary** (*limestone, sandstone, travertine, shale, gypsum*), **Igneous** (*granite, basalt, tuff, andesite, porphyry, diabase*), **Metamorphic** (*marble, quartzite, slate, schist, gneiss*), and recognized commercial trade stones.
* **Cultural & Architectural Heritage Set ($\mathcal{C}$):** Incorporates Article 1 monumental categories (*monument, temple, cathedral, fortress, castle, aqueduct, tomb, pyramid, mausoleum*), masonry engineering practices (*ashlar, cladding, revetment, drystone*), and dynamic lapidary verbs (*quarried, carved, sculpted, hewn, constructed, cut*).

### 3.3 Shortest Dependency Path Algorithm
To evaluate whether a geological token $g \in \mathcal{G}$ linguistically describes or modifies an architectural token $c \in \mathcal{C}$, the engine determines their **Lowest Common Ancestor (LCA)** within the directed root tree and calculates the structural grammatical distance $d_{\text{dep}}(g, c)$:

1. Construct the structural pathway from token $g$ upwards to the sentence root:  
   $$P(g) = [g, \text{head}(g), \text{head}(\text{head}(g)), \dots, \text{root}]$$
2. Construct the structural pathway from token $c$ upwards to the sentence root:  
   $$P(c) = [c, \text{head}(c), \text{head}(\text{head}(c)), \dots, \text{root}]$$
3. Identify the shared intersection node of minimal vertical depth, defined as the Lowest Common Ancestor ($LCA$):  
   $$LCA(g, c) = \arg\min_{v \in P(g) \cap P(c)} \text{depth}(v)$$
4. Calculate total dependency graph distance (in grammatical edges):  
   $$d_{\text{dep}}(g, c) = \text{index}_{P(g)}(LCA) + \text{index}_{P(c)}(LCA)$$

---

## 4. Quantitative Classification Tiers & Decision Rules

Unlike legacy additive integer point metrics, the v3 protocol maps sites into four categorical tiers of empirical grammatical assurance based on the minimum structural graph distance across all sentences:

$$\min_{S \in \text{Text}} \min_{g \in \mathcal{G}, c \in \mathcal{C}} d_{\text{dep}}(g, c)$$

| Confidence Tier | Mathematical Condition | Linguistic Interpretation & Architectural Proof | Representative Case Study |
| :--- | :--- | :--- | :--- |
| **HIGH** | $d_{\text{dep}}(g, c) \le 3$ | **Strong Grammatical Linkage:** Immediate syntactical relationship between stone georesources and built monuments within a short dependency radius ($\le 3$ edges). Proves explicit tangible masonry construction. | *"The imperial **palace** was **built** from local white **marble**."*<br>($d_{\text{dep}}(\text{marble}, \text{palace}) = 3$) |
| **MEDIUM** | $d_{\text{dep}}(g, c) > 3$ | **Sentence Co-Occurrence:** Both geological materials and structural monument terms appear within the boundary of a single sentence, but are separated by $>3$ syntax edges (suggesting ambient landscape or unlinked co-occurrence). | *"The ruined clay **citadel** overlooks the fertile valley and surrounding granite **mountains**."*<br>($d_{\text{dep}}(\text{granite}, \text{citadel}) = 5$) |
| **LOW** | $\mathcal{G} \ne \emptyset \land \mathcal{C} = \emptyset$ | **Isolated Geological References:** Lithic and petrological terminology is explicitly present in the sentence, but zero architectural, structural, or lapidary words appear in proximity. | *"Extensive folds of **limestone** and **dolomite** characterize the plateau's stratigraphy."* |
| **NONE** | $\mathcal{G} = \emptyset$ | **Complete Material Absence:** Zero identified mentions of building rock species or lapidary minerals throughout the processed textual corpus. | *"Intangible traditions and polyphonic chants of the mountain village."* |

---

## 5. Computational Pipeline & Automated Extraction

When executing `classify_monuments_v3.py`, the system performs the following sequential computational workflow:

1. **Text Normalization & Ingestion:** Concatenates official UNESCO site titles, brief historical summaries, and complete OUV records into an analytical string buffer.
2. **Lemmatization & Dependency Parsing:** Operates high-throughput `spaCy` NLP pipelines to generate parts-of-speech (POS) tags and syntactic dependency parse trees. Lemmatization transforms inflectional words (*quarries, quarried, quarrying* $\to$ *quarry*) before set intersection evaluation.
3. **Contextual Evidentiary Harvesting:** To ensure scientific repeatability and auditability, whenever a sentence triggers **HIGH** or **MEDIUM** confidence, the full literal text of the matching sentence is archived in the `match_context` data field. This enables direct human expert auditing of automated grammatical classifications without manually re-reading full dossiers.
4. **Data Persistence:** Exports the classified database (`v3_classified_sites.csv`) containing formal evaluations: `confidence_v3`, harvested geological species (`geo_materials_found`), identified architectural features (`cultural_concepts_found`), and evidentiary quote trails (`match_context`).

---

## 6. Document Lifecycle & Continuous Updating Protocol

As part of our modular academic repository, this document represents the **authoritative reference methodology** for dependency parsing in the UNESCO Heritage Stones project. 

### Guidelines for Future Iterations:
* **Dictionary Enrichment:** Any addition of regional trade stones (e.g., newly designated *IUGS Global Heritage Stone Resources*) or historical architectural terminology must be updated within `GEO_MAT_SET` and `CULT_HER_SET` definitions in `classify_monuments_v3.py` and reflected in subsequent versions of this document.
* **Algorithm Evolution:** Should future updates integrate transformer-based zero-shot coreference resolution (to link structural pronouns across sentence boundaries, e.g., *"The abbey was completed in 1204. **It** was built using local limestone"*), the mathematical formulations in Section 3 and threshold tables in Section 4 will be version-bumped and amended with full historical changelog attribution.

---
*End of Methodology Document 01: Syntactic Dependency Parsing.*
