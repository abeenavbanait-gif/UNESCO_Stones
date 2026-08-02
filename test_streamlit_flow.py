from data_manager import save_live_data_field, get_live_data_for_site

unesco_id = "252"
field_key = "Architecture Type"
ref_key = f"ref_{field_key}_{unesco_id}"
s_name = "Taj Mahal"
s_country = "India"

# Simulate user changing selectbox to "External"
# Streamlit updates session_state and calls on_change
import streamlit as st
st.session_state = {}
st.session_state[ref_key] = "External"

# callback fires
def save_field_callback(unesco_id, site_name, country, field_key, widget_key, is_list=False):
    val = st.session_state[widget_key]
    save_live_data_field(unesco_id, site_name, country, field_key, val)

save_field_callback(unesco_id, s_name, s_country, f"{field_key}_Ref", ref_key, False)

# App reruns, gets DB data
manual_data = get_live_data_for_site(unesco_id)
print("DB Data for Ref:", manual_data.get(f"{field_key}_Ref"))
