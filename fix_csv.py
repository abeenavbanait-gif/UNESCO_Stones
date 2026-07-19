import pandas as pd
import json

# Load JSON for all 1223 sites
with open("data/unesco_master_list.json", "r") as f:
    master_data = json.load(f)
master_df = pd.DataFrame(master_data)

# Load current manual data
current_df = pd.read_csv("Imp Data/UNESCO_Stones_Manual_Data.csv")

# Create a new blank template for ALL sites
template_df = pd.DataFrame()
template_df['Index'] = range(1, len(master_df) + 1)
template_df['Site ID'] = master_df['unesco_id']
template_df['Site Name'] = master_df['site_name']
template_df['Country'] = master_df['country']

# Add all columns that exist in the current_df but are missing in template
for col in current_df.columns:
    if col not in template_df.columns:
        template_df[col] = ""

# Now MERGE the existing data from current_df into the new template
current_df['safe_id'] = current_df['Site ID'].astype(str).str.replace('.0', '', regex=False)
template_df['safe_id'] = template_df['Site ID'].astype(str).str.replace('.0', '', regex=False)

# Update rows where safe_id matches
for idx, row in current_df.iterrows():
    match_idx = template_df[template_df['safe_id'] == row['safe_id']].index
    if len(match_idx) > 0:
        for col in current_df.columns:
            if col != 'Index' and col != 'safe_id':
                val = row[col]
                if pd.notna(val) and val != "":
                    template_df.loc[match_idx, col] = val

template_df.drop(columns=['safe_id'], inplace=True)
template_df.to_csv("Imp Data/UNESCO_Stones_Manual_Data.csv", index=False)
print("Updated UNESCO_Stones_Manual_Data.csv with all 1223 sites!")
