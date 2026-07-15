import pandas as pd
import json
import os
import streamlit as st

DATA_PATH = "Imp Data/906-sites_built_monument_sites.csv"
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
