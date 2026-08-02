import pandas as pd
import os

manual_path = "Live_Manual_Data_Backup (39).csv"
master_path = "Imp Data/989-sites_cultural_sites_classified.csv"
output_path = "Imp Data/Live_Manual_Data_Backup_Upgraded.csv"

print(f"Loading {manual_path}...")
df_manual = pd.read_csv(manual_path)

print(f"Loading {master_path}...")
df_master = pd.read_csv(master_path)

# Ensure ID columns are strings to match
df_manual['Site ID'] = df_manual['Site ID'].astype(str).str.replace('.0', '', regex=False)
df_master['unesco_id'] = df_master['unesco_id'].astype(str)

existing_ids = set(df_manual['Site ID'].tolist())
new_sites = []

for _, row in df_master.iterrows():
    site_id = row['unesco_id']
    if site_id not in existing_ids:
        # Create an empty row with just ID, Name, Country
        new_row = {col: "" for col in df_manual.columns}
        new_row['Site ID'] = site_id
        new_row['Site Name'] = row.get('site_name', '')
        new_row['Country'] = row.get('country', '')
        new_sites.append(new_row)

if new_sites:
    df_new = pd.DataFrame(new_sites)
    df_upgraded = pd.concat([df_manual, df_new], ignore_index=True)
    df_upgraded.to_csv(output_path, index=False)
    print(f"Appended {len(new_sites)} new sites.")
    print(f"Saved upgraded manual data to {output_path}")
else:
    print("No missing sites found. Saving copy just in case.")
    df_manual.to_csv(output_path, index=False)
