"""
Built Monument Classifier v3 — Pure NLP, No AI
================================================
Properly classifies all 991 UNESCO cultural sites into:
  1. Built Monuments (sites with any constructed structures)
  2. Non-Building Sites (landscapes, rock art, fossils, etc.)

Uses spaCy lemmatization + massive keyword dictionaries covering
ALL types of built structures regardless of material.
"""

import os, re, sys
import pandas as pd
from tqdm import tqdm

# ── spaCy setup ──
import spacy
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
print("✅ spaCy loaded.")

# ══════════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE BUILDING / STRUCTURE KEYWORD DICTIONARIES
# ══════════════════════════════════════════════════════════════════════════════

# ── TITLE KEYWORDS: Structural building type words found in site names ──
title_building_keywords = [
    # Religious structures
    'cathedral', 'church', 'churches', 'chapel', 'basilica', 'abbey', 'monastery',
    'convent', 'priory', 'mosque', 'masjid', 'synagogue', 'temple', 'temples',
    'shrine', 'pagoda', 'stupa', 'wat', 'dagoba', 'chorten', 'candi',
    'minaret', 'seminary', 'mission', 'missions',
    
    # Fortifications
    'fortress', 'fort', 'forts', 'fortification', 'fortifications', 'fortified',
    'castle', 'castles', 'citadel', 'alcazar', 'alcázar', 'kremlin',
    'wall', 'walls', 'rampart', 'bastion', 'tower', 'towers', 'kasbah', 'casbah',
    'ksar', 'ksour', 'ribat', 'fortaleza', 'fuerte',
    
    # Palatial / Residential
    'palace', 'palaces', 'palais', 'palazzo', 'villa', 'villas', 'manor', 'mansion',
    'house', 'houses', 'housing', 'residence', 'residences', 'château', 'chateau',
    'schloss', 'hof', 'maison',
    
    # Urban structures
    'town', 'city', 'centre', 'center', 'quarter', 'district', 'medina',
    'historic', 'historical', 'old', 'ancient', 'medieval',
    
    # Tombs / Funerary
    'tomb', 'tombs', 'mausoleum', 'necropolis', 'cemetery', 'cenotaph',
    'pyramid', 'pyramids', 'hypogeum', 'tumulus', 'tumuli', 'burial',
    
    # Infrastructure
    'bridge', 'bridges', 'aqueduct', 'canal', 'dam', 'port', 'harbour', 'harbor',
    'lighthouse', 'railway', 'railroad', 'station', 'factory', 'factories',
    'mill', 'mills', 'ironworks', 'works', 'mine', 'mines', 'mining',
    'industrial', 'lift', 'lifts', 'sluice', 'lock',
    
    # Monumental
    'monument', 'monuments', 'monumental', 'memorial', 'column', 'obelisk',
    'statue', 'fountain', 'gate', 'gateway', 'arch', 'triumphal',
    
    # Architectural / Built
    'building', 'buildings', 'built', 'erected', 'constructed', 'architecture',
    'architectural', 'ensemble', 'complex', 'compound',
    'ruins', 'ruin', 'ruined',
    
    # Specific structure types
    'amphitheatre', 'amphitheater', 'theatre', 'theater', 'colosseum', 'hippodrome',
    'arena', 'stadium', 'bath', 'baths', 'thermae', 'hammam',
    'garden', 'gardens', 'park', 'square', 'plaza',
    'market', 'bazaar', 'souk', 'caravanserai', 'caravansaray', 'khan',
    'hospital', 'hospice', 'university', 'library', 'school', 'madrasa', 'madrasah',
    'observatory', 'museum', 'gallery',
    
    # Water / Agriculture structures
    'qanat', 'aflaj', 'irrigation', 'terrace', 'terraces',
    'reservoir', 'cistern', 'well', 'stepwell',
    
    # Miscellaneous
    'stoa', 'agora', 'forum', 'acropolis',
    'diaolou', 'tulou', 'trulli',
    'speicherstadt', 'kontorhaus',
    'earthwork', 'earthworks', 'mound', 'mounds',
    'plantation', 'plantations', 'roça', 'roças',
    'village', 'villages', 'archaeological',
    'convict', 'prison', 'barracks', 'camp',
    
    # UNESCO common descriptors that imply buildings
    'settlement', 'settlements', 'site', 'sites',
]

# ── BODY TEXT KEYWORDS: Phrases that indicate built/constructed structures ──
body_building_keywords = [
    # Structural verbs and phrases (lemmatized forms)
    'build', 'built', 'construct', 'constructed', 'erect', 'erected', 'raise',
    'founded', 'establish', 'established', 'rebuild', 'rebuilt', 'restore',
    'restored', 'renovate', 'renovated', 'reconstruct', 'reconstructed',
    
    # General structure nouns
    'building', 'buildings', 'structure', 'structures', 'edifice', 'edifices',
    'construction', 'monument', 'monuments',
    
    # Religious
    'cathedral', 'church', 'churches', 'chapel', 'chapels', 'basilica',
    'abbey', 'monastery', 'monasteries', 'convent', 'convents', 'priory',
    'mosque', 'mosques', 'masjid', 'synagogue', 'temple', 'temples',
    'shrine', 'shrines', 'pagoda', 'pagodas', 'stupa', 'stupas',
    'minaret', 'minarets', 'seminary', 'mission', 'missions',
    
    # Fortifications
    'fortress', 'fortresses', 'fort', 'forts', 'fortification', 'fortifications',
    'fortified', 'castle', 'castles', 'citadel', 'citadels',
    'rampart', 'ramparts', 'bastion', 'bastions', 'battlement', 'battlements',
    'tower', 'towers', 'turret', 'turrets', 'watchtower',
    'wall', 'walls', 'enclosure', 'stockade', 'palisade',
    'kasbah', 'casbah', 'ksar', 'ksour', 'ribat', 'kremlin', 'alcazar',
    
    # Palatial / Residential
    'palace', 'palaces', 'villa', 'villas', 'manor', 'manors', 'mansion',
    'house', 'houses', 'dwelling', 'dwellings', 'residence', 'residences',
    'château', 'chateau', 'schloss', 'palazzo',
    
    # Urban
    'town', 'city', 'quarter', 'district', 'neighbourhood', 'neighborhood',
    'medina', 'souk', 'bazaar', 'market', 'marketplace',
    'street', 'avenue', 'boulevard', 'promenade',
    
    # Funerary
    'tomb', 'tombs', 'mausoleum', 'mausoleums', 'necropolis', 'cemetery',
    'burial', 'cenotaph', 'sarcophagus', 'crypt', 'catacomb', 'catacombs',
    'pyramid', 'pyramids', 'mastaba', 'hypogeum',
    
    # Infrastructure
    'bridge', 'bridges', 'aqueduct', 'aqueducts', 'viaduct', 'viaducts',
    'canal', 'canals', 'dam', 'dams', 'dike', 'dyke', 'levee',
    'port', 'harbour', 'harbor', 'wharf', 'pier', 'dock', 'quay',
    'lighthouse', 'lighthouses',
    'railway', 'railroad', 'station', 'stations', 'depot',
    'factory', 'factories', 'mill', 'mills', 'workshop', 'workshops',
    'warehouse', 'warehouses', 'storehouse', 'granary',
    'ironworks', 'steelworks', 'foundry', 'smelter', 'forge', 'kiln',
    'mine', 'mines', 'mining', 'shaft', 'tunnel',
    
    # Architectural elements
    'arch', 'arches', 'vault', 'vaults', 'dome', 'domes', 'cupola',
    'column', 'columns', 'pillar', 'pillars', 'colonnade',
    'facade', 'facades', 'portico', 'porticos', 'loggia',
    'staircase', 'staircases', 'balcony', 'balconies',
    'courtyard', 'courtyards', 'cloister', 'cloisters',
    'nave', 'apse', 'transept', 'chancel', 'narthex',
    'buttress', 'buttresses', 'spire', 'spires',
    'roof', 'roofs', 'ceiling', 'ceilings', 'floor', 'floors',
    'foundation', 'foundations',
    
    # Materials (indicates physical construction)
    'masonry', 'stonework', 'brickwork', 'woodwork', 'ironwork',
    'stone', 'brick', 'bricks', 'concrete', 'mortar', 'plaster',
    'timber', 'adobe', 'stucco',
    'marble', 'granite', 'sandstone', 'limestone', 'travertine',
    'slate', 'basalt', 'tuff', 'laterite',
    
    # Decorative building features
    'fresco', 'frescoes', 'mosaic', 'mosaics', 'mural', 'murals',
    'stained glass', 'relief', 'reliefs', 'sculpture', 'sculptures',
    'carving', 'carvings', 'ornament', 'ornaments',
    'inscription', 'inscriptions',
    
    # Water structures
    'qanat', 'qanats', 'aflaj', 'cistern', 'cisterns', 'reservoir',
    'stepwell', 'well', 'wells', 'fountain', 'fountains',
    'irrigation', 'sluice', 'lock', 'locks',
    
    # Other
    'caravanserai', 'caravansaray', 'khan', 'funduq',
    'agora', 'forum', 'acropolis', 'stoa',
    'amphitheatre', 'amphitheater', 'theatre', 'theater',
    'colosseum', 'hippodrome', 'arena', 'stadium',
    'bath', 'baths', 'thermae', 'hammam',
    'hospital', 'university', 'library', 'school', 'madrasa', 'madrasah',
    'observatory',
    'garden', 'gardens', 'park',
    'diaolou', 'tulou', 'trulli',
    'earthwork', 'earthworks',
    'pile dwelling', 'pile dwellings', 'stilt house',
    'rock-cut', 'rock cut', 'cave temple', 'cave church',
    'plantation', 'plantations', 'roça', 'roças', 'estate', 'estates',
    'village', 'villages', 'hamlet', 'hamlets', 'settlement', 'settlements',
    'camp', 'camps', 'barracks', 'prison', 'convict',
    'archaeological site', 'archaeological complex', 'ruins', 'ruin',
    'subterranean', 'underground',
    
    # Construction action phrases
    'architectural', 'architecture', 'urban planning', 'town planning',
    'designed by', 'commissioned',
]

# ── STRONG EXCLUSION: Sites that are definitively NOT built monuments ──
# These override building signals if the site is primarily about these topics
strong_non_building_indicators = [
    'cultural landscape', 'agave landscape', 'coffee landscape', 'tea landscape',
    'wine landscape', 'hop landscape', 'vineyard landscape',
    'rock art', 'cave painting', 'cave art', 'cave drawing',
    'petroglyph', 'petroglyphs', 'pictograph', 'pictographs',
    'geoglyph', 'geoglyphs',
    'fossil', 'fossils', 'hominid', 'hominin', 'palaeontological', 'paleontological',
    'early man', 'prehistoric man',
    'hunting ground', 'buffalo jump',
    'oral tradition', 'intangible heritage',
]

# ══════════════════════════════════════════════════════════════════════════════
# REGEX CACHE AND MATCHING
# ══════════════════════════════════════════════════════════════════════════════

_REGEX_CACHE = {}

def has_keyword(text, keyword):
    """Check if a keyword exists in text using word boundary regex."""
    kw_lower = keyword.lower()
    if kw_lower not in _REGEX_CACHE:
        pattern = r'\b' + re.escape(kw_lower) + r'\b'
        _REGEX_CACHE[kw_lower] = re.compile(pattern, re.IGNORECASE)
    return bool(_REGEX_CACHE[kw_lower].search(text))

def count_keyword_hits(text, keyword_list):
    """Count how many unique keywords from the list appear in the text."""
    hits = []
    for kw in keyword_list:
        if has_keyword(text, kw):
            hits.append(kw)
    return list(set(hits))

# ══════════════════════════════════════════════════════════════════════════════
# LEMMATIZATION
# ══════════════════════════════════════════════════════════════════════════════

def batch_lemmatize(texts):
    """Batch lemmatize using spaCy pipe."""
    results = []
    docs = nlp.pipe(texts, batch_size=200)
    for doc in tqdm(docs, total=len(texts), desc="Lemmatizing"):
        lemmas = [token.lemma_.lower() for token in doc if not token.is_punct]
        results.append(" ".join(lemmas))
    return results

# ══════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def classify_site(site_name, site_name_lem, body_text_lem, brief_desc_raw, ouv_raw):
    """
    Classify a single site as Built Monument or Non-Building.
    Returns (is_built: bool, confidence: str, score: int, reasons: list, exclusions: list)
    """
    score = 0
    reasons = []
    exclusions = []
    
    # ── STEP 1: Title keyword scan ──
    title_hits = count_keyword_hits(site_name_lem, title_building_keywords)
    # Also scan raw site name for proper nouns the lemmatizer might mangle
    title_hits_raw = count_keyword_hits(site_name.lower(), title_building_keywords)
    title_hits_combined = list(set(title_hits + title_hits_raw))
    
    if len(title_hits_combined) >= 1:
        score += 6 * len(title_hits_combined)  # Strong signal
        reasons.append(f"TITLE[{', '.join(title_hits_combined[:5])}]")
    
    # ── STEP 2: Body text keyword scan ──
    body_hits = count_keyword_hits(body_text_lem, body_building_keywords)
    
    if len(body_hits) >= 5:
        score += 10
        reasons.append(f"BODY_DENSE[{len(body_hits)} hits]")
    elif len(body_hits) >= 3:
        score += 6
        reasons.append(f"BODY_MODERATE[{len(body_hits)} hits]")
    elif len(body_hits) >= 1:
        score += 3
        reasons.append(f"BODY_SPARSE[{len(body_hits)} hits]")
    
    # ── STEP 3: Strong non-building check ──
    raw_combined = f"{site_name} {brief_desc_raw} {ouv_raw}".lower()
    exclusion_hits = count_keyword_hits(raw_combined, strong_non_building_indicators)
    
    if exclusion_hits:
        exclusions = exclusion_hits
        # Only penalize if there are truly ZERO building signals in body text
        if len(body_hits) == 0 and len(title_hits_combined) == 0:
            score -= 8 * len(exclusion_hits)
            reasons.append(f"EXCLUSION[{', '.join(exclusion_hits[:3])}]")
        elif score <= 3:
            # Mild penalty — the site has some building signals but also exclusion terms
            score -= 2
            reasons.append(f"MILD_EXCLUSION[{', '.join(exclusion_hits[:3])}]")
    
    # ── STEP 4: Special override for obvious built structures ──
    # Even if exclusions fired, some site names are unambiguously buildings
    unambiguous_building_words = [
        'cathedral', 'church', 'mosque', 'temple', 'palace', 'castle', 'fortress',
        'fort', 'bridge', 'aqueduct', 'basilica', 'abbey', 'monastery', 'convent',
        'pyramid', 'mausoleum', 'tomb', 'villa', 'amphitheatre', 'amphitheater',
        'tower', 'lighthouse', 'factory', 'mill', 'ironworks', 'railway', 'station',
        'house', 'hospital', 'university', 'library', 'madrasa', 'seminary',
        'stupa', 'pagoda', 'shrine', 'citadel', 'alcazar', 'kremlin',
        'diaolou', 'tulou', 'trulli', 'caravanserai',
        'historic centre', 'historic center', 'old town', 'old city',
        'ancient city', 'medieval city', 'walled city',
        'town hall', 'fortified', 'fortification', 'fortifications',
    ]
    for ub in unambiguous_building_words:
        if has_keyword(site_name.lower(), ub):
            score = max(score, 12)  # Override to at least HIGH
            if f"OVERRIDE[{ub}]" not in reasons:
                reasons.append(f"OVERRIDE[{ub}]")
    
    # ── STEP 5: Rescue check for sparse sites ──
    # If score is still 0 or low, scan the raw brief_description directly
    # (some sites have no OUV and minimal lemmatized text)
    if score <= 0:
        raw_desc_hits = count_keyword_hits(brief_desc_raw.lower(), body_building_keywords)
        raw_name_hits = count_keyword_hits(site_name.lower(), body_building_keywords)
        rescue_hits = list(set(raw_desc_hits + raw_name_hits))
        if len(rescue_hits) >= 2:
            score += 4
            reasons.append(f"RESCUE_DESC[{len(rescue_hits)} raw hits]")
        elif len(rescue_hits) >= 1:
            score += 2
            reasons.append(f"RESCUE_DESC_WEAK[{len(rescue_hits)} raw hit]")
    
    # ── FINAL DECISION ──
    if score >= 10:
        confidence = 'HIGH'
    elif score >= 5:
        confidence = 'MEDIUM'
    elif score >= 2:
        confidence = 'LOW'
    else:
        confidence = 'NONE'
    
    is_built = score >= 2  # Lower threshold to catch edge cases
    
    return is_built, confidence, score, reasons, exclusions, title_hits_combined, body_hits

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    input_file = 'all_1273_sites_input.csv'
    output_dir = '30_july_output'
    
    print("=" * 70)
    print("🏛️  UNESCO Cultural Sites — Built Monument Classifier v3")
    print("=" * 70)
    
    df_all = pd.read_csv(input_file)
    print(f"Loaded {len(df_all)} total sites.")
    
    # Filter to Cultural only
    df = df_all[df_all['category'] == 'Cultural'].copy().reset_index(drop=True)
    print(f"Filtered to {len(df)} Cultural sites.\n")
    
    # Also load the full OUV data from the scraped file
    try:
        df_full_ouv = pd.read_csv('data/unesco_world_heritage_sites.csv')
        df_full_ouv['clean_id'] = df_full_ouv['unesco_id'].astype(str).str.replace('.0', '', regex=False)
        ouv_dict = dict(zip(df_full_ouv['clean_id'], df_full_ouv['ouv_statement']))
        print(f"Loaded full OUV data for {len(ouv_dict)} sites.")
    except:
        ouv_dict = {}
    
    # Prepare text for lemmatization
    site_names = []
    body_texts = []
    brief_descs_raw = []
    ouv_stmts_raw = []
    
    for idx, row in df.iterrows():
        sn = str(row.get('site_name', '')).strip()
        bd = str(row.get('brief_description', '')).strip()
        
        # Try to get full OUV from scraped data
        clean_id = str(row.get('unesco_id', '')).replace('.0', '')
        ouv = str(ouv_dict.get(clean_id, row.get('ouv_statement', ''))).strip()
        if ouv == 'nan':
            ouv = ''
        
        site_names.append(sn)
        brief_descs_raw.append(bd)
        ouv_stmts_raw.append(ouv)
        body_texts.append(f"{sn}. {bd} {ouv}")
    
    # Batch lemmatize
    print("Lemmatizing site names...")
    site_names_lem = batch_lemmatize(site_names)
    print("Lemmatizing body texts...")
    body_texts_lem = batch_lemmatize(body_texts)
    
    # Classify each site
    print("\n🔍 Classifying all sites...")
    results = []
    for idx in tqdm(range(len(df)), desc="Classifying"):
        row = df.iloc[idx]
        is_built, confidence, score, reasons, exclusions, title_hits, body_hits = classify_site(
            site_names[idx], site_names_lem[idx], body_texts_lem[idx],
            brief_descs_raw[idx], ouv_stmts_raw[idx]
        )
        results.append({
            'is_built_monument': is_built,
            'bm_confidence': confidence,
            'bm_score': score,
            'bm_reasons': '; '.join(reasons),
            'bm_exclusions': '; '.join(exclusions),
            'bm_title_hits': '; '.join(title_hits),
            'bm_body_hits_count': len(body_hits),
        })
    
    results_df = pd.DataFrame(results)
    df_classified = pd.concat([df.reset_index(drop=True), results_df], axis=1)
    
    # Split into built and non-built
    built_df = df_classified[df_classified['is_built_monument'] == True].copy()
    non_built_df = df_classified[df_classified['is_built_monument'] == False].copy()
    
    # Patch OUV statements to full versions
    for target_df in [built_df, non_built_df]:
        target_df['clean_id'] = target_df['unesco_id'].astype(str).str.replace('.0', '', regex=False)
        for idx, row in target_df.iterrows():
            cid = row['clean_id']
            if cid in ouv_dict and str(ouv_dict[cid]).strip() not in ['', 'nan']:
                target_df.at[idx, 'ouv_statement'] = ouv_dict[cid]
        target_df.drop(columns=['clean_id'], inplace=True)
    
    # Sort by score
    built_df = built_df.sort_values('bm_score', ascending=False)
    non_built_df = non_built_df.sort_values('bm_score', ascending=False)
    
    # Save
    os.makedirs(output_dir, exist_ok=True)
    built_path = os.path.join(output_dir, f'{len(built_df)}_built_monuments.csv')
    non_built_path = os.path.join(output_dir, f'{len(non_built_df)}_non_building_sites.csv')
    
    # Remove old files
    for f in os.listdir(output_dir):
        if f.endswith('_built_monuments.csv') or f.endswith('_non_building_sites.csv'):
            if f.endswith('_general_building_monuments.csv'):
                continue
            os.remove(os.path.join(output_dir, f))
    
    built_df.to_csv(built_path, index=False)
    non_built_df.to_csv(non_built_path, index=False)
    
    # Report
    print("\n" + "=" * 70)
    print("📊 CLASSIFICATION RESULTS")
    print("=" * 70)
    print(f"Total Cultural Sites:        {len(df)}")
    print(f"Built Monuments:             {len(built_df)}")
    print(f"  - HIGH confidence:         {len(built_df[built_df['bm_confidence'] == 'HIGH'])}")
    print(f"  - MEDIUM confidence:       {len(built_df[built_df['bm_confidence'] == 'MEDIUM'])}")
    print(f"  - LOW confidence:          {len(built_df[built_df['bm_confidence'] == 'LOW'])}")
    print(f"Non-Building Sites:          {len(non_built_df)}")
    print(f"  - NONE confidence:         {len(non_built_df[non_built_df['bm_confidence'] == 'NONE'])}")
    print("-" * 70)
    print(f"Saved: {built_path}")
    print(f"Saved: {non_built_path}")
    print("=" * 70)
    
    # Show all non-building sites for review
    print("\n🌿 NON-BUILDING SITES:")
    for _, r in non_built_df.iterrows():
        exc = f" [EXCL: {r['bm_exclusions']}]" if r['bm_exclusions'] else ""
        print(f"  {r['unesco_id']} | {r['site_name']}{exc}")

if __name__ == '__main__':
    main()
