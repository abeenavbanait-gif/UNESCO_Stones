with open("app.py", "r") as f:
    content = f.read()

download_ui = """    st.markdown("---")
    st.subheader("💾 Export & View Manual Data")
    st.markdown("Download the full manual data you have entered so far for safekeeping to ensure you never lose your progress on the cloud.")
    try:
        import pandas as pd
        live_db = pd.read_csv("Imp Data/Live_Manual_Data.csv")
        csv_data = live_db.to_csv(index=False).encode('utf-8')
        col1, col2 = st.columns([1, 3])
        with col1:
            st.download_button(
                label="⬇️ Download Live CSV Backup",
                data=csv_data,
                file_name="Live_Manual_Data_Backup.csv",
                mime="text/csv",
                type="primary"
            )
        with st.expander("👀 View Current Data Table (All Filled Sites)"):
            st.dataframe(live_db, use_container_width=True)
    except FileNotFoundError:
        st.info("No manual data has been saved yet. Start filling out the Manual Data Entry Form to see it here!")
    
    st.markdown("---")"""

content = content.replace(
    '    st.markdown("---")\n    \n    # Fetch global stats',
    download_ui + '\n    # Fetch global stats'
)

with open("app.py", "w") as f:
    f.write(content)
print("Added download button!")
