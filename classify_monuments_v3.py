import os
import sys
import re
import argparse
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import spacy
    from spacy.matcher import Matcher
    # For v3, we NEED the parser and ner, so we don't disable them.
    # We use en_core_web_sm. If not present, we will fail gracefully.
    nlp = spacy.load("en_core_web_sm")
    print("✅ spaCy ('en_core_web_sm') successfully loaded with full pipeline (Parser & NER).")
except ImportError:
    print("❌ ERROR: spaCy is required for v3 dependency parsing. Please run: pip3 install spacy && python3 -m spacy download en_core_web_sm")
    sys.exit(1)
except OSError:
    print("❌ ERROR: spaCy model 'en_core_web_sm' not found. Please run: python3 -m spacy download en_core_web_sm")
    sys.exit(1)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  V3 DICTIONARIES (UNESCO ARTICLE 1 ALIGNED)                                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

GEO_MATERIALS = [
    # Foundational Basic Terms
    'stone', 'stones', 'rock', 'rocks', 'rock-cut', 'rock cut', 'rockface', 'rock-hewn', 'rock hewn',
    'boulder', 'boulders', 'cobblestone', 'cobblestones', 'cobble', 'cobbles',
    'rubble', 'rubblestone', 'ashlar', 'freestone', 'dimension stone', 'flagstone',
    'megalith', 'megaliths', 'megalithic', 'monolith', 'monolithic',
    'bedrock', 'outcrop',
    
    # Generic Minerals & Geologicals
    'mineral', 'minerals', 'crystal', 'crystals', 'crystalline',
    'gem', 'gems', 'gemstone', 'gemstones', 'precious stone', 'semi-precious stone',
    'ore', 'ores', 'igneous', 'sedimentary', 'sediment', 'sediments',
    'metamorphic', 'metamorphism', 'magma', 'lava', 'volcanic', 'geology', 'geological',
    'earth', 'earthen', 'soil', 'clay', 'sand', 'gravel', 'pebble', 'pebbles',
    'mud', 'mudbrick', 'adobe', 'rammed earth', 'pise', 'wattle and daub',

    # Specific Igneous (from v2)
    'granite', 'diorite', 'gabbro', 'syenite', 'monzonite', 'granodiorite', 'peridotite',
    'basalt', 'andesite', 'rhyolite', 'dacite', 'obsidian', 'pumice', 'scoria', 'trachyte', 'ignimbrite', 'tuff',

    # Specific Sedimentary (from v2)
    'limestone', 'sandstone', 'shale', 'mudstone', 'siltstone', 'conglomerate', 'breccia',
    'dolomite', 'dolostone', 'chalk', 'chert', 'flint', 'alabaster', 'travertine', 'tufa',
    'laterite', 'coquina',

    # Specific Metamorphic (from v2)
    'marble', 'slate', 'schist', 'gneiss', 'quartzite', 'phyllite', 'hornfels', 'amphibolite',
    'skarn', 'serpentinite', 'soapstone', 'steatite'
]

CULTURAL_HERITAGE = [
    # Article 1 Concepts: Monuments / Architecture
    'monument', 'monuments', 'monumental', 'architecture', 'architectural', 
    'sculpture', 'sculptures', 'sculpted', 'statue', 'statues',
    'cave dwelling', 'cave dwellings', 'cave temple', 'cave',
    'building', 'buildings', 'built',
    
    # Structure types
    'temple', 'church', 'mosque', 'cathedral', 'shrine', 'stupa', 'pagoda', 'monastery', 'abbey',
    'tomb', 'mausoleum', 'pyramid', 'necropolis',
    'wall', 'walls', 'fortress', 'fort', 'castle', 'citadel', 'palace',
    'bridge', 'aqueduct', 'amphitheatre', 'theatre',
    
    # Actions/Interventions (Verbs & Nouns)
    'carved', 'carving', 'carve', 'hewn', 'quarried', 'quarry', 'quarrying', 
    'cut', 'masonry', 'mason', 'masons', 'stonemason', 'stonemasonry',
    'construction', 'constructed', 'cladding', 'veneer', 'facing', 'revetment',
    
    # Archaeology / Sites
    'archaeological', 'archaeology', 'ruin', 'ruins', 'settlement', 'city', 'town', 'village',
    'inscription', 'inscriptions', 'petroglyph', 'engraving'
]

# Create lemmatized sets for faster matching
GEO_MAT_SET = set([doc[0].lemma_ for doc in nlp.pipe(GEO_MATERIALS) if len(doc) > 0])
CULT_HER_SET = set([doc[0].lemma_ for doc in nlp.pipe(CULTURAL_HERITAGE) if len(doc) > 0])

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  DEPENDENCY PARSING LOGIC                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def shortest_dependency_path(doc, source_token, target_token):
    """Calculates the shortest path between two tokens in a dependency tree."""
    # Find path to root for source
    source_path = [source_token]
    current = source_token
    while current.head != current:
        current = current.head
        source_path.append(current)
        
    # Find path to root for target
    target_path = [target_token]
    current = target_token
    while current.head != current:
        current = current.head
        target_path.append(current)
        
    # Find lowest common ancestor
    lca = None
    for token in source_path:
        if token in target_path:
            lca = token
            break
            
    if lca is None:
        return float('inf')
        
    # Distance is path from source to LCA + path from target to LCA
    return source_path.index(lca) + target_path.index(lca)

def evaluate_sentence(sent):
    """
    Evaluates a single sentence.
    Returns (confidence, geo_terms, cult_terms)
    confidence: 'HIGH' (linked), 'MEDIUM' (co-occur but not linked), 'LOW' (geo only), 'NONE'
    """
    found_geo = []
    found_cult = []
    
    geo_tokens = []
    cult_tokens = []
    
    # 1. Identify tokens
    for token in sent:
        lemma = token.lemma_.lower()
        if lemma in GEO_MAT_SET:
            found_geo.append(token.text.lower())
            geo_tokens.append(token)
        if lemma in CULT_HER_SET:
            found_cult.append(token.text.lower())
            cult_tokens.append(token)
            
    if not found_geo:
        return 'NONE', [], []
        
    if found_geo and not found_cult:
        return 'LOW', list(set(found_geo)), []
        
    # Both exist. Check dependency path length.
    # If any geo_token is within 3 edges of any cult_token, we consider it HIGH (linked).
    min_dist = float('inf')
    for g_tok in geo_tokens:
        for c_tok in cult_tokens:
            dist = shortest_dependency_path(sent.doc, g_tok, c_tok)
            if dist < min_dist:
                min_dist = dist
                
    if min_dist <= 3:
        return 'HIGH', list(set(found_geo)), list(set(found_cult))
    else:
        return 'MEDIUM', list(set(found_geo)), list(set(found_cult))

def classify_text(text):
    """Processes full text (OUV + Description) and returns best classification."""
    doc = nlp(str(text))
    
    best_conf = 'NONE'
    all_geo = set()
    all_cult = set()
    high_context = []
    med_context = []
    
    conf_rank = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'NONE': 0}
    
    for sent in doc.sents:
        conf, geo, cult = evaluate_sentence(sent)
        if conf != 'NONE':
            all_geo.update(geo)
            all_cult.update(cult)
            
            if conf == 'HIGH':
                high_context.append(sent.text.strip())
            elif conf == 'MEDIUM':
                med_context.append(sent.text.strip())
                
            if conf_rank[conf] > conf_rank[best_conf]:
                best_conf = conf
                
    # Choose context to return
    if high_context:
        context = " | ".join(high_context)
    elif med_context:
        context = " | ".join(med_context)
    else:
        context = ""
        
    return {
        'confidence_v3': best_conf,
        'geo_materials_found': "; ".join(all_geo),
        'cultural_concepts_found': "; ".join(all_cult),
        'match_context': context
    }

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  MAIN EXECUTION                                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def main():
    parser = argparse.ArgumentParser(description="Robust NLP Classification for Built Monuments (v3).")
    parser.add_argument('--input', type=str, default='all_1273_sites_input.csv', help='Input CSV')
    parser.add_argument('--output', type=str, default='v3_classified_sites.csv', help='Output CSV file')
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    print(f"==========================================================")
    print(f"🏛️ UNESCO Heritage Sites - NLP Classification v3 (Robust) 🏛️")
    print(f"==========================================================")
    print(f"Input file:  {input_file}")
    print(f"Output file: {output_file}")
    print(f"----------------------------------------------------------")

    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} sites.\nProcessing via spaCy (Dependency Parsing)...")

    results = []
    # Using tqdm for progress bar
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Classifying sites"):
        site_name = str(row.get('site_name', row.get('name', ''))).strip()
        ouv = str(row.get('ouv_statement', '')).strip()
        desc = str(row.get('brief_description', '')).strip()
        
        full_text = f"{site_name}. {desc} {ouv}"
        
        # If no text, mark NONE
        if len(full_text.strip()) < 5:
            res = {
                'confidence_v3': 'NONE',
                'geo_materials_found': '',
                'cultural_concepts_found': '',
                'match_context': ''
            }
        else:
            res = classify_text(full_text)
            
        results.append(res)
        
    res_df = pd.DataFrame(results)
    
    # Merge with original
    final_df = pd.concat([df, res_df], axis=1)
    
    final_df.to_csv(output_file, index=False)
    
    print(f"\n==========================================================")
    print(f"📊 NLP v3 RESCAN COMPLETE")
    print(f"==========================================================")
    print(f"Total Sites Analyzed: {len(final_df)}")
    print(f"HIGH Confidence:      {len(final_df[final_df['confidence_v3'] == 'HIGH'])} (Strong Grammatical Link)")
    print(f"MEDIUM Confidence:    {len(final_df[final_df['confidence_v3'] == 'MEDIUM'])} (Co-occurrence)")
    print(f"LOW Confidence:       {len(final_df[final_df['confidence_v3'] == 'LOW'])} (Geo Material Only)")
    print(f"NONE:                 {len(final_df[final_df['confidence_v3'] == 'NONE'])}")
    print(f"Saved to:             {output_file}")

if __name__ == '__main__':
    main()
