import streamlit as st
import pandas as pd
import re
from data_manager import load_monument_data, load_notes, save_note, get_global_stats
import asyncio
from rag_pipeline import ingest_dossier, ask_question
from graph_rag_pipeline import ingest_custom_pdf_graph, ask_graph_question
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
df = load_monument_data()
notes = load_notes()

if df.empty:
    st.error("Could not load dataset. Please check the file path.")
    st.stop()


def render_home_page(df):
    st.title("🌍 Global Heritage Stones Dashboard")
    st.markdown("Welcome to the analytical overview of built heritage and construction materials across UNESCO Cultural Sites.")
    
    st.markdown("---")
    
    # Fetch global stats
    g_stats = get_global_stats()
    
    # Global Overview Breakdown
    st.markdown(f"""
    <div style="background-color: #f1f8ff; padding: 15px; border-radius: 8px; border-left: 4px solid #0366d6; margin-bottom: 20px;">
        <h4 style="margin-top: 0; color: #0366d6;">Global UNESCO Overview</h4>
        <p style="margin-bottom: 0;">
            Out of <strong>{g_stats['total_unesco']}</strong> total World Heritage Sites, there are: 
            <strong>{g_stats['cultural']} Cultural</strong>, <strong>{g_stats['natural']} Natural</strong>, and <strong>{g_stats['mixed']} Mixed</strong> sites.<br>
            Within the {g_stats['cultural']} Cultural sites, <strong>{len(df)}</strong> were classified as <em>Built Monuments</em>.<br>
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
    col_chart1, col_chart2 = st.columns(2)
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
    st.sidebar.markdown("### 🤖 RAG Configuration")
    api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Required to chat with the dossier")
    
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
        highlighted = text
        for term in terms:
            if term:
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                highlighted = pattern.sub(f'<span class="highlight-stone">{term}</span>', highlighted)
        return highlighted.replace('\\n', '<br><br>').replace('\n', '<br><br>')
    
    # ==========================================
    # SECTION 2: SITE DESCRIPTION
    # ==========================================
    st.markdown("## 🌍 Site Description")
    brief_desc = site_data.get('brief_description', '')
    if pd.notna(brief_desc) and brief_desc:
        highlighted_brief = highlight_text(brief_desc, all_stones_list)
        st.markdown(f"""
        <div style="background-color: #e8f4f8; padding: 20px; border-radius: 12px; border-left: 4px solid #3498db; line-height: 1.6; font-size: 1.05em;">
            {highlighted_brief}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No brief description available for this site.")
    
    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # ==========================================
    # SECTION 3: OUV HIGHLIGHTING
    # ==========================================
    st.markdown("## 📄 Outstanding Universal Value (OUV)")
    
    ouv_text = site_data.get('ouv_statement', '')
    if pd.notna(ouv_text) and ouv_text:
        highlighted_ouv = highlight_text(ouv_text, all_stones_list)
        
        st.markdown(f"""
        <div style="background-color: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); line-height: 1.8; font-size: 1.1em; border-top: 4px solid #4e4376;">
            {highlighted_ouv}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No OUV Statement available for this site.")
    
    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # ==========================================
    # SECTION 4: NOTE TAKING MODULE
    # ==========================================
    st.markdown("## 📝 Researcher Notes")
    current_note = notes.get(unesco_id, "")
    
    new_note = st.text_area("Observations, confirmations, or dossier excerpts for this site:", value=current_note, height=150, label_visibility="collapsed")
    
    if st.button("💾 Save Notes", type="primary"):
        if save_note(unesco_id, new_note):
            st.success("Notes saved successfully! (They will persist when you return to this site)")
    
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
    # SECTION 6: CUSTOM DOCUMENT GRAPHRAG
    # ==========================================
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("## 🕸️ Custom Document GraphRAG")
    st.markdown("Upload any architectural PDF to build a semantic Knowledge Graph and chat with it.")
    
    with st.expander("Expand to Upload & Chat with Graph", expanded=False):
        uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
        
        if uploaded_file is not None:
            if st.button("🏗️ Build Knowledge Graph (Takes 1-2 mins)"):
                if not api_key:
                    st.error("Please enter your Gemini API Key in the sidebar first.")
                else:
                    with st.spinner("Extracting entities and building Graph using Gemini..."):
                        try:
                            nodes, edges = ingest_custom_pdf_graph(uploaded_file.read(), api_key)
                            st.success(f"Graph built successfully! Found {nodes} entities and {edges} relationships.")
                        except Exception as e:
                            st.error(f"Error building graph: {e}")
            
            st.markdown("---")
            graph_q = st.text_input("Ask a question about your uploaded document's graph:")
            if st.button("Ask Graph AI"):
                if not api_key:
                    st.error("Please enter your Gemini API Key in the sidebar.")
                elif not graph_q:
                    st.warning("Please enter a question.")
                else:
                    with st.spinner("Traversing Knowledge Graph..."):
                        try:
                            ans, ctx = ask_graph_question(graph_q, api_key)
                            st.markdown(f"**Answer:**\n\n{ans}")
                            with st.expander("View Graph Context Used"):
                                st.text(ctx)
                        except Exception as e:
                            st.error(f"Error querying graph: {e}")
    


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
