with open("app.py", "r") as f:
    content = f.read()

old_code = """        st.markdown(f'''
        <div style="user-select: text; -webkit-user-select: text; cursor: text; background-color: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); line-height: 1.8; font-size: 1.1em; border-top: 4px solid #4e4376;">
            {highlighted_ouv}
        </div>
        ''', unsafe_allow_html=True)"""

new_code = """        st.markdown(f'''
        <div style="user-select: text; -webkit-user-select: text; cursor: text; background-color: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); line-height: 1.8; font-size: 1.1em; border-top: 4px solid #4e4376;">
            {highlighted_ouv}
        </div>
        ''', unsafe_allow_html=True)
        
        with st.expander("📝 Show Raw OUV Text (Use this if drag-and-drop is not working from above)"):
            st.text_area("Raw Text (Easy to highlight and drag)", value=ouv_text, height=300, key=f"raw_ouv_{unesco_id}")"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open("app.py", "w") as f:
        f.write(content)
    print("Patched raw OUV text area successfully.")
else:
    print("Old code not found.")
