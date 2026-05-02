import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# ── Configuration & State ───────────────────────────────────────────────────
st.set_page_config(page_title="HarborHome Boston", page_icon="🏘️", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = "Home"

def ch_page(name):
    st.session_state.page = name

# ── Visibility & Style Fixes ────────────────────────────────────────────────
st.markdown("""
<style>
    /* Force high-contrast colors to fix visibility issues */
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    [data-testid="stSidebar"] { display: none; }
    
    /* Modern Navigation Bar */
    .nav-bar {
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 1rem;
        background: #1E293B;
        border-bottom: 2px solid #3B82F6;
        margin-bottom: 2rem;
    }
    
    /* High-Contrast Info Cards */
    .info-card {
        background: #1E293B;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        color: #F8FAFC !important;
        margin-bottom: 1rem;
    }
    .info-card h4 { color: #3B82F6 !important; margin: 0; }
    .info-card p { color: #CBD5E1 !important; margin: 5px 0; }

    /* Action Buttons */
    .action-box {
        background: #1E293B;
        padding: 2rem;
        border-radius: 16px;
        border: 2px solid #334155;
        text-align: center;
        transition: 0.3s;
    }
    .action-box:hover { border-color: #3B82F6; background: #263449; }
</style>
""", unsafe_allow_html=True)

# ── MASSIVE DATASET ─────────────────────────────────────────────────────────
HOUSING = [
    {"name": "Roxbury Crossing", "lat": 42.3315, "lon": -71.0952, "rent": 950, "beds": 2, "area": "Roxbury", "type": "Subsidized"},
    {"name": "JP Commons", "lat": 42.3100, "lon": -71.1130, "rent": 1100, "beds": 1, "area": "Jamaica Plain", "type": "Affordable"},
    {"name": "Dorchester Arms", "lat": 42.3010, "lon": -71.0680, "rent": 850, "beds": 2, "area": "Dorchester", "type": "Subsidized"},
    {"name": "Mattapan Village", "lat": 42.2770, "lon": -71.0920, "rent": 1300, "beds": 3, "area": "Mattapan", "type": "Market Rate (Low)"},
    {"name": "Eastie Waterfront", "lat": 42.3720, "lon": -71.0350, "rent": 1050, "beds": 2, "area": "East Boston", "type": "Affordable"},
    {"name": "South End Haven", "lat": 42.3380, "lon": -71.0750, "rent": 1400, "beds": 1, "area": "South End", "type": "Affordable"}
]

MEDICAL = [
    {"name": "Boston Medical Center", "lat": 42.3350, "lon": -71.0740, "type": "Hospital / ER"},
    {"name": "Whittier Street Health", "lat": 42.3320, "lon": -71.0920, "type": "Clinic / Dental"},
    {"name": "Codman Square Health", "lat": 42.2900, "lon": -71.0690, "type": "Urgent Care"},
    {"name": "DotHouse Health", "lat": 42.3080, "lon": -71.0580, "type": "General Practice"},
    {"name": "Mass General Hospital", "lat": 42.3620, "lon": -71.0690, "type": "Hospital / ER"},
    {"name": "Dimock Center", "lat": 42.3180, "lon": -71.0980, "type": "Mental Health"},
    {"name": "Fenway Health", "lat": 42.3440, "lon": -71.0910, "type": "Specialty Care"}
]

SNAP = [
    {"name": "Stop & Shop (Dorchester)", "lat": 42.3210, "lon": -71.0650},
    {"name": "Daily Table (Roxbury)", "lat": 42.3295, "lon": -71.0845},
    {"name": "Tropical Foods", "lat": 42.3310, "lon": -71.0820},
    {"name": "Market Basket (Chelsea)", "lat": 42.3950, "lon": -71.0350},
    {"name": "Price Rite (Hyde Park)", "lat": 42.2490, "lon": -71.1250},
    {"name": "Save-A-Lot (Mattapan)", "lat": 42.2850, "lon": -71.0720},
    {"name": "Whole Foods (South End)", "lat": 42.3440, "lon": -71.0630}
]

# ── Navigation UI ──────────────────────────────────────────────────────────
st.title("HarborHome Boston 🏘️")
st.write("Community-Powered Resource & Housing Access Portal")

# Manual Navigation Bar
c1, c2, c3, c4 = st.columns(4)
if c1.button("🏠 Home", use_container_width=True): ch_page("Home")
if c2.button("🔍 Housing", use_container_width=True): ch_page("Housing")
if c3.button("📍 Resources", use_container_width=True): ch_page("Resources")
if c4.button("📰 News", use_container_width=True): ch_page("News")

st.divider()

# ── PAGE: HOME ──────────────────────────────────────────────────────────────
if st.session_state.page == "Home":
    st.subheader("Welcome to Your Neighborhood Hub")
    st.write("We help Boston residents find stable housing, affordable food, and free medical care.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="action-box"><h2>🏠</h2><h3>Housing Search</h3><p>Find waitlist-open apartments.</p></div>', unsafe_allow_html=True)
        if st.button("Browse Housing", use_container_width=True): ch_page("Housing")
    with col2:
        st.markdown('<div class="action-box"><h2>🩺</h2><h3>Medical Care</h3><p>Locate free clinics and ERs.</p></div>', unsafe_allow_html=True)
        if st.button("Find Care", use_container_width=True): ch_page("Resources")
    with col3:
        st.markdown('<div class="action-box"><h2>🛒</h2><h3>Food Access</h3><p>Find stores accepting SNAP.</p></div>', unsafe_allow_html=True)
        if st.button("Find Food", use_container_width=True): ch_page("Resources")

# ── PAGE: HOUSING (Filters Restored) ────────────────────────────────────────
elif st.session_state.page == "Housing":
    st.subheader("Explore Affordable Housing")
    
    with st.expander("⚙️ Filter Listings", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        max_r = f_col1.slider("Max Monthly Rent", 500, 2000, 1500)
        min_b = f_col2.selectbox("Minimum Bedrooms", [1, 2, 3])
        h_type = f_col3.multiselect("Lease Type", ["Subsidized", "Affordable", "Market Rate (Low)"], default=["Subsidized", "Affordable"])
    
    filtered = [h for h in HOUSING if h['rent'] <= max_r and h['beds'] >= min_b and h['type'] in h_type]
    
    map_col, list_col = st.columns([2, 1])
    with map_col:
        m1 = folium.Map(location=[42.3300, -71.0800], zoom_start=12, tiles="CartoDB dark_matter")
        for h in filtered:
            folium.Marker([h["lat"], h["lon"]], tooltip=h['name'], icon=folium.Icon(color="blue", icon="home")).add_to(m1)
        st_folium(m1, height=500, use_container_width=True)
    
    with list_col:
        st.write(f"**{len(filtered)} Matches Found**")
        for h in filtered:
            st.markdown(f"""<div class="info-card"><h4>{h['name']}</h4><p>{h['area']} • {h['beds']} Bed • ${h['rent']}/mo</p><small>{h['type']}</small></div>""", unsafe_allow_html=True)

# ── PAGE: RESOURCES (Medical + SNAP) ────────────────────────────────────────
elif st.session_state.page == "Resources":
    st.subheader("Health & Nutrition Resources")
    view = st.multiselect("Show on Map", ["Medical Centers 🩺", "SNAP Retailers 🛒"], default=["Medical Centers 🩺", "SNAP Retailers 🛒"])
    
    m2 = folium.Map(location=[42.3300, -71.0800], zoom_start=12, tiles="CartoDB dark_matter")
    
    if "Medical Centers 🩺" in view:
        for med in MEDICAL:
            folium.Marker([med["lat"], med["lon"]], popup=med["name"], tooltip=med["type"], icon=folium.Icon(color="red", icon="plus-sign")).add_to(m2)
    
    if "SNAP Retailers 🛒" in view:
        for s in SNAP:
            folium.Marker([s["lat"], s["lon"]], popup=s["name"], icon=folium.Icon(color="orange", icon="shopping-cart")).add_to(m2)
            
    st_folium(m2, height=600, use_container_width=True)

# ── PAGE: NEWS ──────────────────────────────────────────────────────────────
elif st.session_state.page == "News":
    st.subheader("Community Bulletin")
    st.info("**May 10:** Free Community Health Fair @ The Dimock Center")
    st.warning("**May 12:** Deadline to apply for Fuel Assistance (LIHEAP)")
    st.error("**Maintenance:** Water Main work in East Boston on May 15")

    