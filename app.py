import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import math

# ── Configuration ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HarborHome | Boston Public Resource Hub",
    page_icon="🏘️",
    layout="wide"
)

# ── Enhanced Styling (Action-Oriented & Modern) ──────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    [data-testid="stSidebar"] { display: none; }
    .main .block-container { padding-top: 1.5rem; max-width: 1250px; }

    /* Navigation Buttons */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        background-color: #F1F5F9;
        border-radius: 8px;
        padding: 10px 25px;
        height: auto;
    }
    .stTabs [aria-selected="true"] { background-color: #3B82F6 !important; color: white !important; }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 3rem;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Action Buttons for Home Page */
    .action-btn {
        background: white;
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #E2E8F0;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .action-btn:hover { border-color: #3B82F6; transform: translateY(-5px); }
</style>
""", unsafe_allow_html=True)

# ── DATA EXPANSION (Housing, Medical, SNAP, Utilities) ───────────────────────
HOUSING = [
    {"name": "Roxbury Crossing Apts", "lat": 42.3315, "lon": -71.0952, "rent": 950, "beds": 2, "type": "Subsidized", "waitlist": "Open"},
    {"name": "JP Common Ground", "lat": 42.3100, "lon": -71.1130, "rent": 875, "beds": 1, "type": "Affordable", "waitlist": "Open"},
    {"name": "Dorchester Arms", "lat": 42.3010, "lon": -71.0680, "rent": 800, "beds": 2, "type": "Subsidized", "waitlist": "Closed"},
    {"name": "Mattapan Village", "lat": 42.2770, "lon": -71.0920, "rent": 1100, "beds": 3, "type": "Affordable", "waitlist": "Open"},
    {"name": "Eastie Waterfront", "lat": 42.3720, "lon": -71.0350, "rent": 900, "beds": 2, "type": "Affordable", "waitlist": "Open"},
    {"name": "South End Haven", "lat": 42.3380, "lon": -71.0750, "rent": 1200, "beds": 1, "type": "Market Rate (Low)", "waitlist": "Open"}
]

MEDICAL = [
    {"name": "Whittier Street Health", "lat": 42.3320, "lon": -71.0920, "spec": "Primary/Dental"},
    {"name": "Codman Square Health", "lat": 42.2900, "lon": -71.0690, "spec": "Urgent Care"},
    {"name": "Dimock Center", "lat": 42.3180, "lon": -71.0980, "spec": "Mental Health/Clinic"},
    {"name": "DotHouse Health", "lat": 42.3080, "lon": -71.0580, "spec": "Full Service"},
    {"name": "Boston Medical Center", "lat": 42.3350, "lon": -71.0740, "spec": "Emergency/Hospital"},
    {"name": "Upham's Corner Health", "lat": 42.3160, "lon": -71.0620, "spec": "Community Clinic"}
]

SNAP_STORES = [
    {"name": "Stop & Shop (Roxbury)", "lat": 42.3290, "lon": -71.0880},
    {"name": "Daily Table (Dorchester)", "lat": 42.3075, "lon": -71.0685},
    {"name": "Price Rite (Hyde Park)", "lat": 42.2490, "lon": -71.1250},
    {"name": "Tropical Foods", "lat": 42.3310, "lon": -71.0820},
    {"name": "Market Basket (Chelsea/Eastie)", "lat": 42.3950, "lon": -71.0350},
    {"name": "Save-A-Lot", "lat": 42.2850, "lon": -71.0720}
]

# ── Main Layout ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h1 style="color:white; margin:0; font-size: 2.8rem;">HarborHome Boston 🏠</h1>
    <p style="font-size:1.2rem; margin-top:10px; opacity:0.95;">The Open-Access Portal for Housing, Health, and Basic Needs.</p>
</div>
""", unsafe_allow_html=True)

tab_home, tab_house, tab_res, tab_news = st.tabs(["🏠 Welcome", "🔍 Housing Search", "📍 Resource Finder", "📰 Community Updates"])

# ── TAB 1: HOME (With Action Buttons) ────────────────────────────────────────
with tab_home:
    st.markdown("### How can we help you today?")
    st.write("Select a service below to begin your search. All data is real-time and open to the public.")
    
    # Custom CSS for columns that look like buttons
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        st.markdown("""<div class="action-btn"><h1>🏘️</h1><h3>Find a Home</h3><p>Filter by rent, beds, and proximity to schools.</p></div>""", unsafe_allow_html=True)
        if st.button("Start Housing Search", use_container_width=True):
            st.info("Click the 'Housing Search' tab at the top!")
            
    with btn_col2:
        st.markdown("""<div class="action-btn"><h1>🩺</h1><h3>Get Medical Care</h3><p>Locate clinics and urgent care in your neighborhood.</p></div>""", unsafe_allow_html=True)
        if st.button("Locate Health Centers", use_container_width=True):
            st.info("Click the 'Resource Finder' tab and filter for Medical.")

    with btn_col3:
        st.markdown("""<div class="action-btn"><h1>🛒</h1><h3>Food & Support</h3><p>Find stores that accept SNAP and local food pantries.</p></div>""", unsafe_allow_html=True)
        if st.button("Find Food Resources", use_container_width=True):
            st.info("Click the 'Resource Finder' tab and filter for SNAP.")

    st.divider()
    st.subheader("🌐 Accessibility Options")
    lang = st.radio("Primary Language", ["English", "Español", "Tiếng Việt", "Kreyòl Ayisyen"], horizontal=True)

# ── TAB 2: HOUSING SEARCH (Filters Restored) ─────────────────────────────────
with tab_house:
    st.subheader("Comprehensive Housing Search")
    
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        max_rent = st.slider("Maximum Monthly Rent", 500, 2000, 1200)
    with f_col2:
        min_beds = st.selectbox("Minimum Bedrooms", [1, 2, 3, 4], index=1)
    with f_col3:
        h_type = st.multiselect("Housing Type", ["Subsidized", "Affordable", "Market Rate (Low)"], default=["Subsidized", "Affordable"])

    # Filter Logic
    filtered_housing = [h for h in HOUSING if h['rent'] <= max_rent and h['beds'] >= min_beds and h['type'] in h_type]

    h_left, h_right = st.columns([2, 1])
    with h_left:
        m = folium.Map(location=[42.3200, -71.0800], zoom_start=12, tiles="CartoDB positron")
        for h in filtered_housing:
            folium.Marker([h["lat"], h["lon"]], tooltip=h['name'], icon=folium.Icon(color="green", icon="home")).add_to(m)
        st_folium(m, height=500, use_container_width=True)

    with h_right:
        st.write(f"**Found {len(filtered_housing)} matches**")
        for h in filtered_housing:
            st.markdown(f"""
            <div style="background:white; padding:12px; border-radius:10px; border:1px solid #E2E8F0; margin-bottom:10px;">
                <h4 style="margin:0;">{h['name']}</h4>
                <p style="margin:0; font-size:0.9rem;">${h['rent']}/mo • {h['beds']} Bed • {h['type']}</p>
                <small style="color:blue;">Waitlist: {h['waitlist']}</small>
            </div>
            """, unsafe_allow_html=True)

# ── TAB 3: RESOURCE FINDER (Medical + SNAP + Infrastructure) ──────────────────
with tab_res:
    st.subheader("📍 Neighborhood Support Map")
    
    res_type = st.multiselect("View Local Resources", 
                              ["Medical Centers 🩺", "SNAP Retailers 🛒", "Public WiFi 📶", "Water Stations 💧"], 
                              default=["Medical Centers 🩺", "SNAP Retailers 🛒"])
    
    m2 = folium.Map(location=[42.3100, -71.0700], zoom_start=13, tiles="CartoDB positron")
    
    if "Medical Centers 🩺" in res_type:
        for med in MEDICAL:
            folium.Marker([med["lat"], med["lon"]], popup=f"{med['name']} ({med['spec']})", icon=folium.Icon(color="red", icon="plus")).add_to(m2)
    
    if "SNAP Retailers 🛒" in res_type:
        for s in SNAP_STORES:
            folium.Marker([s["lat"], s["lon"]], popup=s["name"], icon=folium.Icon(color="orange", icon="shopping-cart")).add_to(m2)

    st_folium(m2, height=550, use_container_width=True)

# ── TAB 4: NEWS ──────────────────────────────────────────────────────────────
with tab_news:
    st.header("Community Bulletin")
    n_col1, n_col2 = st.columns(2)
    with n_col1:
        st.info("**May 5:** Public Hearing on Dorchester Rent Stabilization @ 6PM (City Hall)")
        st.success("**May 10:** Free Community Health Fair @ The Dimock Center")
    with n_col2:
        st.warning("**May 12:** Deadline to apply for Fuel Assistance (LIHEAP)")
        st.error("**Alert:** Water Main Maintenance in East Boston on May 15")

        