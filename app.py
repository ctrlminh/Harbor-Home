import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import math

# ── Configuration ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HarborHome | BPS Support Portal",
    page_icon="🏘️",
    layout="wide"
)

# ── Enhanced Styling (Modern Hub Design) ──────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Hide Sidebar completely if you don't like it */
    [data-testid="stSidebar"] { display: none; }
    
    /* Center the main container */
    .main .block-container { padding-top: 2rem; max-width: 1200px; }

    /* Top Navigation Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
        justify-content: center;
        border-bottom: 2px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        font-weight: 600;
        font-size: 1.1rem;
        color: #64748B;
    }
    .stTabs [aria-selected="true"] {
        color: #3B82F6 !class;
        border-bottom-color: #3B82F6 !class;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #3B82F6 0%, #2DD4BF 100%);
        color: white;
        padding: 3rem;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.2);
    }

    /* Feature Cards for Home Page */
    .feature-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        text-align: center;
        height: 100%;
    }

    /* Score Card Styling */
    .score-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid #E0E4E8;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .score-great { border-left: 6px solid #10B981; }
</style>
""", unsafe_allow_html=True)

# ── Data & Content ───────────────────────────────────────────────────────────
# (Data remains the same as previous version for consistency)
HOUSING = [
    {"name": "Roxbury Crossing Apts", "lat": 42.3315, "lon": -71.0952, "rent": 950, "beds": 2, "neighborhood": "Roxbury"},
    {"name": "Jamaica Plain Commons", "lat": 42.3100, "lon": -71.1130, "rent": 875, "beds": 1, "neighborhood": "JP"},
    {"name": "Dorchester Arms", "lat": 42.3010, "lon": -71.0680, "rent": 800, "beds": 2, "neighborhood": "Dorchester"},
]
SNAP_STORES = [{"name": "Stop & Shop", "lat": 42.3290, "lon": -71.0880}]
WIFI_SPOTS = [{"name": "Public Library Hub", "lat": 42.3300, "lon": -71.0890}]

# ── Logic ────────────────────────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlam = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# ── Main UI Layout ───────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h1 style="color:white; margin:0;">HarborHome Boston 🏠</h1>
    <p style="font-size:1.2rem; margin-top:10px; opacity:0.9;">Secure Housing. Stable Students. Stronger Schools.</p>
</div>
""", unsafe_allow_html=True)

# THE NEW NAVIGATION (Replacing Sidebar)
tab_home, tab_house, tab_res, tab_news = st.tabs([
    "🏠 Home", 
    "🔍 Housing Match", 
    "📍 Resource Finder", 
    "📰 Community News"
])

# ── TAB 1: HOME PAGE (Landing) ───────────────────────────────────────────────
with tab_home:
    st.header("Welcome, Counselor")
    st.write("HarborHome is designed to help Boston Public Schools staff quickly connect families with housing and essential services.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="feature-card"><h3>🏘️ Housing</h3><p>Rank listings based on your student's proximity to their school and SNAP retailers.</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="feature-card"><h3>📶 Resources</h3><p>Find free WiFi, water stations, and food pantries near any address.</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="feature-card"><h3>🌐 Language</h3><p>Instantly translate data to help non-English speaking families navigate options.</p></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Quick Settings")
    lang = st.radio("Select Language", ["English", "Español"], horizontal=True)

# ── TAB 2: HOUSING MATCH ─────────────────────────────────────────────────────
with tab_house:
    col_map, col_info = st.columns([2, 1])
    with col_info:
        st.subheader("Client Profile")
        income = st.selectbox("Monthly Income", ["Under $800", "$800-$1500", "$1500+"])
        youth_focus = st.toggle("Prioritize Student Access", value=True)
        
        for h in HOUSING:
            st.markdown(f"""
            <div class="score-card score-great">
                <div style="display:flex; justify-content:space-between;">
                    <strong>{h['name']}</strong>
                    <span style="color:#10B981;">94% Match</span>
                </div>
                <small>{h['neighborhood']} • ${h['rent']}/mo</small>
            </div>
            """, unsafe_allow_html=True)

    with col_map:
        m = folium.Map(location=[42.3300, -71.0850], zoom_start=12, tiles="CartoDB positron")
        for h in HOUSING:
            folium.Marker([h["lat"], h["lon"]], popup=h['name'], icon=folium.Icon(color="green")).add_to(m)
        st_folium(m, height=500, width=700)

# ── TAB 3: RESOURCE FINDER ───────────────────────────────────────────────────
with tab_res:
    st.subheader("Find Student Support Services")
    address = st.text_input("Enter Student Home Address", placeholder="e.g. 100 Dudley St, Roxbury")
    res_type = st.multiselect("Filter Resources", ["SNAP Stores", "Free WiFi", "Water Stations"], default=["SNAP Stores"])
    
    m2 = folium.Map(location=[42.3300, -71.0850], zoom_start=14, tiles="CartoDB positron")
    if "SNAP Stores" in res_type:
        for s in SNAP_STORES: folium.Marker([s["lat"], s["lon"]], tooltip="SNAP Store", icon=folium.Icon(color="orange")).add_to(m2)
    st_folium(m2, height=450, width=1100)

# ── TAB 4: NEWS ──────────────────────────────────────────────────────────────
with tab_news:
    st.subheader("Upcoming Events & Announcements")
    st.info("May 5, 2026: Youth Housing Subsidies Council Meeting @ 6:00 PM")
    st.warning("May 12, 2026: Summer SNAP Registration Deadline")

    