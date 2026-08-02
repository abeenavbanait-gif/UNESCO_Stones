import pandas as pd
import numpy as np

# 1. Update rescanned_built_geological_monuments.csv with coordinates from whc-sites-2025.xlsx
print("Updating coordinates...")
df_built = pd.read_csv("out_data_July_29/rescanned_built_geological_monuments.csv")
df_excel = pd.read_excel("whc-sites-2025.xlsx")

# Ensure IDs are strings for clean merge
df_built['unesco_id'] = df_built['unesco_id'].astype(str).str.replace('.0', '', regex=False)
df_excel['id_no'] = df_excel['id_no'].astype(str).str.replace('.0', '', regex=False)

# Map coordinates
coord_map = df_excel.set_index('id_no')[['latitude', 'longitude']].to_dict(orient='index')

def get_lat(uid):
    return coord_map.get(str(uid), {}).get('latitude', np.nan)
    
def get_lon(uid):
    return coord_map.get(str(uid), {}).get('longitude', np.nan)

df_built['latitude'] = df_built['unesco_id'].apply(get_lat)
df_built['longitude'] = df_built['unesco_id'].apply(get_lon)

# Save it to both places
df_built.to_csv("out_data_July_29/rescanned_built_geological_monuments.csv", index=False)
df_built.to_csv("re-scan/rescanned_built_geological_monuments.csv", index=False)

# 2. Extract Stone Mentions CSV
print("Extracting stone mentions...")
stone_records = []
for _, row in df_built.iterrows():
    uid = row['unesco_id']
    name = row['site_name']
    stones = []
    
    if pd.notna(row['stone_types_found_v2']):
        for s in str(row['stone_types_found_v2']).split(';'):
            if s.strip() and s.strip() != 'N/A':
                stones.append(s.strip().title())
                
    if pd.notna(row['named_trade_stones_v2']):
        for s in str(row['named_trade_stones_v2']).split(';'):
            if s.strip() and s.strip() != 'N/A':
                stones.append(s.strip().title())
                
    stones = list(set(stones))
    for s in stones:
        stone_records.append({'unesco_id': uid, 'site_name': name, 'stone_mention': s})

df_stones = pd.DataFrame(stone_records)
df_stones.to_csv("out_data_July_29/extracted_stone_mentions.csv", index=False)
print(f"Extracted {len(df_stones)} stone mentions across {df_stones['unesco_id'].nunique()} sites.")
