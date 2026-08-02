import streamlit as st

st.markdown("Select me and drag me to the text area below.")
st.text_area("Drop here")

st.markdown("""
<div style="padding: 20px; background: white;">
    Select this HTML text and drag it.
</div>
""", unsafe_allow_html=True)
