import streamlit as st
import time

if 'db' not in st.session_state:
    st.session_state.db = {"Field": "Initial"}

st.write("DB Value:", st.session_state.db["Field"])

# Simulate loading from DB at the top
loaded_val = st.session_state.db["Field"]

val = st.text_input("Edit Field", value=loaded_val, key="my_field")

if st.button("Save"):
    # Wait, what if we use the session state value directly?
    st.session_state.db["Field"] = val
    st.write(f"Saved: {val}")
