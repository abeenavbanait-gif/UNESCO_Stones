import streamlit as st
import pandas as pd
import re
import urllib.request
import urllib.parse
import ssl
import json
from data_manager import load_monument_data, load_notes, save_note

# Page Config
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
    
    /* Force Dropdown and Search Inputs to be readable and RED */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 2px solid #ff4b4b !important; /* Red border */
        border-radius: 6px;
    }
    
    div[data-baseweb="input"] input, div[data-baseweb="select"] div {
        color: #333333 !important;
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

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_wiki_images(site_name):
    """Fetch multiple images dynamically from Wikimedia API using urllib to avoid macOS segfaults."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        def fetch_json(url):
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
            response = urllib.request.urlopen(req, context=ctx)
            return json.loads(response.read())
            
        # First attempt: exact match
        url = f'https://en.wikipedia.org/w/api.php?action=query&prop=images&titles={urllib.parse.quote(site_name)}&format=json&imlimit=15'
        res = fetch_json(url)
        pages = res.get('query', {}).get('pages', {})
        page_id = list(pages.keys())[0]
        
        # Second attempt: search API fallback for long UNESCO names
        if page_id == '-1':
            search_url = f'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(site_name)}&format=json&utf8='
            search_res = fetch_json(search_url)
            search_results = search_res.get('query', {}).get('search', [])
            
            if search_results:
                best_match_title = search_results[0]['title']
                url = f'https://en.wikipedia.org/w/api.php?action=query&prop=images&titles={urllib.parse.quote(best_match_title)}&format=json&imlimit=15'
                res = fetch_json(url)
                pages = res.get('query', {}).get('pages', {})
                page_id = list(pages.keys())[0]
        
        if page_id != '-1':
            images = pages[page_id].get('images', [])
            # Filter out svg/gif, keep jpg/png
            image_titles = [img['title'] for img in images if img['title'].lower().endswith(('.jpg', '.png', '.jpeg'))]
            
            if image_titles:
                # Limit to 6 images for the sidebar gallery
                titles_str = '|'.join(image_titles[:6])
                img_url = f'https://en.wikipedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&titles={urllib.parse.quote(titles_str)}&format=json'
                img_res = fetch_json(img_url)
                
                img_pages = img_res.get('query', {}).get('pages', {})
                urls = []
                for p_id, p_data in img_pages.items():
                    if 'imageinfo' in p_data:
                        urls.append(p_data['imageinfo'][0]['url'])
                return urls
    except Exception as e:
        print(f"Image fetch error: {e}")
        pass
    return []

# Load Data
df = load_monument_data()
notes = load_notes()

if df.empty:
    st.error("Could not load dataset. Please check the file path.")
    st.stop()

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

def prev_site():
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1
    else:
        st.session_state.current_index = len(site_options) - 1

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
image_urls = fetch_wiki_images(site_data['site_name'])
if image_urls:
    st.sidebar.markdown("### 📸 Site Gallery")
    # Display images vertically in the sidebar, wrapping them in clickable links
    for img_url in image_urls:
        html_code = f'<a href="{img_url}" target="_blank"><img src="{img_url}" class="sidebar-gallery-img"></a>'
        st.sidebar.markdown(html_code, unsafe_allow_html=True)

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

st.markdown("<br><hr>", unsafe_allow_html=True)

# ==========================================
# SECTION 2: OUV HIGHLIGHTING
# ==========================================
st.markdown("## 📄 Outstanding Universal Value (OUV)")

ouv_text = site_data.get('ouv_statement', '')
if pd.notna(ouv_text) and ouv_text:
    all_stones_list = []
    for col in ['stone_types_found', 'named_trade_stones', 'decorative_minerals_found', 'architectural_elements_found', 'architecture_style_found']:
        val = site_data.get(col, '')
        if pd.notna(val) and val:
            all_stones_list.extend([s.strip() for s in val.split(';') if s.strip()])
            
    highlighted_text = ouv_text
    all_stones_list.sort(key=len, reverse=True)
    
    for term in all_stones_list:
        if term:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted_text = pattern.sub(f'<span class="highlight-stone">{term}</span>', highlighted_text)
            
    highlighted_text = highlighted_text.replace('\\n', '<br><br>').replace('\n', '<br><br>')
    
    st.markdown(f"""
    <div style="background-color: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); line-height: 1.8; font-size: 1.1em; border-top: 4px solid #4e4376;">
        {highlighted_text}
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("No OUV Statement available for this site.")

st.markdown("<br><hr>", unsafe_allow_html=True)

# ==========================================
# SECTION 3: NOTE TAKING MODULE
# ==========================================
st.markdown("## 📝 Researcher Notes")
current_note = notes.get(unesco_id, "")

new_note = st.text_area("Observations, confirmations, or dossier excerpts for this site:", value=current_note, height=150, label_visibility="collapsed")

if st.button("💾 Save Notes", type="primary"):
    if save_note(unesco_id, new_note):
        st.success("Notes saved successfully! (They will persist when you return to this site)")
