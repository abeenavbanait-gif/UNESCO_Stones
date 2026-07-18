import streamlit as st
import pandas as pd
import re
from data_manager import load_monument_data, load_notes, save_note, get_global_stats, get_manual_data_for_site, save_manual_data
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
    col_chart1, col_chart2, col_chart3 = st.columns(3)
    with col_chart1:
        st.markdown("### 📊 Sites by Region")
        region_counts = df['region'].value_counts().reset_index()
        region_counts.columns = ['Region', 'Count']
        fig_pie = px.pie(region_counts, values='Count', names='Region', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_layout(
            legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_chart2:
        st.markdown("### 🪨 Rock Class Distribution")
        # Calculate rock class distribution
        class_counts = {"Igneous": 0, "Metamorphic": 0, "Sedimentary": 0}
        for val in df['stone_geological_class'].dropna():
            for rock_class in val.split(';'):
                rc = rock_class.strip().capitalize()
                if rc in class_counts:
                    class_counts[rc] += 1
        
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
            st.info("No rock class data available.")
            
    with col_chart3:
        st.markdown("### 🪨 Top 15 Most Common Stones")
        # Flatten stone types
        stone_list = []
        for s in df['stone_types_found'].dropna():
            stone_list.extend([stn.strip().title() for stn in s.split(';') if stn.strip()])
        stone_counts = pd.Series(stone_list).value_counts().head(15).reset_index()
        stone_counts.columns = ['Stone', 'Count']
        
        fig_bar = px.bar(stone_counts, x='Count', y='Stone', orientation='h', color='Count', color_continuous_scale='Viridis')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
        
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
        selected = st.session_state.site_selector
        st.session_state.current_index = site_options.index(selected)
    
    selected_site_name = st.sidebar.selectbox(
        "Select a Site to Study", 
        site_options, 
        index=st.session_state.current_index,
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
    st.markdown(f"""
    <div class="details-bar">
        <h1 style="margin-top:0px; margin-bottom:5px;">🏛️ {site_data['site_name']}</h1>
        <p style="font-size: 1.1em; margin-bottom: 15px;">
            <strong>UNESCO ID:</strong> {unesco_id} &nbsp;|&nbsp; 
            <strong>Country:</strong> {site_data['country']} &nbsp;|&nbsp; 
            <strong>Year:</strong> {site_data.get('year_inscribed', 'N/A')} &nbsp;|&nbsp; 
            <strong>Score:</strong> {site_data.get('score', 'N/A')}
        </p>
        <div>
            <a href="{unesco_url}" target="_blank" style="margin-right: 15px;">🔗 View Official UNESCO Dossier</a>
            <a href="{unesco_url}/gallery/" target="_blank" style="margin-right: 15px;">🖼️ View Full UNESCO Gallery</a>
            <a href="{maps_url}" target="_blank">🗺️ Open in Google Maps</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
    st.markdown("## ✍️ Manual Data Entry Form")
    st.markdown("Use this form to build out the master database while reviewing the site documents.")
    
    manual_data = get_manual_data_for_site(unesco_id)
    
    with st.form(key=f"manual_data_form_{unesco_id}"):
        with st.expander("🏛️ A. Monument Information", expanded=True):
            col1, col2 = st.columns(2)
            arch_type = col1.text_input("Architecture Type", value=manual_data.get('Architecture Type', ''))
            const_period = col2.text_input("Construction Period", value=manual_data.get('Construction Period', ''))
            civilization = col1.text_input("Civilization", value=manual_data.get('Civilization', ''))
            
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
            if existing_crit:
                for opt in CRITERIA_OPTIONS:
                    numeral = opt.split(' ')[0] # extracts "(i)", "(ii)", etc.
                    # check if numeral is in existing_crit, and it's an exact match
                    # e.g. "(i)" is in "(i)", but we don't want "(i)" to match "(iii)"
                    # since existing format is usually "(i)(ii)", we can just check if numeral in existing_crit
                    # Wait, "(i)" is inside "(ii)" and "(iii)" and "(iv)".
                    # We should parse existing_crit properly:
                    import re
                    # extract all matches like (i), (ii), etc
                    found_numerals = re.findall(r'\([ivx]+\)', existing_crit.lower())
                    if numeral.lower() in found_numerals:
                        default_crits.append(opt)
                        
            unesco_crit_list = col2.multiselect("UNESCO Criteria", options=CRITERIA_OPTIONS, default=default_crits)
            # We will save the joined full text strings so you have the statements in your CSV
            unesco_crit = " | ".join(unesco_crit_list)
            
            
        with st.expander("🪨 B. Geological Materials"):
            col1, col2 = st.columns(2)
            major_stone = col1.text_input("Major Stone", value=manual_data.get('Major Stone', ''))
            secondary_stone = col2.text_input("Secondary Stone", value=manual_data.get('Secondary Stone', ''))
            local_name = col1.text_input("Local Stone Name", value=manual_data.get('Local Stone Name', ''))
            lithology = col2.text_input("Lithology", value=manual_data.get('Lithology', ''))
            geo_age = col1.text_input("Geological Age", value=manual_data.get('Geological Age', ''))
            formation = col2.text_input("Formation", value=manual_data.get('Formation', ''))
            colour = col1.text_input("Colour", value=manual_data.get('Colour', ''))
            texture = col2.text_input("Texture", value=manual_data.get('Texture', ''))
            minerals = col1.text_input("Minerals", value=manual_data.get('Minerals', ''))
            
        with st.expander("🗺️ C. Provenance"):
            col1, col2 = st.columns(2)
            quarry = col1.text_input("Quarry", value=manual_data.get('Quarry', ''))
            quarry_country = col2.text_input("Quarry Country", value=manual_data.get('Quarry Country', ''))
            local_vs_imp = col1.selectbox("Local vs Imported", ["", "Local", "Imported", "Unknown"], index=["", "Local", "Imported", "Unknown"].index(manual_data.get('Local vs Imported', '')) if manual_data.get('Local vs Imported', '') in ["", "Local", "Imported", "Unknown"] else 0)
            transport_dist = col2.text_input("Transport Distance", value=manual_data.get('Transport Distance', ''))
            
        with st.expander("🏗️ D. Architectural Use"):
            col1, col2 = st.columns(2)
            struct_use = col1.text_input("Structural Use", value=manual_data.get('Structural Use', ''))
            dec_use = col2.text_input("Decorative Use", value=manual_data.get('Decorative Use', ''))
            masonry = col1.text_input("Masonry Technique", value=manual_data.get('Masonry Technique', ''))
            
        with st.expander("🛠️ E. Conservation"):
            col1, col2 = st.columns(2)
            weathering = col1.text_input("Weathering", value=manual_data.get('Weathering', ''))
            replacement = col2.text_input("Replacement Stone", value=manual_data.get('Replacement Stone', ''))
            restoration = col1.text_input("Restoration", value=manual_data.get('Restoration', ''))
            condition = col2.selectbox("Condition", ["", "Excellent", "Good", "Moderate", "Poor"], index=["", "Excellent", "Good", "Moderate", "Poor"].index(manual_data.get('Condition', '')) if manual_data.get('Condition', '') in ["", "Excellent", "Good", "Moderate", "Poor"] else 0)
            
        with st.expander("💎 F. Heritage Stone"):
            col1, col2 = st.columns(2)
            ghsr = col1.selectbox("GHSR", ["", "Yes", "No"], index=["", "Yes", "No"].index(manual_data.get('GHSR', '')) if manual_data.get('GHSR', '') in ["", "Yes", "No"] else 0)
            heritage_cand = col2.selectbox("Heritage Stone Candidate", ["", "Yes", "No"], index=["", "Yes", "No"].index(manual_data.get('Heritage Stone Candidate', '')) if manual_data.get('Heritage Stone Candidate', '') in ["", "Yes", "No"] else 0)
            geo_val = col1.selectbox("Geoheritage Value", ["", "High", "Medium", "Low"], index=["", "High", "Medium", "Low"].index(manual_data.get('Geoheritage Value', '')) if manual_data.get('Geoheritage Value', '') in ["", "High", "Medium", "Low"] else 0)
            
        with st.expander("📚 G. Sources"):
            col1, col2 = st.columns(2)
            unesco_mention = col1.selectbox("UNESCO Mention", ["", "Yes", "No"], index=["", "Yes", "No"].index(manual_data.get('UNESCO Mention', '')) if manual_data.get('UNESCO Mention', '') in ["", "Yes", "No"] else 0)
            wiki_mention = col2.selectbox("Wikipedia Mention", ["", "Yes", "No"], index=["", "Yes", "No"].index(manual_data.get('Wikipedia Mention', '')) if manual_data.get('Wikipedia Mention', '') in ["", "Yes", "No"] else 0)
            papers = col1.text_input("Research Papers", value=manual_data.get('Research Papers', ''))
            confidence = col2.selectbox("Confidence Score", ["", "High", "Medium", "Low"], index=["", "High", "Medium", "Low"].index(manual_data.get('Confidence Score', '')) if manual_data.get('Confidence Score', '') in ["", "High", "Medium", "Low"] else 0)
            
        submit_btn = st.form_submit_button("💾 Save Data to CSV", type="primary")
        if submit_btn:
            form_data = {
                'Architecture Type': arch_type,
                'Construction Period': const_period,
                'Civilization': civilization,
                'UNESCO Criteria': unesco_crit,
                'Major Stone': major_stone,
                'Secondary Stone': secondary_stone,
                'Local Stone Name': local_name,
                'Lithology': lithology,
                'Geological Age': geo_age,
                'Formation': formation,
                'Colour': colour,
                'Texture': texture,
                'Minerals': minerals,
                'Quarry': quarry,
                'Quarry Country': quarry_country,
                'Local vs Imported': local_vs_imp,
                'Transport Distance': transport_dist,
                'Structural Use': struct_use,
                'Decorative Use': dec_use,
                'Masonry Technique': masonry,
                'Weathering': weathering,
                'Replacement Stone': replacement,
                'Restoration': restoration,
                'Condition': condition,
                'GHSR': ghsr,
                'Heritage Stone Candidate': heritage_cand,
                'Geoheritage Value': geo_val,
                'UNESCO Mention': unesco_mention,
                'Wikipedia Mention': wiki_mention,
                'Research Papers': papers,
                'Confidence Score': confidence
            }
            if save_manual_data(unesco_id, form_data):
                st.success("Data successfully saved to UNESCO_Stones_Manual_Data.csv!")
            else:
                st.error("Failed to save data. Please check the logs.")
    
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
        
        st.markdown(f"""
        <div style="background-color: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); line-height: 1.8; font-size: 1.1em; border-top: 4px solid #4e4376;">
            {highlighted_ouv}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No OUV Statement available for this site.")
    
    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # ==========================================
    # SECTION 5: CHAT WITH DOSSIER (RAG)
    # ==========================================
    st.markdown("## 🤖 Chat with Official Dossier (RAG)")
    st.markdown("Interact directly with this site's official UNESCO nomination file using AI.")
    
    # Use an expander to keep the UI clean
    with st.expander("Expand to Chat", expanded=False):
        if st.button("📥 Load Dossier (Downloads & Embeds PDF)"):
            with st.spinner("Downloading and embedding PDF... This may take a minute."):
                success, msg = asyncio.run(ingest_dossier(unesco_id))
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
                    
        st.markdown("---")
        
        question = st.text_input("Ask a question about the materials, geology, or construction:")
        if st.button("Ask AI"):
            if not api_key:
                st.error("Please enter your Gemini API Key in the sidebar.")
            elif not question:
                st.warning("Please enter a question.")
            else:
                with st.spinner("Analyzing dossier..."):
                    answer = ask_question(unesco_id, question, api_key)
                    st.markdown(f"**Answer:**\n\n{answer}")
    


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
