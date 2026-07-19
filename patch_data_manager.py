import os

with open("data_manager.py", "r") as f:
    content = f.read()

# Replace the MANUAL_DATA_PATH definition
content = content.replace(
    'MANUAL_DATA_PATH = "Imp Data/UNESCO_Stones_Manual_Data.csv"',
    'MANUAL_DATA_PATH = "Imp Data/UNESCO_Stones_Manual_Data.csv"\nLIVE_DATA_PATH = "Imp Data/Live_Manual_Data.csv"'
)

# New save_live_data and get_live_data_for_site functions
new_functions = """
def load_live_data():
    if not os.path.exists(LIVE_DATA_PATH):
        # Create empty template
        base_fields = [
            'Architecture Type', 'Construction Period', 'Civilization', 'UNESCO Criteria',
            'Mentioned Major Stone(s)', 'Rock Class', 'Secondary Stone', 'Local Stone Name', 'Lithology',
            'Geological Age', 'Formation', 'Colour', 'Texture', 'Minerals',
            'Quarry', 'Quarry Country', 'Local vs Imported', 'Transport Distance',
            'Structural Use', 'Decorative Use', 'Masonry Technique',
            'Weathering', 'Replacement Stone', 'Restoration', 'Condition'
        ]
        cols = ['Site ID', 'Site Name', 'Country']
        for bf in base_fields:
            cols.extend([bf, f"{bf}_Ref", f"{bf}_Ext"])
        cols.extend(['UNESCO Mention', 'Other references'])
        
        df = pd.DataFrame(columns=cols)
        os.makedirs(os.path.dirname(LIVE_DATA_PATH), exist_ok=True)
        df.to_csv(LIVE_DATA_PATH, index=False)
        return df
    return pd.read_csv(LIVE_DATA_PATH)

def get_live_data_for_site(unesco_id):
    df = load_live_data()
    safe_unesco_id = str(unesco_id).replace('.0', '')
    if not df.empty and 'Site ID' in df.columns:
        df['safe_id'] = df['Site ID'].astype(str).str.replace('.0', '', regex=False)
        row = df[df['safe_id'] == safe_unesco_id]
        if not row.empty:
            # Get the LAST entry in case of duplicates (chronological append)
            return row.iloc[-1].fillna("").to_dict()
    return {}

def save_live_data_field(unesco_id, site_name, country, field_key, field_value):
    df = load_live_data()
    safe_unesco_id = str(unesco_id).replace('.0', '')
    
    # Check if the site already exists in the CSV
    df['safe_id'] = df['Site ID'].astype(str).str.replace('.0', '', regex=False)
    idx = df[df['safe_id'] == safe_unesco_id].index
    
    if len(idx) > 0:
        # Update existing row (the most recent one)
        target_idx = idx[-1]
        
        # Ensure column exists
        if field_key not in df.columns:
            df[field_key] = ""
            
        if df[field_key].dtype == 'float64':
            df[field_key] = df[field_key].astype(object)
            
        df.loc[target_idx, field_key] = field_value
    else:
        # Append as a completely new row
        new_row = {
            "Site ID": safe_unesco_id,
            "Site Name": site_name,
            "Country": country,
            field_key: field_value
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
    df.drop(columns=['safe_id'], errors='ignore', inplace=True)
    df.to_csv(LIVE_DATA_PATH, index=False)
    return True
"""

# Append the new functions right before UPLOADED_DOCS_DIR
content = content.replace('UPLOADED_DOCS_DIR = "Imp Data/uploaded_docs"', new_functions + '\nUPLOADED_DOCS_DIR = "Imp Data/uploaded_docs"')

# Update exports at the top (not strictly necessary but good practice, it's not exported there actually)

with open("data_manager.py", "w") as f:
    f.write(content)
