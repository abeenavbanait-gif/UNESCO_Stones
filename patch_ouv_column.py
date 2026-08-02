import pandas as pd

# Load the target dataset (built monuments)
target_path = 'out_data_July_29/rescanned_built_geological_monuments.csv'
df_target = pd.read_csv(target_path)
print(f"Target length: {len(df_target)}")

# Load the full scraped OUV dataset
full_path = 'data/unesco_world_heritage_sites.csv'
df_full = pd.read_csv(full_path)
print(f"Full data length: {len(df_full)}")

# Clean IDs for precise merging
df_target['clean_id'] = df_target['unesco_id'].astype(str).str.replace('.0', '', regex=False)
df_full['clean_id'] = df_full['unesco_id'].astype(str).str.replace('.0', '', regex=False)

# Map the full OUVs
ouv_dict = dict(zip(df_full['clean_id'], df_full['ouv_statement']))

updated_count = 0
for idx, row in df_target.iterrows():
    cid = row['clean_id']
    if cid in ouv_dict and pd.notna(ouv_dict[cid]) and str(ouv_dict[cid]).strip():
        # Replace the short OUV with the full scraped OUV
        df_target.at[idx, 'ouv_statement'] = ouv_dict[cid]
        updated_count += 1

# Drop the temporary clean_id column
df_target = df_target.drop(columns=['clean_id'])

# Save the updated target CSV
df_target.to_csv(target_path, index=False)
print(f"Successfully updated OUV statements for {updated_count} out of {len(df_target)} sites.")

# Let's check max length now
print("New max OUV length:", df_target['ouv_statement'].str.len().max())
