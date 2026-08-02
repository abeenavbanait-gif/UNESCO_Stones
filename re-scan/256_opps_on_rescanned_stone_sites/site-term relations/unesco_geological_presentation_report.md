# 🏛️ Research Report: How UNESCO Represents Building Stones and Geological Materials

This report analyzes how geological materials—such as building stones, rocks, and decorative minerals—are documented and framed in the official UNESCO World Heritage texts. 

The analysis is based on the newly generated dataset **`exploded_site_stones.csv`** and **`stone_type_frequency.csv`**.

---

## 📊 Geological Frequency Overview

Across the 254 stone-bearing sites, we extracted **326 explicit rock/stone mentions** spanning **80 unique geological types**:

### Top Stone Mentions in UNESCO Texts:
1. **Limestone**: 49 occurrences
2. **Sandstone**: 37 occurrences
3. **Marble**: 32 occurrences
4. **Granite**: 23 occurrences
5. **Coal**: 15 occurrences
6. **Adobe**: 12 occurrences
7. **Red Sandstone**: 9 occurrences
8. **Flint**: 8 occurrences
9. **Slate**: 7 occurrences
10. **Laterite**: 6 occurrences
11. **Tuff**: 6 occurrences

---

## 🔍 How UNESCO Frames Geological Materials

Our semantic analysis of OUV statements and brief descriptions reveals that UNESCO documents geological materials through four main narrative framings:

### 1. Primary Structural Framing (The Building Block)
UNESCO mentions geological materials when they constitute the primary structural fabric of a monument, indicating durability, massive engineering, or regional structural traditions.
* **Limestone** (49 mentions): Commonly cited for massive structural engineering.
  * *Example (Ħal Saflieni Hypogeum, Malta)*: *\"using cyclopean rigging to lift huge blocks of coralline limestone.\"*
* **Sandstone** (37 mentions): Linked with ancient Indian and European masonry.
  * *Example (Mahabodhi Temple, India)*: *\"a platform attached to the main temple made of polished sandstone known as Vajrasana...\"*

### 2. Decorative & Chromatic Framing (The Aesthetic Accent)
Stones are frequently described by color, texture, or polish to highlight artistic excellence, rare materials, or imperial patronage.
* **White Marble** (5 mentions) / **Marble** (32 mentions): Highlighting prestige and visual brilliance.
  * *Example (Taj Mahal, India)*: *\"An immense mausoleum of white marble... the jewel of Muslim art in India...\"*
* **Colored & Local Stones**: Used to describe contrasts in masonry facades or carvings.
  * *Example (Chhatrapati Shivaji Terminus, India)*: *\"carvings made in local yellow Malad stones blended with Italian marble and polished granite...\"*

### 3. Sourcing & Origin Framing (The Local Link)
When documentation is geologically rich, it explicitly connects structural stones to their geographic quarry source, tracing the trade routes of antiquity.
* **Egyptian Granite & Cipollino Marble** (Villa Adriana, Italy): Identifies columns of *Egyptian granite* and *cipollino marble*, indicating Roman maritime supply chains.
* **Istrian Stone** (Early Christian Monuments of Ravenna, Italy): Mentions the importation of *Istrian stone* (a dense limestone from Croatia) for Byzantine mausoleums.

### 4. Fossil & Organic Formations (The Industrial/Natural Context)
* **Coal** (15 mentions) / **Peat** (4 mentions): Appears in industrial heritage descriptions (e.g. *Zollverein Coal Mine* or prehistoric canal landscapes) indicating geological fuel sources.
* **Chalk** (4 mentions) / **Flint** (8 mentions): Appears in prehistoric mining landscapes or chalk carvings.

---

## 📂 Output Files Reference

The generated datasets are available at:
📂 **`re-scan/256_opps_on_rescanned_stone_sites/site-term relations/`**

* 🔗 **Exploded Site-Stone CSV**: `exploded_site_stones.csv` (row-by-row mapping of sites to individual stone types).
* 📈 **Stone Frequency CSV**: `stone_type_frequency.csv` (sorted list of geological materials by frequency).
