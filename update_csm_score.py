import pandas as pd
import os
import re

ROCK_TYPES = ["marble", "limestone", "sandstone", "granite", "tuff", "basalt", "slate", "porphyry", "travertine", "gneiss", "dolerite", "calcite", "quartzite", "alabaster", "schist", "chalk", "syenite", "gabbro", "andesite", "coral rag", "flint"]
CONSTRUCTION_CRAFTS = ["masonry", "quarry", "quarrying", "quarried", "ashlar", "carved", "hewn", "mortar", "brick", "dry-stone", "stonemasonry", "cladding", "veneer", "stone wall", "stone block", "stone blocks", "stone carving", "sculpted stone"]

def compute_csm_metrics(row):
    score = 0
    reasons = []
    materials_count = 0
    
    txt_lower = str(row.get('description', '')) + " " + str(row.get('brief_description', '')) + " " + str(row.get('ouv_statement', ''))
    txt_lower = txt_lower.lower()
    
    # 1. Trade stones (+5 each)
    named = str(row.get('named_trade_stones_v2', '') if pd.notna(row.get('named_trade_stones_v2', '')) else '')
    named_list = [s.strip().title() for s in named.split(';') if s.strip() and s.strip().lower() not in ['nan', 'none', 'none detected', '']]
    if named_list:
        pts = 5 * len(named_list)
        score += pts
        materials_count += len(named_list)
        reasons.append(f"{len(named_list)} Trade Stone(s) (+{pts})")
        
    # 2. General stones (+3 each) - merge CSV column + text scans
    stones = str(row.get('stone_types_found_v2', '') if pd.notna(row.get('stone_types_found_v2', '')) else '')
    stones_list = [s.strip().title() for s in stones.split(';') if s.strip() and s.strip().lower() not in ['nan', 'none', 'none detected', '']]
    
    # Text scan for rock types
    for r in ROCK_TYPES:
        if re.search(r'\b' + re.escape(r) + r'\b', txt_lower) and r.title() not in stones_list and r.title() not in named_list:
            stones_list.append(r.title())
            
    if stones_list:
        pts = 3 * len(stones_list)
        score += pts
        materials_count += len(stones_list)
        reasons.append(f"{len(stones_list)} Stone Species (+{pts})")
        
    # 3. Construction terms (+2 each) - merge CSV column + text scans
    const = str(row.get('construction_terms_v2', '') if pd.notna(row.get('construction_terms_v2', '')) else '')
    const_list = [s.strip().title() for s in const.split(';') if s.strip() and s.strip().lower() not in ['nan', 'none', 'none detected', '']]
    
    for c in CONSTRUCTION_CRAFTS:
        if re.search(r'\b' + re.escape(c) + r'\b', txt_lower) and c.title() not in const_list:
            const_list.append(c.title())
            
    if const_list:
        pts = 2 * len(const_list)
        score += pts
        materials_count += len(const_list)
        reasons.append(f"{len(const_list)} Construction Craft(s) (+{pts})")
        
    # 4. Title / Category Stone keyword match (+3)
    t_match = str(row.get('matched_title_terms_v2', '') if pd.notna(row.get('matched_title_terms_v2', '')) else '')
    c_match = str(row.get('matched_categories_v2', '') if pd.notna(row.get('matched_categories_v2', '')) else '')
    site_name_val = str(row.get('site_name', '')).lower()
    
    has_tag = False
    for t in [t_match, c_match, site_name_val]:
        for kw in ['stone', 'rock', 'quarry', 'ouv_stone', 'title_stone_keyword', 'marble', 'granite', 'limestone', 'cathedral', 'castle', 'fortress', 'palace']:
            if kw in t.lower():
                has_tag = True
                break
        if has_tag: break
        
    if has_tag:
        score += 3
        reasons.append("Title/OUV Stone/Monument Match (+3)")
        
    # Cap score at 35
    score = min(35, score)
    
    # Confidence rating
    if score >= 10 or (len(named_list) > 0 and len(stones_list) > 0):
        conf = "HIGH"
    elif score >= 6 or len(stones_list) > 0 or len(const_list) >= 2:
        conf = "MEDIUM"
    elif score >= 2 or len(const_list) > 0 or has_tag:
        conf = "LOW"
    else:
        conf = "NONE"
        
    reasons_str = "; ".join(reasons) if reasons else "No explicit stone/construction terms in schema"
    return score, conf, materials_count, reasons_str

target_files = [
    "v3_991_classified.csv",
    "30_july_output/987_built_monuments.csv",
    "30_july_output/4_non_building_sites.csv",
    "30_july_output/645_geological_monuments.csv",
    "30_july_output/832_general_building_monuments.csv"
]

print("Starting deep calculation and persistence of Construction & Stone Materials Score (csm_score)...")
for filepath in target_files:
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        results = df.apply(compute_csm_metrics, axis=1)
        df['csm_score'] = [r[0] for r in results]
        df['csm_confidence'] = [r[1] for r in results]
        df['csm_materials_count'] = [r[2] for r in results]
        df['csm_reasons'] = [r[3] for r in results]
        df.to_csv(filepath, index=False)
        print(f"✅ Updated {filepath} -> avg csm_score: +{df['csm_score'].mean():.2f} (max: +{df['csm_score'].max()})")
print("All CSV databases successfully updated with enriched csm_score!")
