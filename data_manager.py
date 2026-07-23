import pandas as pd
import json
import os
import streamlit as st

DATA_PATH = "Imp Data/built_monument_sites.csv"
NOTES_PATH = "Imp Data/user_notes.json"
MANUAL_DATA_PATH = "Imp Data/UNESCO_Stones_Manual_Data.csv"
LIVE_DATA_PATH = "Imp Data/Live_Manual_Data.csv"

@st.cache_data(show_spinner=False)
def load_monument_data(filepath=DATA_PATH):
    """Load the master CSV data with caching."""
    try:
        df = pd.read_csv(filepath)
        # Ensure unesco_id is string for consistent mapping
        df['unesco_id'] = df['unesco_id'].astype(str)
        return df
    except Exception as e:
        st.error(f"Failed to load data from {DATA_PATH}: {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def get_global_stats(filepath='Imp Data/unesco_whs_master_database.csv'):
    """Calculate macro statistics dynamically from the master CSV datasets with caching."""
    stats = {}
    try:
        # Load master CSV database
        master_df = pd.read_csv(filepath)
        stats['total_unesco'] = len(master_df)
        stats['cultural'] = len(master_df[master_df['category'] == 'Cultural'])
        stats['natural'] = len(master_df[master_df['category'] == 'Natural'])
        stats['mixed'] = len(master_df[master_df['category'] == 'Mixed'])
        
        # Calculate missing OUV statements for cultural sites
        cultural_df = master_df[master_df['category'] == 'Cultural']
        missing_ouv = cultural_df['ouv_statement'].isna().sum() + (cultural_df['ouv_statement'] == '').sum()
        stats['missing_ouv'] = int(missing_ouv)
    except Exception as e:
        print(f"Error loading dynamic global stats: {e}")
        # Absolute fallback if file is missing
        stats = {
            'total_unesco': 1248, 'cultural': 972, 'natural': 235, 'mixed': 41, 'missing_ouv': 0
        }
    return stats

def load_notes():
    """Load user notes from JSON."""
    if not os.path.exists(NOTES_PATH):
        return {}
    try:
        with open(NOTES_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to load notes: {e}")
        return {}

def save_note(unesco_id, note_text):
    """Save a note for a specific unesco_id."""
    notes = load_notes()
    notes[str(unesco_id)] = note_text
    
    # Ensure directory exists just in case
    os.makedirs(os.path.dirname(NOTES_PATH), exist_ok=True)
    
    try:
        with open(NOTES_PATH, 'w') as f:
            json.dump(notes, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Failed to save note: {e}")
        return False

def load_manual_data():
    """Load the manual data CSV."""
    if not os.path.exists(MANUAL_DATA_PATH):
        return pd.DataFrame()
    return pd.read_csv(MANUAL_DATA_PATH)

def get_manual_data_for_site(unesco_id):
    """Retrieve existing manual data for a specific site so the form can be pre-filled."""
    df = load_manual_data()
    if df.empty:
        return {}
    try:
        safe_unesco_id = str(unesco_id).replace('.0', '')
        df['safe_id'] = df['Site ID'].astype(str).str.replace('.0', '', regex=False)
        row = df[df['safe_id'] == safe_unesco_id]
        if not row.empty:
            return row.iloc[0].fillna("").to_dict()
    except Exception as e:
        pass
    return {}

def save_manual_data(unesco_id, form_data: dict):
    """Save the form inputs back to the CSV."""
    df = load_manual_data()
        
    try:
        safe_unesco_id = str(unesco_id).replace('.0', '')
        
        if df.empty:
            # Create a new DataFrame if empty
            new_row = {"Site ID": safe_unesco_id}
            new_row.update(form_data)
            df = pd.DataFrame([new_row])
        else:
            df['safe_id'] = df['Site ID'].astype(str).str.replace('.0', '', regex=False)
            idx = df[df['safe_id'] == safe_unesco_id].index
            if len(idx) > 0:
                for key, val in form_data.items():
                    # Dynamically add new columns if they don't exist yet
                    if key not in df.columns:
                        df[key] = ""
                        
                    if df[key].dtype == 'float64':
                        df[key] = df[key].astype(object)
                    df.loc[idx, key] = val
            else:
                # Append new row if site not found
                new_row = {"Site ID": safe_unesco_id}
                new_row.update(form_data)
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                
            df.drop(columns=['safe_id'], errors='ignore', inplace=True)
            
        df.to_csv(MANUAL_DATA_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"Save manual data error: {e}")
    return False


def load_live_data():
    """Load live data with session_state in-memory caching for zero disk latency on reruns."""
    if 'live_data_df' in st.session_state and isinstance(st.session_state['live_data_df'], pd.DataFrame):
        return st.session_state['live_data_df']
        
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
    else:
        df = pd.read_csv(LIVE_DATA_PATH)
        
    st.session_state['live_data_df'] = df
    return df

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
    df = load_live_data().copy()
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
    st.session_state['live_data_df'] = df
    df.to_csv(LIVE_DATA_PATH, index=False)
    return True


def get_visited_site_ids(df=None):
    """Return a set of safe site IDs that have at least one user-filled form field."""
    if df is None:
        df = load_live_data()
    if df.empty or 'Site ID' not in df.columns:
        return set()
    meta_cols = ['Site ID', 'Site Name', 'Country', 'safe_id', 'Index', 'UNESCO Criteria']
    data_cols = [c for c in df.columns if c not in meta_cols]
    if not data_cols:
        return set()
    df_work = df.copy()
    df_work['safe_id'] = df_work['Site ID'].astype(str).str.replace('.0', '', regex=False)
    calc_df = df_work[data_cols].copy()
    calc_df = calc_df.replace([r'^\s*$', 'NaN', 'nan', 'None', 'Unknown'], pd.NA, regex=True)
    visited_mask = calc_df.notna().sum(axis=1) > 0
    return set(df_work[visited_mask]['safe_id'].tolist())

def is_site_visited(unesco_id, visited_ids=None):
    """Check if a specific unesco_id has user-filled form data."""
    safe_unesco_id = str(unesco_id).replace('.0', '')
    if visited_ids is not None:
        return safe_unesco_id in visited_ids
    return safe_unesco_id in get_visited_site_ids()



UPLOADED_DOCS_DIR = "Imp Data/uploaded_docs"

def save_site_document(unesco_id, doc_name, uploaded_file):
    """Save an uploaded document to the local database structure for a specific site."""
    site_dir = os.path.join(UPLOADED_DOCS_DIR, str(unesco_id))
    os.makedirs(site_dir, exist_ok=True)
    
    ext = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'pdf'
    safe_name = "".join([c for c in doc_name if c.isalnum() or c in " -_"]).strip()
    if not safe_name: 
        safe_name = "document"
    
    file_path = os.path.join(site_dir, f"{safe_name}.{ext}")
    try:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        return True, file_path
    except Exception as e:
        return False, str(e)

def get_site_documents(unesco_id):
    """Retrieve all uploaded documents for a specific site."""
    site_dir = os.path.join(UPLOADED_DOCS_DIR, str(unesco_id))
    if not os.path.exists(site_dir):
        return []
    
    docs = []
    try:
        for f in os.listdir(site_dir):
            if os.path.isfile(os.path.join(site_dir, f)):
                docs.append({
                    "name": os.path.splitext(f)[0],
                    "file": f,
                    "path": os.path.join(site_dir, f)
                })
    except Exception:
        pass
    return docs
