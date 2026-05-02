import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# ── Configuration ──────────────────────────────────────────────────────────
st.set_page_config(page_title="HarborHome Boston", page_icon="🏘️", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = "Home"

def ch_page(name):
    st.session_state.page = name

# ── Theme-Agnostic Styling ─────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        transition: background-color 0.3s ease;
    }

    /* Universal Info Cards: Works in Light & Dark */
    .info-card {
        background-color: rgba(128, 128, 128, 0.1); /* Semi-transparent */
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    .info-card:hover {
        transform: translateY(-2px);
        border-color: #3B82F6;
    }

    /* Dynamic Text Colors */
    /* Streamlit uses these variables automatically based on theme */
    .info-card h4 {
        color: var(--text-color);
        margin: 0;
        font-weight: 700;
    }
    .info-card p {
        color: var(--text-color);
        opacity: 0.8;
        margin: 5px 0;
    }

    /* Action Box for Home Page */
    .action-box {
        background-color: rgba(59, 130, 246, 0.1);
        padding: 2rem;
        border-radius: 16px;
        border: 2px solid rgba(59, 130, 246, 0.3);
        text-align: center;
        height: 100%;
    }
    
    /* Navigation bar spacing */
    .nav-container {
        display: flex;
        gap: 10px;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# ── DATASET (Keep your existing data here) ─────────────────────────────────
# ... (Medical, SNAP, and Housing lists from the previous code) ...

# ── Navigation UI ──────────────────────────────────────────────────────────
st.title("HarborHome Boston 🏘️")
st.caption("Secure Housing. Stable Students. Stronger Schools.")

# Navigation row using native buttons for better theme integration
c1, c2, c3, c4 = st.columns(4)
with c1: st.button("🏠 Home", use_container_width=True, on_click=ch_page, args=("Home",))
with c2: st.button("🔍 Housing", use_container_width=True, on_click=ch_page, args=("Housing",))
with c3: st.button("📍 Resources", use_container_width=True, on_click=ch_page, args=("Resources",))
with c4: st.button("📰 News", use_container_width=True, on_click=ch_page, args=("News",))

st.divider()

# ── Updated Map Logic (Auto-Theme) ──────────────────────────────────────────
# Inside your Housing/Resource pages, update the map tile logic:
# m = folium.Map(location=[42.33, -71.08], zoom_start=12, tiles="OpenStreetMap") 
# ^ "OpenStreetMap" is better for light/dark switching than "Dark Matter"
# ── NEW RESOURCE CATEGORIES ────────────────────────────────────────────────
WIFI_CENTERS = [
    {"name": "Wicked Free Wi-Fi (Citywide)", "address": "Various Locations", "notes": "Public Wi-Fi across Dorchester, Roxbury, and East Boston."},
    {"name": "BPL Outdoor Wi-Fi Pop-ups", "address": "Multiple Branches", "notes": "24/7 outdoor Wi-Fi at East Boston, Codman Sq, and more."},
    {"name": "South End Library", "address": "685 Tremont St", "notes": "Free high-speed indoor Wi-Fi."}
]

COMMUNITY_CENTERS = [
    {"name": "BCYF Blackstone", "address": "South End", "notes": "Computer lab, gym, and teen center."},
    {"name": "BCYF Paris Street", "address": "East Boston", "notes": "Fitness center, teen center, and dance studio."},
    {"name": "BCYF Shelburne", "address": "Roxbury", "notes": "Youth and senior programming."}
]

# Note: Many BPL branches and BCYF centers double as Cooling Centers during heat waves.
COOLING_CENTERS = [
    {"name": "Central Library (Copley)", "address": "700 Boylston St", "notes": "Official cooling site with A/C and seating."},
    {"name": "BCYF Gallivan", "address": "Mattapan", "notes": "Cooling resource for residents."},
    {"name": "BCYF Charlestown", "address": "255 Medford St", "notes": "Indoor pool and climate-controlled space."}
]
if st.session_state.page == "Resources":
    st.header("📍 Community Support Hub")
    
    # Category Tabs
    tab1, tab2, tab3 = st.tabs(["📶 Wi-Fi & Library", "🏠 Community Centers", "❄️ Cooling Centers"])
    
    with tab1:
        st.subheader("Free Internet Access")
        for item in WIFI_CENTERS:
            st.markdown(f"""
            <div class="info-card">
                <h4>{item['name']}</h4>
                <p>📍 {item['address']}</p>
                <p>ℹ️ {item['notes']}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.subheader("BCYF Neighborhood Centers")
        for item in COMMUNITY_CENTERS:
            st.markdown(f"""
            <div class="info-card">
                <h4>{item['name']}</h4>
                <p>📍 {item['address']}</p>
                <p>ℹ️ {item['notes']}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.info("During Heat Emergencies, these locations act as official cooling sites.")
        for item in COOLING_CENTERS:
            st.markdown(f"""
            <div class="info-card" style="border-left: 5px solid #3B82F6;">
                <h4>{item['name']}</h4>
                <p>📍 {item['address']}</p>
                <p>❄️ {item['notes']}</p>
            </div>
            """, unsafe_allow_html=True)