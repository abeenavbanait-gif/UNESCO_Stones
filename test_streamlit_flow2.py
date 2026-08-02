import pandas as pd
from data_manager import save_live_data_field, get_live_data_for_site

unesco_id = "252"
field_key = "Architecture Type"
ref_key = f"ref_{field_key}_{unesco_id}"

# 1. Clear DB and save a reference
df = pd.read_csv("Imp Data/Live_Manual_Data_backup.csv")
df.to_csv("Imp Data/Live_Manual_Data.csv", index=False)

save_live_data_field("252", "Taj Mahal", "India", "Architecture Type_Ref", "Internal (DS/OUV)")

# 2. Simulate page reload (empty session state)
import streamlit as st
st.session_state = {}

manual_data = get_live_data_for_site(unesco_id)

db_ref = str(manual_data.get(f"{field_key}_Ref", ""))
st.session_state[ref_key] = db_ref if db_ref in ["", "Internal (DS/OUV)", "External"] else ""

print("Session state after reload:", st.session_state)

