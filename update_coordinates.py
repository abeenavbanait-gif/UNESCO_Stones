import pandas as pd

excel_path = '/Users/rahul_banait/Desktop/Heritage Stones/ops 3.0/whc-sites-2025.xlsx'

print("Loading reference coordinates from Excel...")
ref_df = pd.read_excel(excel_path)

# Ensure ID is a string for mapping
ref_df['id_no'] = ref_df['id_no'].astype(str)

# Create mapping dictionary
lat_map = dict(zip(ref_df['id_no'], ref_df['latitude']))
lon_map = dict(zip(ref_df['id_no'], ref_df['longitude']))

files_to_update = [
    'Imp Data/unesco_cultural_sites.csv',
    'Imp Data/cultural_sites_classified.csv',
    'Imp Data/built_monument_sites.csv'
]

for file in files_to_update:
    try:
        print(f"Updating {file}...")
        df = pd.read_csv(file)
        df['unesco_id'] = df['unesco_id'].astype(str)
        
        # Keep track of old vs new for logging
        old_lats = df['latitude'].copy()
        
        df['latitude'] = df['unesco_id'].map(lat_map).fillna(df['latitude'])
        df['longitude'] = df['unesco_id'].map(lon_map).fillna(df['longitude'])
        
        changed = (old_lats != df['latitude']).sum()
        print(f"  -> {changed} coordinates updated in {file}.")
        
        df.to_csv(file, index=False)
    except Exception as e:
        print(f"Error processing {file}: {e}")

print("Update complete!")
