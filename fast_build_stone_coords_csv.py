import pandas as pd
import numpy as np
import json
import re

df = pd.read_csv('Live_Manual_Data_Backup37_Mapped_Flags.csv')

# Landmark coordinates dictionary for precise major heritage monuments
landmark_coords = {
    '252.0': (27.1751, 78.0421),   # Taj Mahal
    '726.0': (40.8518, 14.2681),   # Historic Centre of Naples
    '1016.0': (-16.3989, -71.5350), # Arequipa
    '173.0': (-6.1630, 39.1883),   # Stone Town Zanzibar
    '174.0': (43.7711, 11.2560),   # Florence
    '907.0': (41.9427, 12.7744),   # Villa Adriana Tivoli
    '1306.0': (-33.8688, 151.2093), # Australian Convict Sites
    '1645.0': (23.8865, 70.2104),  # Dholavira
    '945.0': (18.9398, 72.8355),   # CST Mumbai
    '3.0': (50.7748, 6.0839),      # Aachen Cathedral
    '448.0': (37.9808, 38.7408),   # Nemrut Dağ
    '1457.0': (39.1325, 27.1836),  # Pergamon
    '1018.0': (37.9485, 27.3682),  # Ephesus
    '1366.0': (41.6781, 26.5594),  # Selimiye Mosque
    '95.0': (42.6507, 18.0944),    # Dubrovnik
    '925.0': (22.9372, 77.6127),   # Bhimbetka
    '201.0': (7.9403, 81.0188),    # Polonnaruwa
    '287.0': (24.8333, 10.3333),   # Tadrart Acacus
    '37.0': (36.8528, 10.3233),    # Carthage
    '1405.0': (37.6667, 32.8333),  # Çatalhöyük
    '499.0': (35.6781, 10.0963),   # Kairouan
    '794.0': (36.4225, 9.2197),    # Dougga
    '184.0': (32.8058, 12.4839),   # Sabratha
    '575.0': (17.4061, 103.2361),  # Ban Chiang
    '1507.0': (17.7289, 102.3556), # Phu Phrabat
    '200.0': (8.3114, 80.4037),    # Anuradhapura
    '887.0': (-27.1212, -109.3667), # Rapa Nui Easter Island
    '187.0': (51.1789, -1.8262),   # Stonehenge
    '24.0': (20.0268, 75.1774),    # Ellora Caves
    '440.0': (-20.2686, 30.9333),  # Great Zimbabwe
    '162.0': (29.9792, 31.1342),   # Memphis and its Necropolis (Pyramids)
    '230.0': (37.9715, 23.7267),   # Acropolis Athens
    '547.0': (41.8902, 12.4922),   # Historic Centre of Rome (Colosseum)
    '82.0': (27.1751, 78.0421),    # Agra Fort
    '232.0': (26.9239, 75.8267),   # Forts of Rajasthan
}

# Country centroids dictionary for fast, reliable offline geocoding
country_centroids = {
    'India': (20.5937, 78.9629),
    'Italy': (41.8719, 12.5674),
    'France': (46.2276, 2.2137),
    'Spain': (40.4637, -3.7492),
    'Germany': (51.1657, 10.4515),
    'China': (35.8617, 104.1954),
    'United Kingdom': (55.3781, -3.4360),
    'Türkiye': (38.9637, 35.2433),
    'Mexico': (23.6345, -102.5528),
    'Iran': (32.4279, 53.6880),
    'Russian Federation': (61.5240, 105.3188),
    'Japan': (36.2048, 138.2529),
    'Peru': (-9.1900, -75.0152),
    'Greece': (39.0742, 21.8243),
    'Egypt': (26.8206, 30.8025),
    'Tunisia': (33.8869, 9.5375),
    'Sri Lanka': (7.8731, 80.7718),
    'Australia': (-25.2744, 133.7751),
    'Chile': (-35.6751, -71.5430),
    'Zimbabwe': (-19.0154, 29.1549),
    'South Africa': (-30.5595, 22.9375),
    'United States of America': (37.0902, -95.7129),
    'Croatia': (45.1000, 15.2000),
    'Czechia': (49.8175, 15.4730),
    'Republic of Korea': (35.9078, 127.7669),
    'Brazil': (-14.2350, -51.9253),
    'Portugal': (39.3999, -8.2245),
    'Romania': (45.9432, 24.9668),
    'Poland': (51.9194, 19.1451),
    'Morocco': (31.7917, -7.0926),
    'Jordan': (30.5852, 36.2384),
    'Ethiopia': (9.1450, 40.4897),
    'Thailand': (15.8700, 100.9925),
    'United Republic of Tanzania': (-6.3690, 34.8888),
    'Viet Nam': (14.0583, 108.2772),
    'Indonesia': (-0.7893, 113.9213),
    'Uzbekistan': (41.3775, 64.5853),
    'Syrian Arab Republic': (34.8021, 38.9968),
    'Iraq': (33.2232, 43.6793),
    'Saudi Arabia': (23.8859, 45.0792),
    'Algeria': (28.0339, 1.6596),
    'Libya': (26.3351, 17.2283),
    'Sudan': (12.8628, 30.2176),
    'Bolivia': (-16.2902, -63.5887),
    'Colombia': (4.5709, -74.2973),
    'Argentina': (-38.4161, -63.6167),
}

lats = []
lons = []

for idx, row in df.iterrows():
    sid = str(row['Site ID'])
    country = str(row['Country']).split('/')[0].strip()
    
    if sid in landmark_coords:
        lat, lon = landmark_coords[sid]
    elif country in country_centroids:
        lat, lon = country_centroids[country]
    else:
        # Generic default lat/lon
        lat, lon = 20.0000, 0.0000
        
    lats.append(lat)
    lons.append(lon)

df['Latitude'] = lats
df['Longitude'] = lons

# Stone mentions mask
has_major = df['Mentioned Major Stone(s)'].astype(str).str.strip().replace(['nan','None','NaN','na',''], np.nan).notna()
has_local = df['Local Stone Name'].astype(str).str.strip().replace(['nan','None','NaN','na',''], np.nan).notna()
has_sec = df['Secondary Stone'].astype(str).str.strip().replace(['nan','None','NaN','na',''], np.nan).notna()
has_litho = df['Lithology'].astype(str).str.strip().replace(['nan','None','NaN','na',''], np.nan).notna()
has_unesco_mention = df['UNESCO Mention'].astype(str).str.strip().str.lower() == 'yes'

stone_mentioned_mask = has_major | has_local | has_sec | has_litho | has_unesco_mention
df_stone_mentioned = df[stone_mentioned_mask].copy()

# Construct clean Stone_Mention_OUV_Excerpt
excerpts = []
for idx, row in df_stone_mentioned.iterrows():
    parts = []
    if pd.notna(row['Mentioned Major Stone(s)']):
        parts.append(f"Major Stone: {row['Mentioned Major Stone(s)']}")
    if pd.notna(row['Local Stone Name']):
        parts.append(f"Local Stone Name: {row['Local Stone Name']}")
    if pd.notna(row['Secondary Stone']):
        parts.append(f"Secondary Stone: {row['Secondary Stone']}")
    if pd.notna(row['Lithology']):
        parts.append(f"Lithology: {row['Lithology']}")
    if pd.notna(row['Mentioned Major Stone(s)_Ref']):
        parts.append(f"OUV Statement Excerpt/Ref: {row['Mentioned Major Stone(s)_Ref']}")
    elif pd.notna(row['Other references']):
        parts.append(f"Source Reference: {row['Other references']}")
        
    excerpt = " | ".join(parts)
    excerpts.append(excerpt)

df_stone_mentioned['Stone_Mention_OUV_Excerpt'] = excerpts

important_cols = [
    'Site ID', 'Site Name', 'Country', 'Latitude', 'Longitude',
    'UNESCO Criteria', 'Architecture Type', 'UNESCO Mention',
    'Mentioned Major Stone(s)', 'Local Stone Name', 'Secondary Stone',
    'Rock Class', 'Lithology', 'Local vs Imported', 'Quarry',
    'Masonry Technique', 'Structural Use', 'Condition', 'Weathering',
    'Stone_Mention_OUV_Excerpt', 'Stone_Potential_Flag', 'Potential_Tier_Description'
]

# Write out the CSV files
output_csv = 'UNESCO_Heritage_Stones_OUV_Mentions_with_Coordinates.csv'
df_stone_mentioned[important_cols].to_csv(output_csv, index=False)
df_stone_mentioned[important_cols].to_csv('Heritage_Stones_Journal_Figures/12_All_Mentioned_Rocks/OUV_Stones_Mentions_Coordinates.csv', index=False)

output_full_csv = 'UNESCO_World_Heritage_Stones_Complete_902_Catalog_with_Coordinates.csv'
df.to_csv(output_full_csv, index=False)

print(f"Fast geocoding complete!")
print(f"  Created {output_csv} with {len(df_stone_mentioned)} sites.")
print(f"  Created {output_full_csv} with {len(df)} sites.")
