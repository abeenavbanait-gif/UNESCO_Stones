import re

with open('app.py', 'r') as f:
    content = f.read()

# 1. Update imports
content = content.replace(
    'get_manual_data_for_site, save_manual_data',
    'get_live_data_for_site, save_live_data_field'
)

# 2. Add callback function before render_field
callback_code = """
    def save_field_callback(unesco_id, site_name, country, field_key, widget_key, is_list=False):
        val = st.session_state[widget_key]
        if is_list:
            val = " | ".join(val)
        save_live_data_field(unesco_id, site_name, country, field_key, val)

"""

# Find where render_field starts
content = content.replace(
    '    manual_data = get_manual_data_for_site(unesco_id)\n    \n    form_data = {}\n        \n    def render_field',
    '    manual_data = get_live_data_for_site(unesco_id)\n' + callback_code + '    def render_field'
)

# 3. Update render_field
old_render_field = """        if widget_type == "text_input":
            val = col_input.text_input(label, key=main_key)
        elif widget_type == "selectbox":
            val = col_input.selectbox(label, options, key=main_key)
        elif widget_type == "multiselect":
            val_list = col_input.multiselect(label, options=options, key=main_key)
            val = " | ".join(val_list)
                
        ref_choice = col_ref.selectbox("Reference", ["", "Internal (DS/OUV)", "External"], key=ref_key)
            
        ext_val = ""
        if ref_choice == "External":
            ext_val = col_ref.text_input("Citation / Link", key=ext_key)
                
        form_data[field_key] = val
        form_data[f"{field_key}_Ref"] = ref_choice
        form_data[f"{field_key}_Ext"] = ext_val"""

new_render_field = """        s_name = site_data['site_name']
        s_country = site_data['country']
        
        if widget_type == "text_input":
            val = col_input.text_input(label, key=main_key, on_change=save_field_callback, args=(unesco_id, s_name, s_country, field_key, main_key, False))
        elif widget_type == "selectbox":
            val = col_input.selectbox(label, options, key=main_key, on_change=save_field_callback, args=(unesco_id, s_name, s_country, field_key, main_key, False))
        elif widget_type == "multiselect":
            val_list = col_input.multiselect(label, options=options, key=main_key, on_change=save_field_callback, args=(unesco_id, s_name, s_country, field_key, main_key, True))
            val = " | ".join(val_list)
                
        ref_choice = col_ref.selectbox("Reference", ["", "Internal (DS/OUV)", "External"], key=ref_key, on_change=save_field_callback, args=(unesco_id, s_name, s_country, f"{field_key}_Ref", ref_key, False))
            
        ext_val = ""
        if ref_choice == "External":
            ext_val = col_ref.text_input("Citation / Link", key=ext_key, on_change=save_field_callback, args=(unesco_id, s_name, s_country, f"{field_key}_Ext", ext_key, False))"""

content = content.replace(old_render_field, new_render_field)

# 4. Update UNESCO Mention and Other references
old_unesco = """        val_unesco = st.selectbox("UNESCO Mention", ["", "Yes", "No"], key=f"unesco_{unesco_id}")
        val_other = st.text_input("Other references", key=f"other_ref_{unesco_id}")
        form_data["UNESCO Mention"] = val_unesco
        form_data["Other references"] = val_other
            
    save_success = False
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
    with col_btn1:
        submit_btn = st.button("💾 Save Data to CSV", type="primary")
    with col_btn3:
        fullscreen_btn = st.button("🖥️ Fullscreen Table", type="secondary")
            
    if submit_btn or fullscreen_btn:
        save_success = save_manual_data(unesco_id, form_data)
        if fullscreen_btn:
            view_fullscreen_table(unesco_id)
                
    with col_btn2:
        with st.popover("👀 View Site Data"):
            try:
                import numpy as np
                current_db = pd.read_csv("Imp Data/UNESCO_Stones_Manual_Data.csv")"""

new_unesco = """        s_name = site_data['site_name']
        s_country = site_data['country']
        val_unesco = st.selectbox("UNESCO Mention", ["", "Yes", "No"], key=f"unesco_{unesco_id}", on_change=save_field_callback, args=(unesco_id, s_name, s_country, "UNESCO Mention", f"unesco_{unesco_id}", False))
        val_other = st.text_input("Other references", key=f"other_ref_{unesco_id}", on_change=save_field_callback, args=(unesco_id, s_name, s_country, "Other references", f"other_ref_{unesco_id}", False))
            
    st.success("✅ Auto-saving is active. Your data is instantly saved as you type.")
    
    col_btn2, col_btn3 = st.columns([1, 1])
    with col_btn3:
        fullscreen_btn = st.button("🖥️ Fullscreen Table", type="secondary")
            
    if fullscreen_btn:
        view_fullscreen_table(unesco_id)
                
    with col_btn2:
        with st.popover("👀 View Site Data"):
            try:
                import numpy as np
                current_db = pd.read_csv("Imp Data/Live_Manual_Data.csv")"""

content = content.replace(old_unesco, new_unesco)

# Also update the view_fullscreen_table popover logic
content = content.replace(
    'current_db = pd.read_csv("Imp Data/UNESCO_Stones_Manual_Data.csv")',
    'current_db = pd.read_csv("Imp Data/Live_Manual_Data.csv")'
)

with open('app.py', 'w') as f:
    f.write(content)
print("Patched app.py")
