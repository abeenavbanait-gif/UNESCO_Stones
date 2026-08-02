with open("app.py", "r") as f:
    content = f.read()

old_code = """            num_visited = len(visited_sites)
            
            st.markdown(f"### 📊 Data Entry Progress: {num_visited} / {len(manual_df)} Sites Visited")"""

new_code = """            num_visited = len(visited_sites)
            
            total_sites = 972
            pct = min((num_visited / total_sites) * 100, 100)
            
            html_progress = f'''
            <div style="display: flex; align-items: center; margin-bottom: 20px;">
                <h3 style="margin: 0; margin-right: 20px;">📊 Data Entry Progress: {num_visited} / {total_sites} Sites Visited</h3>
                <div style="flex-grow: 1; background-color: #e0e0e0; border-radius: 10px; height: 20px; overflow: hidden;">
                    <div style="width: {pct}%; height: 100%; background-color: #28a745; border-radius: 10px;"></div>
                </div>
                <span style="margin-left: 10px; font-weight: bold; color: #555;">{pct:.1f}%</span>
            </div>
            '''
            st.markdown(html_progress, unsafe_allow_html=True)"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open("app.py", "w") as f:
        f.write(content)
    print("Patch applied successfully.")
else:
    print("Old code not found.")
