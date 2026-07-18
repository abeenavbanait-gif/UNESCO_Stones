import pandas as pd
import json
import os
import streamlit as st

DATA_PATH = "Imp Data/built_monument_sites.csv"
NOTES_PATH = "Imp Data/user_notes.json"
MANUAL_DATA_PATH = "Imp Data/UNESCO_Stones_Manual_Data.csv"

def load_monument_data(filepath=DATA_PATH):
    """Load the master CSV data."""
    try:
        df = pd.read_csv(filepath)
        # Ensure unesco_id is string for consistent mapping
        df['unesco_id'] = df['unesco_id'].astype(str)
        return df
    except Exception as e:
        st.error(f"Failed to load data from {DATA_PATH}: {e}")
        return pd.DataFrame()

def get_global_stats(filepath='Imp Data/unesco_whs_master_database.csv'):
    """Calculate macro statistics dynamically from the master CSV datasets."""
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
    if df.empty:
        return False
        
    try:
        safe_unesco_id = str(unesco_id).replace('.0', '')
        df['safe_id'] = df['Site ID'].astype(str).str.replace('.0', '', regex=False)
        idx = df[df['safe_id'] == safe_unesco_id].index
        if len(idx) > 0:
            for key, val in form_data.items():
                # Dynamically add new columns if they don't exist yet (e.g., for new Reference tracking fields)
                if key not in df.columns:
                    df[key] = ""
                    
                if df[key].dtype == 'float64':
                    df[key] = df[key].astype(object)
                df.loc[idx, key] = val
            df.drop(columns=['safe_id'], errors='ignore', inplace=True)
            df.to_csv(MANUAL_DATA_PATH, index=False)
            return True
    except Exception as e:
        st.error(f"Save manual data error: {e}")
    return False

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
