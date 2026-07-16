import pandas as pd
import json
import os
import streamlit as st

DATA_PATH = "Imp Data/built_monument_sites.csv"
NOTES_PATH = "Imp Data/user_notes.json"

@st.cache_data
def load_monument_data():
    """Load the master CSV data. Cached for performance."""
    try:
        df = pd.read_csv(DATA_PATH)
        # Ensure unesco_id is string for consistent mapping
        df['unesco_id'] = df['unesco_id'].astype(str)
        return df
    except Exception as e:
        st.error(f"Failed to load data from {DATA_PATH}: {e}")
        return pd.DataFrame()

@st.cache_data
def get_global_stats():
    """Calculate macro statistics dynamically from the master CSV datasets."""
    stats = {}
    try:
        # Load master CSV database
        master_df = pd.read_csv('Imp Data/unesco_whs_master_database.csv')
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
