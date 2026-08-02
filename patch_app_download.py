with open("app.py", "r") as f:
    content = f.read()

old_code = """    st.success("✅ Auto-saving is active. Your data is instantly saved as you type.")
    
    col_btn2, col_btn3 = st.columns([1, 1])"""

new_code = """    st.success("✅ Auto-saving is active in the cloud. Your data is instantly saved as you type.")
    st.info("⚠️ Because you are on the cloud, download your data to your hard drive frequently!")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn1:
        try:
            import pandas as pd
            live_db = pd.read_csv("Imp Data/Live_Manual_Data.csv")
            csv_data = live_db.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Download to Hard Drive",
                data=csv_data,
                file_name="Live_Manual_Data.csv",
                mime="text/csv",
                type="primary"
            )
        except Exception:
            pass
"""

content = content.replace(old_code, new_code)
with open("app.py", "w") as f:
    f.write(content)
print("Patched download button!")
