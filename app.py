import streamlit as st
import pandas as pd
import re
from data_manager import load_monument_data, load_notes, save_note, get_global_stats, get_live_data_for_site, save_live_data_field, save_site_document, get_site_documents, get_visited_site_ids, is_site_visited
import asyncio
from rag_pipeline import ingest_dossier, ask_question
from custom_rag_pipeline import ingest_custom_document, ask_custom_question
import plotly.express as px
import urllib.parse

st.set_page_config(page_title="UNESCO Building Stones Dashboard", layout="wide", page_icon="🏛️")

# Custom CSS
st.markdown("""
<style>
    /* Global Font Size Increase */
    html, body, [class*="st-"] {
        font-size: 1.05rem;
    }

    /* Main background */
    .stApp {
        background-color: #FAF9F6;
        color: #2b2b2b;
    }
    
    /* Light Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #4e4376 !important;
    }
    
    /* Force Dropdown, Search Inputs, and Textareas to be readable and YELLOW */
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stTextArea"] div[data-baseweb="textarea"] {
        background-color: #fff9c4 !important; /* Yellow background */
        border: 2px solid #fbc02d !important; /* Yellow border */
        border-radius: 6px;
    }
    
    div[data-testid="stTextInput"] input, 
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] div,
    div[data-testid="stTextArea"] textarea {
        color: #000000 !important; /* Black font */
    }
    
    /* Make sure placeholder text is legible */
    div[data-testid="stTextInput"] input::placeholder, 
    div[data-testid="stTextArea"] textarea::placeholder {
        color: #555555 !important;
    }
    
    /* Headers and text in main area */
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #2b2b2b;
    }
    
    /* Top Details Bar */
    .details-bar {
        background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
        color: white !important;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .details-bar h1, .details-bar h2, .details-bar h3, .details-bar p, .details-bar span, .details-bar a {
        color: white !important;
    }
    .details-bar a {
        text-decoration: underline;
    }
    
    /* Highlighting */
    .highlight-stone {
        background-color: #ff9a9e;
        background-image: linear-gradient(120deg, #f6d365 0%, #fda085 100%);
        color: #000 !important;
        font-weight: bold;
        padding: 3px 6px;
        border-radius: 4px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    }
    
    /* Info Cards */
    .info-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #4e4376;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        height: 100%;
    }
    
    /* Override markdown text colors inside cards */
    .info-card p, .info-card h3 {
        color: #2b2b2b !important;
    }
    
    /* Top action buttons */
    .stButton>button {
        border-radius: 20px;
        font-weight: bold;
        background-color: #4CAF50 !important;
        color: white !important;
        border: 2px solid #45a049 !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #45a049 !important;
        color: white !important;
        border-color: #3d8b40 !important;
    }
    
    /* Sidebar Gallery Image Hover Effect */
    .sidebar-gallery-img {
        width: 100%;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s ease-in-out;
    }
    .sidebar-gallery-img:hover {
        transform: scale(1.05);
        cursor: pointer;
    }
</style>


""", unsafe_allow_html=True)

def get_unesco_images(unesco_id):
    """Generate predictable UNESCO gallery image URLs to bypass Cloudflare scraping blocks."""
    try:
        padded_id = str(unesco_id).zfill(4)
        urls = []
        for i in range(1, 7):
            num = str(i).zfill(4)
            url = f"https://whc.unesco.org/uploads/sites/gallery/original/site_{padded_id}_{num}.jpg"
            urls.append(url)
        return urls
    except Exception:
        return []

# Load Data
df = load_monument_data('Imp Data/built_monument_sites.csv')
notes = load_notes()

if df.empty:
    st.error("Could not load dataset. Please check the file path.")
    st.stop()


def render_home_page(df):
    st.title("🌍 Global Heritage Stones Dashboard")
    st.markdown("Welcome to the analytical overview of built heritage and construction materials across UNESCO Cultural Sites.")
    
    st.markdown("---")
    st.subheader("💾 Export & View Manual Data")
    st.markdown("Download the full manual data you have entered so far for safekeeping to ensure you never lose your progress on the cloud.")
    try:
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
            st.dataframe(live_db.astype(str).replace('nan', ''), use_container_width=True)
    except FileNotFoundError:
        st.info("No manual data has been saved yet. Start filling out the Manual Data Entry Form to see it here!")
    
    st.markdown("---")
    # Fetch global stats

    
    # Global Overview Breakdown
    g_stats = get_global_stats('Imp Data/unesco_whs_master_database.csv')
    
    st.markdown(f"""
    <div style="background-color: #f1f8ff; padding: 20px; border-radius: 8px; border-left: 4px solid #0366d6; margin-bottom: 20px;">
        <h4 style="margin-top: 0; margin-bottom: 15px; color: #0366d6;">Global UNESCO Overview</h4>
        <table style="width: 100%; border-collapse: collapse; text-align: left; background-color: white; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <tr style="background-color: #e1efff; border-bottom: 1px solid #c8e1ff;">
                <th style="padding: 10px; color: #0366d6;">Metric</th>
                <th style="padding: 10px; color: #0366d6;">Count</th>
            </tr>
            <tr style="border-bottom: 1px solid #eaeaea;">
                <td style="padding: 10px;">Total World Heritage Sites</td>
                <td style="padding: 10px;"><strong>{g_stats['total_unesco']}</strong></td>
            </tr>
            <tr style="border-bottom: 1px solid #eaeaea;">
                <td style="padding: 10px;">Cultural Sites</td>
                <td style="padding: 10px;"><strong>{g_stats['cultural']}</strong></td>
            </tr>
            <tr style="border-bottom: 1px solid #eaeaea;">
                <td style="padding: 10px;">Natural Sites</td>
                <td style="padding: 10px;"><strong>{g_stats['natural']}</strong></td>
            </tr>
            <tr style="border-bottom: 1px solid #eaeaea;">
                <td style="padding: 10px;">Mixed Sites</td>
                <td style="padding: 10px;"><strong>{g_stats['mixed']}</strong></td>
            </tr>
            <tr style="background-color: #f8fbfd; border-bottom: 1px solid #eaeaea;">
                <td style="padding: 10px; color: #d35400;"><strong>Built Monuments (Analyzed)</strong></td>
                <td style="padding: 10px; color: #d35400;"><strong>{len(df)}</strong></td>
            </tr>
        </table>
        <p style="margin-top: 10px; margin-bottom: 0; font-size: 0.9em; color: #666;">
            <em>Note: {g_stats['missing_ouv']} cultural sites lacked official OUV statements and could not be fully analyzed.</em>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Data Entry Progress Section
    try:
        manual_df = pd.read_csv("Imp Data/Live_Manual_Data.csv")
        meta_cols = ['Site ID', 'Site Name', 'Country', 'safe_id', 'Index', 'UNESCO Criteria']
        data_cols = [c for c in manual_df.columns if c not in meta_cols]
        
        if len(data_cols) > 0:
            calc_df = manual_df[data_cols].copy()
            # Treat empty strings, string NaNs, and "Unknown" as empty data
            calc_df = calc_df.replace([r'^\s*$', 'NaN', 'nan', 'None', 'Unknown'], pd.NA, regex=True)
            
            filled_counts = calc_df.notna().sum(axis=1)
            visited_mask = filled_counts > 0
            
            visited_sites = manual_df[visited_mask].copy()
            visited_sites['Fields Filled'] = filled_counts[visited_mask]
            visited_sites['Total Fields'] = len(data_cols)
            visited_sites['Completion (%)'] = ((visited_sites['Fields Filled'] / visited_sites['Total Fields']) * 100).round(1)
            
            num_visited = len(visited_sites)
            
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
            st.markdown(html_progress, unsafe_allow_html=True)
            if num_visited > 0:
                display_df = visited_sites[['Site Name', 'Country', 'Completion (%)', 'Fields Filled']].sort_values(by='Completion (%)', ascending=False).reset_index(drop=True)
                display_df['Completion (%)'] = display_df['Completion (%)'].astype(str) + "%"
                for col in display_df.columns:
                    display_df[col] = display_df[col].astype(str).replace('nan', '')
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No data has been filled yet. Head over to the Site Explorer to get started!")
            
            st.markdown("---")
    except Exception as e:
        st.warning(f"Could not load data entry statistics: {e}")
        
    # High-level metrics
    col1, col2, col3, col4 = st.columns(4)
    total_sites = len(df)
    
    # Calculate total unique stones
    all_stones = set()
    for s in df['named_trade_stones'].dropna():
        for stn in s.split(';'):
            if stn.strip(): all_stones.add(stn.strip().lower())
    
    avg_score = df['score'].mean() if 'score' in df.columns else 0
    
    col1.metric("Total Built Monuments", f"{total_sites}")
    col2.metric("Unique Trade Stones", f"{len(all_stones)}")
    col3.metric("Avg Classification Score", f"{avg_score:.1f}/100")
    col4.metric("Regions Spanned", f"{df['region'].nunique()}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Map
    st.markdown("### 🗺️ Geographical Distribution of Sites")
    map_df = df.dropna(subset=['latitude', 'longitude']).copy()
    if not map_df.empty:
        # Format columns for the hover tooltip
        map_df['Category'] = map_df['category']
        map_df['Architecture'] = map_df['architecture_style_found'].fillna('None Detected').apply(lambda x: x.replace(';', ', ').title())
        map_df['Stone Mentions'] = map_df['stone_count'].apply(lambda x: 'Yes' if pd.notna(x) and x > 0 else 'No')
        map_df['Major Rock Type'] = map_df['stone_types_found'].fillna('N/A').apply(lambda x: x.replace(';', ', ').title() if x != 'N/A' else 'None')
        
        fig_map = px.scatter_mapbox(
            map_df, 
            lat="latitude", 
            lon="longitude", 
            hover_name="site_name", 
            hover_data={
                "latitude": False,
                "longitude": False,
                "score": True,
                "Category": True,
                "Architecture": True,
                "Stone Mentions": True,
                "Major Rock Type": True
            },
            color="score",
            color_continuous_scale=px.colors.sequential.YlOrRd,
            size_max=15, 
            zoom=1.5,
            mapbox_style="carto-positron",
            title="World Map of Built Monuments"
        )
        fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No coordinate data available to display the map.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts
    try:
        manual_df = pd.read_csv("Imp Data/Live_Manual_Data.csv")
    except:
        manual_df = pd.DataFrame()
        
    col_chart1, col_chart2, col_chart3 = st.columns(3)
    with col_chart1:
        st.markdown("### 📊 Sites by Region")
        if not manual_df.empty and 'Site ID' in manual_df.columns:
            manual_df['_merge_id'] = manual_df['Site ID'].astype(str).str.replace('.0', '', regex=False)
            df_region = df[['unesco_id', 'region']].copy()
            df_region['_merge_id'] = df_region['unesco_id'].astype(str).str.replace('.0', '', regex=False)
            merged_region = manual_df.merge(df_region[['_merge_id', 'region']], on='_merge_id', how='left')
            region_counts = merged_region['region'].value_counts().reset_index()
            region_counts.columns = ['Region', 'Count']
            fig_pie = px.pie(region_counts, values='Count', names='Region', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie.update_layout(
                legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No manual data available yet.")
            
    with col_chart2:
        st.markdown("### 🪨 Rock Class Distribution")
        class_counts = {"Igneous": 0, "Metamorphic": 0, "Sedimentary": 0}
        if not manual_df.empty and 'Rock Class' in manual_df.columns:
            for val in manual_df['Rock Class'].dropna():
                rc = str(val).strip().capitalize()
                if "Igneous" in rc: class_counts["Igneous"] += 1
                elif "Metamorphic" in rc: class_counts["Metamorphic"] += 1
                elif "Sedimentary" in rc: class_counts["Sedimentary"] += 1
        
        if sum(class_counts.values()) > 0:
            pie_df = pd.DataFrame({
                "Rock Class": list(class_counts.keys()),
                "Count": list(class_counts.values())
            })
            fig_pie_class = px.pie(
                pie_df, 
                values="Count", 
                names="Rock Class",
                hole=0.4,
                color="Rock Class",
                color_discrete_map={
                    "Igneous": "#e74c3c",       # Red
                    "Metamorphic": "#9b59b6",   # Purple
                    "Sedimentary": "#f1c40f"    # Yellow
                }
            )
            fig_pie_class.update_layout(
                legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_pie_class, use_container_width=True)
        else:
            st.info("No manual rock class data available yet.")
            
    with col_chart3:
        st.markdown("### 🪨 Top 15 Most Common Stones")
        stone_list = []
        if not manual_df.empty:
            if 'Mentioned Major Stone(s)' in manual_df.columns:
                for s in manual_df['Mentioned Major Stone(s)'].dropna():
                    stone_list.extend([stn.strip().title() for stn in str(s).split(',') if stn.strip() and stn.strip().lower() not in ['nan', 'none']])
            if 'Secondary Stone' in manual_df.columns:
                for s in manual_df['Secondary Stone'].dropna():
                    stone_list.extend([stn.strip().title() for stn in str(s).split(',') if stn.strip() and stn.strip().lower() not in ['nan', 'none']])
                    
        if stone_list:
            stone_counts = pd.Series(stone_list).value_counts().head(15).reset_index()
            stone_counts.columns = ['Stone', 'Count']
            
            fig_bar = px.bar(stone_counts, x='Count', y='Stone', orientation='h', color='Count', color_continuous_scale=px.colors.sequential.Blues)
            fig_bar.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(t=20, b=20, l=20, r=20),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No manual stone data available yet.")
        
    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # NLP Score Explanation
    st.markdown("### 🧠 How is the NLP Score Calculated?")
    st.markdown("""
    The **Confidence Score** (0-100) measures the likelihood that a UNESCO Cultural Site is a built monument primarily defined by its construction materials (stone). It is calculated in three layers:
    
    1. **Layer 1: Built Heritage Criteria** (+30 pts)
       - The site must be inscribed under specific UNESCO Criteria representing human architecture (e.g., Criterion (i) Masterpiece, (iv) Typology).
    2. **Layer 2: Architecture Name Matching** (+40 pts)
       - The site name is scanned against 50+ architectural keywords (e.g., *Temple*, *Castle*, *Palace*, *Bridge*).
    3. **Layer 3: NLP OUV Text Analysis** (+30 pts)
       - The official Outstanding Universal Value (OUV) text is processed using `NLTK` (lemmatization and tokenization).
       - It searches for geological terms, trade stones (e.g., *Carrara marble*), construction verbs (*carved*, *quarried*), and architectural elements (*facade*, *dome*).
       - The density of these terms heavily influences the final score.
    """)
    
    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # Data Download Section
    st.markdown("### 💾 Download Raw Datasets")
    st.markdown("Download the processed CSV files containing the heritage stones database, classification models, and NLP results.")
    
    import os
    data_dir = "Imp Data"
    if os.path.exists(data_dir):
        csv_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.csv')])
        
        if csv_files:
            # Create a nice layout with 2 or 3 columns for buttons
            cols = st.columns(3)
            for i, file in enumerate(csv_files):
                file_path = os.path.join(data_dir, file)
                try:
                    with open(file_path, "rb") as f:
                        csv_bytes = f.read()
                    
                    # Convert file name to a more readable format for the label
                    clean_name = file.replace('.csv', '').replace('_', ' ').title()
                    if len(clean_name) > 30:
                        clean_name = clean_name[:27] + "..."
                        
                    cols[i % 3].download_button(
                        label=f"📥 {clean_name}",
                        data=csv_bytes,
                        file_name=file,
                        mime="text/csv",
                        help=f"Download {file}",
                        key=f"dl_{file}"
                    )
                except Exception as e:
                    pass
        else:
            st.info("No CSV datasets found in the data directory.")

@st.dialog("🖥️ Fullscreen Site Data", width="large")
def view_fullscreen_table(unesco_id):
    try:
        import numpy as np
        current_db = pd.read_csv("Imp Data/Live_Manual_Data.csv")
        base_fields = [
            'Architecture Type', 'Construction Period', 'Civilization', 'UNESCO Criteria',
            'Mentioned Major Stone(s)', 'Rock Class', 'Secondary Stone', 'Local Stone Name', 'Lithology',
            'Geological Age', 'Formation', 'Colour', 'Texture', 'Minerals',
            'Quarry', 'Quarry Country', 'Local vs Imported', 'Transport Distance',
            'Structural Use', 'Decorative Use', 'Masonry Technique',
            'Weathering', 'Replacement Stone', 'Restoration', 'Condition'
        ]
        active_fields = ['Site ID', 'Site Name', 'Country']
        for bf in base_fields:
            active_fields.extend([bf, f"{bf}_Ref", f"{bf}_Ext"])
        active_fields.extend(['UNESCO Mention', 'Other references'])
        valid_cols = [c for c in active_fields if c in current_db.columns]
        safe_unesco_id = str(unesco_id).replace('.0', '')
        current_db['safe_id'] = current_db['Site ID'].astype(str).str.replace('.0', '', regex=False)
        site_db = current_db[current_db['safe_id'] == safe_unesco_id][valid_cols].copy()
        
        if site_db.empty:
            st.info("No manual data has been saved for this site yet.")
        else:
            display_df = site_db.T
            display_df.columns = ["Value"]
            display_df = display_df.fillna("")
            st.dataframe(display_df, use_container_width=True, height=600)
    except Exception as e:
        st.warning("Database not found or empty.")

def render_site_explorer(df, notes):
    # ==========================================
    # SIDEBAR FILTERING
    # ==========================================
    st.sidebar.title("🔍 Site Filters")
    
    search_query = st.sidebar.text_input("Search Site Name", "")
    regions = ["All"] + sorted(df['region'].dropna().unique().tolist())
    selected_region = st.sidebar.selectbox("Filter by Region", regions)
    
    countries = ["All"] + sorted(list(set([c.strip() for sublist in df['country'].dropna().str.split(',') for c in sublist])))
    selected_country = st.sidebar.selectbox("Filter by Country", countries)
    
    search_stone = st.sidebar.text_input("Search for a Stone (e.g. Marble)", "")
    
    # Apply Filters
    filtered_df = df.copy()
    
    if search_query:
        filtered_df = filtered_df[filtered_df['site_name'].str.contains(search_query, case=False, na=False)]
    
    if selected_region != "All":
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    
    if selected_country != "All":
        filtered_df = filtered_df[filtered_df['country'].str.contains(selected_country, case=False, na=False)]
    
    if search_stone:
        filtered_df = filtered_df[
            filtered_df['stone_types_found'].str.contains(search_stone, case=False, na=False) | 
            filtered_df['named_trade_stones'].str.contains(search_stone, case=False, na=False)
        ]
    
    st.sidebar.markdown(f"**{len(filtered_df)} Sites Match Your Filters**")
    st.sidebar.markdown("---")
    
    if filtered_df.empty:
        st.warning("No sites match your filters.")
        st.stop()
    
    site_options = filtered_df['site_name'].tolist()
    
    # ==========================================
    # NAVIGATION STATE
    # ==========================================
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    
    # Cap index if filters changed
    if st.session_state.current_index >= len(site_options):
        st.session_state.current_index = 0
    
    def next_site():
        if st.session_state.current_index < len(site_options) - 1:
            st.session_state.current_index += 1
        else:
            st.session_state.current_index = 0
        # Force the selectbox to update its value
        st.session_state.site_selector = site_options[st.session_state.current_index]
    
    def prev_site():
        if st.session_state.current_index > 0:
            st.session_state.current_index -= 1
        else:
            st.session_state.current_index = len(site_options) - 1
        # Force the selectbox to update its value
        st.session_state.site_selector = site_options[st.session_state.current_index]
    
    def on_select_change():
        selected = st.session_state.get('site_selector')
        if selected and selected in site_options:
            st.session_state.current_index = site_options.index(selected)
        else:
            st.session_state.current_index = 0

    
    visited_ids = get_visited_site_ids()

    def format_site_option(name):
        s_rows = filtered_df[filtered_df['site_name'] == name]
        if not s_rows.empty:
            s_id = str(s_rows.iloc[0]['unesco_id']).replace('.0', '')
            if s_id in visited_ids:
                return f"🟢 {name}"
        return f"⚪ {name}"

    if "site_selector" not in st.session_state or st.session_state.site_selector not in site_options:
        st.session_state.site_selector = site_options[st.session_state.current_index]

    selected_site_name = st.sidebar.selectbox(
        "Select a Site to Study", 
        site_options, 
        format_func=format_site_option,
        key="site_selector",
        on_change=on_select_change
    )


    
    # Get the selected row
    site_data = filtered_df[filtered_df['site_name'] == selected_site_name].iloc[0]
    unesco_id = str(site_data['unesco_id'])
    
    # ==========================================
    # SIDEBAR IMAGE GALLERY
    # ==========================================
    image_urls = get_unesco_images(unesco_id)
    if image_urls:
        st.sidebar.markdown("### 📸 Site Gallery")
        for img_url in image_urls:
            gallery_page_url = f"https://whc.unesco.org/en/list/{unesco_id}/gallery/"
            html_code = f'<a href="{gallery_page_url}" target="_blank" title="View on UNESCO Gallery"><img src="{img_url}" class="sidebar-gallery-img" onerror="this.style.display=\'none\'" referrerpolicy="no-referrer"></a>'
            st.sidebar.markdown(html_code, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("### 🤖 Gemini API Configuration")
    api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
    st.sidebar.caption("Required for the Official Dossier Chat and Custom GraphRAG features. [Get a free key here](https://aistudio.google.com/app/apikey).")
    
    st.sidebar.markdown("---")
    # ==========================================
    # MAIN PANEL: TOP BAR
    # ==========================================
    nav_col1, nav_col2, nav_col3 = st.columns([1, 8, 1])
    with nav_col1:
        st.button("⬅️ Previous", on_click=prev_site, use_container_width=True)
    with nav_col3:
        st.button("Next Site ➡️", on_click=next_site, type="primary", use_container_width=True)
    
    lat = site_data.get('latitude', '')
    lon = site_data.get('longitude', '')
    if pd.notna(lat) and pd.notna(lon) and str(lat).strip() != '':
        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    else:
        safe_name = urllib.parse.quote(site_data['site_name'])
        maps_url = f"https://www.google.com/maps/search/?api=1&query={safe_name}"
    
    unesco_url = site_data.get('unesco_url', f"https://whc.unesco.org/en/list/{unesco_id}")
    
    # Display the Essential Details Bar
    saved_docs = get_site_documents(unesco_id)
    doc_links_html = ""
    import base64
    for doc in saved_docs:
        try:
            with open(doc['path'], "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            doc_links_html += f'<a href="data:application/octet-stream;base64,{b64}" download="{doc["file"]}" style="margin-right: 15px;">🔗 View {doc["name"]}</a>'
        except Exception:
            pass
            
    if not doc_links_html:
        # If no documents uploaded yet, provide an anchor to jump down to the upload section
        doc_links_html = '<a href="#upload-site-documents" style="margin-right: 15px;">🔗 ICOMOS Document</a>'

    site_is_visited = is_site_visited(unesco_id, visited_ids)
    visited_tag = ' <span style="font-size: 0.65em; background-color: #2e7d32; color: #ffffff; padding: 4px 10px; border-radius: 12px; vertical-align: middle; font-weight: bold; margin-left: 10px;">🟢 Visited</span>' if site_is_visited else ''

    header_html = f'''<div class="details-bar">
<h1 style="margin-top:0px; margin-bottom:5px; color: white;">🏛️ {site_data['site_name']}{visited_tag}</h1>
<p style="font-size: 1.1em; margin-bottom: 15px; color: white;">
<strong>UNESCO ID:</strong> {unesco_id} &nbsp;|&nbsp; 
<strong>Country:</strong> {site_data['country']} &nbsp;|&nbsp; 
<strong>Year:</strong> {site_data.get('year_inscribed', 'N/A')} &nbsp;|&nbsp; 
<strong>Score:</strong> {site_data.get('score', 'N/A')}
</p>
<div>
{doc_links_html}
<a href="{unesco_url}" target="_blank" style="margin-right: 15px; color: white;">🔗 View Official UNESCO Dossier</a>
<a href="{unesco_url}/gallery/" target="_blank" style="margin-right: 15px; color: white;">🖼️ View Full UNESCO Gallery</a>
<a href="{maps_url}" target="_blank" style="color: white;">🗺️ Open in Google Maps</a>
</div>
</div>'''

    st.markdown(header_html, unsafe_allow_html=True)



    
    # ==========================================
    # SECTION 1: ARCHITECTURE & STONES CARDS
    # ==========================================
    st.markdown("## 🧱 Site Construction Details")
    col_arch, col_stone = st.columns(2)
    
    with col_arch:
        arch = site_data.get('architecture_style_found', '')
        arch_display = ", ".join([s.strip().title() for s in arch.split(';') if s.strip()]) if pd.notna(arch) and arch else "None Detected"
        
        elem = site_data.get('architectural_elements_found', '')
        elem_display = ", ".join([s.strip().title() for s in elem.split(';') if s.strip()]) if pd.notna(elem) and elem else "None Detected"
    
        st.markdown(f"""
        <div class="info-card">
            <h3 style="color:#4e4376; margin-top:0;">📐 Architecture</h3>
            <p><strong>Styles:</strong> {arch_display}</p>
            <p><strong>Elements:</strong> {elem_display}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_stone:
        stones = site_data.get('stone_types_found', '')
        stones_disp = ", ".join([s.strip().title() for s in stones.split(';') if s.strip()]) if pd.notna(stones) and stones else "None Detected"
        
        named = site_data.get('named_trade_stones', '')
        named_disp = ", ".join([s.strip().title() for s in named.split(';') if s.strip()]) if pd.notna(named) and named else "None Detected"
    
        st.markdown(f"""
        <div class="info-card" style="border-left-color: #f6d365;">
            <h3 style="color:#e67e22; margin-top:0;">🪨 Building Stones</h3>
            <p><strong>General Stones:</strong> {stones_disp}</p>
            <p><strong>Trade Stones:</strong> <span style="color:#d35400; font-weight:bold;">{named_disp}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        suggested = site_data.get('suggested_stones', '')
        if pd.notna(suggested) and suggested:
            suggested_disp = ", ".join([s.strip().title() for s in str(suggested).split(';') if s.strip()])
            st.markdown(f"""
            <div style="background-color: #fff8e1; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin-top: 15px; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 20px;">💡</span>
                    <strong style="color: #b08d00; font-size: 16px;">Suggestion for UNESCO Database</strong>
                </div>
                <p style="margin-top: 8px; margin-bottom: 0; color: #5a4a00; line-height: 1.4;">
                    The rock <strong>{suggested_disp}</strong> is historically significant to this monument, but it is <em>missing</em> from the official UNESCO OUV statement and site description. It should be explicitly mentioned.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    # ==========================================
    # SECTION: WEB SEARCH INSIGHTS
    # ==========================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 🔍 Web Search Stone Researcher")
    st.markdown(f"Click below to run a live, automated Wikipedia search for stones used to build **{site_data['site_name']}**.")
    
    if st.button("Search Wikipedia for Building Stones 🌐", type="primary"):
        with st.spinner(f"Searching Wikipedia for {site_data['site_name']}..."):
            try:
                import wikipedia
                # Set a custom user agent to prevent Wikipedia API from rejecting our requests
                wikipedia.set_user_agent('UNESCOHeritageStonesBot/1.0 (contact@example.com)')
                
                try:
                    page = wikipedia.page(site_data['site_name'], auto_suggest=False)
                except wikipedia.exceptions.DisambiguationError as e:
                    page = wikipedia.page(e.options[0], auto_suggest=False)
                except wikipedia.exceptions.PageError:
                    page = wikipedia.page(site_data['site_name'], auto_suggest=True)
                
                content = page.content.lower()
                summary_text = page.summary

                # Extract stones
                COMMON_STONES = [
                    'marble', 'granite', 'limestone', 'sandstone', 'basalt', 'tuff', 
                    'slate', 'quartzite', 'travertine', 'andesite', 'diorite', 'porphyry', 
                    'alabaster', 'schist', 'gneiss', 'obsidian', 'laterite', 'coral', 
                    'chalk', 'flint', 'chert', 'adobe', 'brick', 'terracotta', 'sillar',
                    'makrana marble', 'carrara marble', 'pietra serena'
                ]
                
                found_stones = set()
                for stone in COMMON_STONES:
                    if re.search(r'\b' + re.escape(stone) + r'\b', content):
                        found_stones.add(stone.title())
                        
                st.markdown(f"""
                <div style="background-color: #f0fdfa; border-left: 4px solid #0d9488; padding: 20px; border-radius: 8px; margin-top: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                        <span style="font-size: 22px;">🌐</span>
                        <strong style="color: #0f766e; font-size: 18px;">Wikipedia Overview ({page.title})</strong>
                    </div>
                    <div style="color: #115e59; line-height: 1.6; font-size: 1.05em; padding-left: 10px; font-style: italic;">
                        "{summary_text}"
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 💡 Dynamic Suggestion Based on Search")
                if found_stones:
                    found_str = ", ".join(found_stones)
                    st.markdown(f"""
                    <div style="background-color: #fff8e1; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px;">
                        <span style="font-size: 18px;">💡</span>
                        <strong style="color: #b08d00;">Extracted from Wikipedia:</strong> 
                        The rock(s) <strong>{found_str}</strong> appear to be highly related to this monument based on its Wikipedia page.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Not available (No major building stones definitively extracted from the Wikipedia page).")
                    
            except Exception as e:
                st.error(f"Failed to query Wikipedia: {str(e)}")
    
    # ==========================================
    # SECTION 6: CUSTOM DOCUMENT RAG
    # ==========================================
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("## 📚 Custom Document Chatbot (RAG)")
    st.markdown("Upload PDFs, Word Docs, Text files, Markdown files, or Spreadsheets to train a local vector database and chat with your documents.")
    
    with st.expander("Expand to Upload & Chat with Documents", expanded=False):
        uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt", "md", "docx", "csv", "xlsx"])
        
        if uploaded_file is not None:
            if st.button("🏗️ Ingest Document into Database"):
                with st.spinner("Extracting text, chunking, and saving to ChromaDB (Local Vector Store)..."):
                    try:
                        # UploadedFile is essentially a BytesIO object with a .name property
                        chunks_added = ingest_custom_document(uploaded_file.getvalue(), uploaded_file.name)
                        st.success(f"Document ingested successfully! Saved {chunks_added} chunks to the vector database.")
                    except Exception as e:
                        st.error(f"Error ingesting document: {e}")
        
        st.markdown("---")
        doc_q = st.text_input("Ask a question about your uploaded documents or the Wikipedia database:")
        if st.button("Ask Document AI"):
            if not api_key:
                st.error("Please enter your Gemini API Key in the sidebar.")
            elif not doc_q:
                st.warning("Please enter a question.")
            else:
                with st.spinner("Searching Vector Database and generating answer..."):
                    try:
                        ans = ask_custom_question(doc_q, api_key)
                        st.markdown(f"**Answer:**\n\n{ans}")
                    except Exception as e:
                        st.error(f"Error querying documents: {e}")

    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # ==========================================
    # SECTION 6.5: UPLOAD SITE DOCUMENTS
    # ==========================================
    st.markdown("<div id='upload-site-documents'></div>", unsafe_allow_html=True)
    st.markdown("## 📁 Upload Site Documents")
    st.markdown("Save official documents (e.g. ICOMOS Dossier, maps, research papers) directly to this site's database.")
    
    with st.expander("Expand to Upload Document", expanded=False):
        doc_name = st.text_input("Document Name", value=f"Advisory Body Evaluation (ICOMOS) {site_data['site_name']}")
        uploaded_doc = st.file_uploader("Upload File (PDF, DOCX, TXT, etc.)")
        
        if st.button("💾 Save Document to Database", type="primary"):
            if not uploaded_doc:
                st.warning("Please upload a file first.")
            elif not doc_name:
                st.warning("Please provide a name for the document.")
            else:
                success, msg = save_site_document(unesco_id, doc_name, uploaded_doc)
                if success:
                    st.success(f"Successfully saved {doc_name}! It is now available in the top banner.")
                    st.rerun()
                else:
                    st.error(f"Failed to save document: {msg}")
                    
    # Show existing documents
    if saved_docs:
        st.markdown("**Currently Saved Documents:**")
        for doc in saved_docs:
            col_dl, col_del = st.columns([3, 1])
            with open(doc['path'], "rb") as f:
                col_dl.download_button(
                    label=f"⬇️ Download {doc['name']}",
                    data=f.read(),
                    file_name=doc['file'],
                    mime="application/octet-stream",
                    key=f"dl_{doc['file']}"
                )
            if col_del.button("🗑️ Delete", key=f"del_{doc['file']}", type="secondary"):
                try:
                    import os
                    os.remove(doc['path'])
                    st.toast(f"Deleted {doc['name']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting file: {e}")

    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # Generate list of all extracted terms for highlighting
    all_stones_list = []
    for col in ['stone_types_found', 'named_trade_stones', 'decorative_minerals_found', 'architectural_elements_found', 'architecture_style_found']:
        val = site_data.get(col, '')
        if pd.notna(val) and val:
            all_stones_list.extend([s.strip() for s in val.split(';') if s.strip()])
    all_stones_list.sort(key=len, reverse=True)
    
    def highlight_text(text, terms):
        if not text or pd.isna(text): return ""
        
        # Clean up excessive line breaks and messy data
        cleaned = text.replace('\\n\\n', '\n\n').replace('\\n', ' ')
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = cleaned.replace('\n\n', '<br><br>')
        cleaned = cleaned.replace('\n', ' ')
        
        valid_terms = [t for t in terms if t]
        if not valid_terms: return cleaned
        
        # Single-pass regex replacement prevents nested <span> tags!
        escaped_terms = [re.escape(t) for t in valid_terms]
        pattern = re.compile(r'\b(' + '|'.join(escaped_terms) + r')\b', re.IGNORECASE)
        
        highlighted = pattern.sub(lambda m: f'<span class="highlight-stone">{m.group(1)}</span>', cleaned)
        return highlighted
    
    # ==========================================
    # SECTION 2 & 4: SITE DESCRIPTION & RESEARCHER NOTES (2-COLUMN LAYOUT)
    # ==========================================
    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    col_desc, col_notes = st.columns(2)
    
    with col_desc:
        st.markdown("## 🌍 Site Description")
        brief_desc = site_data.get('brief_description', '')
        if pd.notna(brief_desc) and brief_desc:
            highlighted_brief = highlight_text(brief_desc, all_stones_list)
            st.markdown(f"""
            <div style="background-color: #e8f4f8; padding: 20px; border-radius: 12px; border-left: 4px solid #3498db; line-height: 1.6; font-size: 1.05em; height: 250px; overflow-y: auto;">
                {highlighted_brief}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No brief description available for this site.")
            
    with col_notes:
        st.markdown("## 📝 Researcher Notes")
        current_note = notes.get(unesco_id, "")
        
        new_note = st.text_area(
            "Observations, confirmations, or dossier excerpts for this site:", 
            value=current_note, 
            height=200, 
            label_visibility="collapsed"
        )
        
        if st.button("💾 Save Notes", type="primary"):
            if save_note(unesco_id, new_note):
                st.success("Notes saved successfully!")
                
    # ==========================================
    # SECTION X: MANUAL DATA ENTRY FORM
    # ==========================================
    st.markdown("<br><hr>", unsafe_allow_html=True)
    if site_is_visited:
        st.markdown("## ✍️ Manual Data Entry Form 🟢 *(Visited & Saved)*")
    else:
        st.markdown("## ✍️ Manual Data Entry Form")
    st.markdown("Use this form to build out the master database while reviewing the site documents.")



    
    manual_data = get_live_data_for_site(unesco_id)

    def save_field_callback(unesco_id, site_name, country, field_key, widget_key, is_list=False):
        val = st.session_state[widget_key]
        if is_list:
            val = " | ".join(val)
        success = save_live_data_field(unesco_id, site_name, country, field_key, val)
        if success:
            st.toast(f"✅ Saved `{field_key}`")

    def render_field(label, field_key, widget_type="text_area", options=None, default=None):
        col_input, col_ref = st.columns([2, 1])
        
        main_key = f"data_{field_key}_{unesco_id}"
        ref_key = f"ref_{field_key}_{unesco_id}"
        ext_key = f"ext_{field_key}_{unesco_id}"
        
        # Initialize session state from DB if not already present for this site
        if main_key not in st.session_state:
            if widget_type == "multiselect":
                st.session_state[main_key] = default if default else []
            elif widget_type == "selectbox":
                # Ensure the DB value is actually in the options, otherwise default to options[0]
                db_val = str(manual_data.get(field_key, ''))
                st.session_state[main_key] = db_val if db_val in options else options[0]
            else:
                st.session_state[main_key] = str(manual_data.get(field_key, ''))
                
        if ref_key not in st.session_state:
            db_ref = str(manual_data.get(f"{field_key}_Ref", ""))
            st.session_state[ref_key] = db_ref if db_ref in ["", "Internal (DS/OUV)", "External"] else ""
            
        if ext_key not in st.session_state:
            st.session_state[ext_key] = str(manual_data.get(f"{field_key}_Ext", ""))
            
        s_name = site_data['site_name']
        s_country = site_data['country']
        
        if widget_type == "text_area":
            val = col_input.text_area(label, key=main_key, height=68, on_change=save_field_callback, args=(unesco_id, s_name, s_country, field_key, main_key, False))
        elif widget_type == "selectbox":
            val = col_input.selectbox(label, options, key=main_key, on_change=save_field_callback, args=(unesco_id, s_name, s_country, field_key, main_key, False))
        elif widget_type == "multiselect":
            val_list = col_input.multiselect(label, options=options, key=main_key, on_change=save_field_callback, args=(unesco_id, s_name, s_country, field_key, main_key, True))
            val = " | ".join(val_list)
                
        ref_choice = col_ref.selectbox("Reference", ["", "Internal (DS/OUV)", "External"], key=ref_key, on_change=save_field_callback, args=(unesco_id, s_name, s_country, f"{field_key}_Ref", ref_key, False))
            
        ext_val = ""
        if ref_choice == "External":
            ext_val = col_ref.text_area("Citation / Link", key=ext_key, height=68, on_change=save_field_callback, args=(unesco_id, s_name, s_country, f"{field_key}_Ext", ext_key, False))

    with st.expander("🏛️ A. Monument Information", expanded=True):
        render_field("Architecture Type", "Architecture Type")
        render_field("Construction Period", "Construction Period")
        render_field("Civilization", "Civilization")
            
        CRITERIA_OPTIONS = [
            "(i) to represent a masterpiece of human creative genius;",
            "(ii) to exhibit an important interchange of human values, over a span of time or within a cultural area of the world, on developments in architecture or technology, monumental arts, town-planning or landscape design;",
            "(iii) to bear a unique or at least exceptional testimony to a cultural tradition or to a civilization which is living or which has disappeared;",
            "(iv) to be an outstanding example of a type of building, architectural or technological ensemble or landscape which illustrates (a) significant stage(s) in human history;",
            "(v) to be an outstanding example of a traditional human settlement, land-use, or sea-use which is representative of a culture (or cultures), or human interaction with the environment especially when it has become vulnerable under the impact of irreversible change;",
            "(vi) to be directly or tangibly associated with events or living traditions, with ideas, or with beliefs, with artistic and literary works of outstanding universal significance;",
            "(vii) to contain superlative natural phenomena or areas of exceptional natural beauty and aesthetic importance;",
            "(viii) to be outstanding examples representing major stages of earth's history, including the record of life, significant on-going geological processes in the development of landforms, or significant geomorphic or physiographic features;",
            "(ix) to be outstanding examples representing significant on-going ecological and biological processes in the evolution and development of terrestrial, fresh water, coastal and marine ecosystems and communities of plants and animals;",
            "(x) to contain the most important and significant natural habitats for in-situ conservation of biological diversity, including those containing threatened species of outstanding universal value from the point of view of science or conservation."
        ]
        existing_crit = str(manual_data.get('UNESCO Criteria', ''))
        default_crits = []
        
        if not existing_crit or existing_crit.lower() in ['nan', 'none', '']:
            existing_crit = site_data.get('criteria', '')
            
        if existing_crit and str(existing_crit).lower() not in ['nan', 'none']:
            import re as regex
            for opt in CRITERIA_OPTIONS:
                numeral = opt.split(' ')[0]
                found_numerals = regex.findall(r'\([ivx]+\)', str(existing_crit).lower())
                if numeral.lower() in found_numerals:
                    default_crits.append(opt)
        render_field("UNESCO Criteria", "UNESCO Criteria", widget_type="multiselect", options=CRITERIA_OPTIONS, default=default_crits)
            
    with st.expander("🪨 B. Geological Materials"):
        render_field("Mentioned Major Stone(s)", "Mentioned Major Stone(s)")
        render_field("Rock Class", "Rock Class", widget_type="selectbox", options=["", "Igneous Rock", "Sedimentary Rock", "Metamorphic Rock"])
        render_field("Secondary Stone(s)", "Secondary Stone")
        render_field("Local Stone Name", "Local Stone Name")
        render_field("Lithology", "Lithology")
        render_field("Geological Age", "Geological Age")
        render_field("Formation", "Formation")
        render_field("Colour", "Colour")
        render_field("Texture", "Texture")
        render_field("Minerals", "Minerals")
            
    with st.expander("🗺️ C. Provenance"):
        render_field("Quarry", "Quarry")
        render_field("Quarry Country", "Quarry Country")
        render_field("Local vs Imported", "Local vs Imported")
        render_field("Transport Distance", "Transport Distance")
            
    with st.expander("🏗️ D. Architectural Use"):
        render_field("Structural Use", "Structural Use")
        render_field("Decorative Use", "Decorative Use")
        render_field("Masonry Technique", "Masonry Technique")
            
    with st.expander("🛠️ E. Conservation"):
        render_field("Weathering", "Weathering")
        render_field("Replacement Stone", "Replacement Stone")
        render_field("Restoration", "Restoration")
        render_field("Condition", "Condition", widget_type="selectbox", options=["", "Excellent", "Good", "Moderate", "Poor"])
            
    with st.expander("📚 F. Sources"):
        if f"unesco_{unesco_id}" not in st.session_state:
            db_u = str(manual_data.get("UNESCO Mention", ""))
            st.session_state[f"unesco_{unesco_id}"] = db_u if db_u in ["", "Yes", "No"] else ""
        if f"other_ref_{unesco_id}" not in st.session_state:
            st.session_state[f"other_ref_{unesco_id}"] = str(manual_data.get("Other references", ""))
            
        s_name = site_data['site_name']
        s_country = site_data['country']
        val_unesco = st.selectbox("UNESCO Mention", ["", "Yes", "No"], key=f"unesco_{unesco_id}", on_change=save_field_callback, args=(unesco_id, s_name, s_country, "UNESCO Mention", f"unesco_{unesco_id}", False))
        val_other = st.text_area("Other references", key=f"other_ref_{unesco_id}", height=68, on_change=save_field_callback, args=(unesco_id, s_name, s_country, "Other references", f"other_ref_{unesco_id}", False))
            
    import os
    is_cloud = "/mount/src/" in os.path.abspath(__file__)
    
    if is_cloud:
        st.success("☁️ Auto-saving is active in the cloud. Your data is instantly saved as you type.")
        st.warning("⚠️ Because you are on the cloud, download your data to your hard drive frequently!")
    else:
        st.success("✅ Auto-saving is active locally. Your data is instantly saved directly to your hard drive!")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn1:
        if is_cloud:
            try:
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

    with col_btn3:
        fullscreen_btn = st.button("🖥️ Fullscreen Table", type="secondary")
            
    if fullscreen_btn:
        view_fullscreen_table(unesco_id)
                
    with col_btn2:
        with st.popover("👀 View Site Data"):
            try:
                import numpy as np
                current_db = pd.read_csv("Imp Data/Live_Manual_Data.csv")
                    
                base_fields = [
        'Architecture Type', 'Construction Period', 'Civilization', 'UNESCO Criteria',
        'Mentioned Major Stone(s)', 'Rock Class', 'Secondary Stone', 'Local Stone Name', 'Lithology',
        'Geological Age', 'Formation', 'Colour', 'Texture', 'Minerals',
        'Quarry', 'Quarry Country', 'Local vs Imported', 'Transport Distance',
        'Structural Use', 'Decorative Use', 'Masonry Technique',
        'Weathering', 'Replacement Stone', 'Restoration', 'Condition'
    ]
                active_fields = ['Site ID', 'Site Name', 'Country']
                for bf in base_fields:
                    active_fields.extend([bf, f"{bf}_Ref", f"{bf}_Ext"])
                active_fields.extend(['UNESCO Mention', 'Other references'])
                    
                valid_cols = [c for c in active_fields if c in current_db.columns]
                    
                safe_unesco_id = str(unesco_id).replace('.0', '')
                current_db['safe_id'] = current_db['Site ID'].astype(str).str.replace('.0', '', regex=False)
                site_db = current_db[current_db['safe_id'] == safe_unesco_id][valid_cols].copy()
                    
                if site_db.empty:
                    st.info("No manual data has been saved for this site yet. Start typing and hit save!")
                else:
                    display_df = site_db.T
                    display_df.columns = ["Value"]
                    display_df["Value"] = display_df["Value"].astype(str).replace('nan', '')
                    st.dataframe(display_df, use_container_width=True)
            except Exception as e:
                st.warning("Database not found or empty.")
                    


    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    def format_unesco_headers(text):
        if not text or pd.isna(text): return ""
            
        # Pre-process weird formatting where colon is pushed to next line, or is missing entirely!
        # Ensure it becomes "Criterion (ii):\n\n"
        text = re.sub(r'(Criterion\s*\([ivx]+\))\s*\\?n*\s*:?\s*\\?n*', r'\1:\n\n', text, flags=re.IGNORECASE)
            
        # Bold the main headings (handling possible \n strings from raw dataset)
        headings = [
            r'Brief synthesis',
            r'Integrity',
            r'Authenticity',
            r'Protection and management requirements'
        ]
            
        for h in headings:
            # Match the heading at the start of a line or surrounded by spaces/newlines. 
            # Handle optional trailing colon.
            # Force a double newline (\n\n) after the heading so it sits on its own line like UNESCO.
            text = re.sub(rf'(?i)(^|\n|\\n|\s)({h})\s*:?\s*(\n|\\n|$)?', r'\1<strong>\2</strong>\n\n', text)
                
        # Bold the criteria
        text = re.sub(r'(?i)(^|\n|\\n|\s)(Criterion\s*\([ivx]+\):)', r'\1<strong>\2</strong>', text)
            
        return text
    
    # ==========================================
    # SECTION 3: OUV HIGHLIGHTING
    # ==========================================
    st.markdown("## 📄 Outstanding Universal Value (OUV)")
    
    ouv_text = site_data.get('ouv_statement', '')
    if pd.notna(ouv_text) and ouv_text:
        formatted_ouv = format_unesco_headers(ouv_text)
        highlighted_ouv = highlight_text(formatted_ouv, all_stones_list)
            
        st.markdown("""<span style='font-size: 0.9em; color: gray;'>*(Tip: To drag and drop text, first highlight the text, let go of the mouse, then click and drag the highlighted area into the form)*</span>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="user-select: text; -webkit-user-select: text; cursor: text; background-color: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); line-height: 1.8; font-size: 1.1em; border-top: 4px solid #4e4376;">
            {highlighted_ouv}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No OUV Statement available for this site.")
    st.markdown("<br><hr>", unsafe_allow_html=True)
    


# ==========================================
# MAIN APP ROUTING
# ==========================================
df = load_monument_data()
notes = load_notes()

if df.empty:
    st.error("Could not load dataset. Please check the file path.")
    st.stop()

st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", ["🏠 Home Statistics", "🏛️ Site Explorer"])
st.sidebar.markdown("---")

if page == "🏠 Home Statistics":
    render_home_page(df)
else:
    render_site_explorer(df, notes)
