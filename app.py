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
    .info-card {
        background-color: rgba(128, 128, 128, 0.1);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 1rem;
    }
    .info-card h4 { color: var(--text-color); margin: 0; font-weight: 700; }
    .info-card p { color: var(--text-color); opacity: 0.8; margin: 5px 0; }

    .action-box {
        background-color: rgba(59, 130, 246, 0.1);
        padding: 2rem;
        border-radius: 16px;
        border: 2px solid rgba(59, 130, 246, 0.3);
        text-align: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ── FULL DATASET ──────────────────────────────────────────────────────────
HOUSING = [
    {"name": "Roxbury Crossing", "lat": 42.3315, "lon": -71.0952, "rent": 950, "beds": 2, "type": "Subsidized"},
    {"name": "JP Commons", "lat": 42.3100, "lon": -71.1130, "rent": 1100, "beds": 1, "type": "Affordable"},
    {"name": "Dorchester Arms", "lat": 42.3010, "lon": -71.0680, "rent": 850, "beds": 2, "type": "Subsidized"},
    {"name": "Mattapan Village", "lat": 42.2770, "lon": -71.0920, "rent": 1300, "beds": 3, "type": "Market Rate (Low)"}
]

MEDICAL = [
    {"name": "Boston Medical Center", "lat": 42.3350, "lon": -71.0740, "type": "Hospital / ER"},
    {"name": "Whittier Street Health", "lat": 42.3320, "lon": -71.0920, "type": "Clinic / Dental"}
]

SNAP = [
    {"name": "Stop & Shop (Dorchester)", "lat": 42.3210, "lon": -71.0650},
    {"name": "Daily Table (Roxbury)", "lat": 42.3295, "lon": -71.0845}
]

WIFI_CENTERS = [
    {"name": "Wicked Free Wi-Fi", "address": "Citywide Hotspots", "notes": "Public Wi-Fi in Roxbury/Dorchester."},
    {"name": "South End Library", "address": "685 Tremont St", "notes": "Free high-speed indoor Wi-Fi."}
]

COMMUNITY_CENTERS = [
    {"name": "BCYF Blackstone", "address": "South End", "notes": "Computer labs and youth programs."},
    {"name": "BCYF Shelburne", "address": "Roxbury", "notes": "Community gym and teen center."}
]

COOLING_CENTERS = [
    {"name": "Central Library (Copley)", "address": "700 Boylston St", "notes": "Official cooling site with A/C."},
    {"name": "BCYF Gallivan", "address": "Mattapan", "notes": "Climate-controlled community space."}
]

# ── Navigation UI ──────────────────────────────────────────────────────────
st.title("HarborHome Boston 🏘️")
st.caption("Secure Housing. Stable Students. Stronger Schools.")

c1, c2, c3, c4 = st.columns(4)
with c1: st.button("🏠 Home", use_container_width=True, on_click=ch_page, args=("Home",))
with c2: st.button("🔍 Housing", use_container_width=True, on_click=ch_page, args=("Housing",))
with c3: st.button("📍 Resources", use_container_width=True, on_click=ch_page, args=("Resources",))
with c4: st.button("📰 News", use_container_width=True, on_click=ch_page, args=("News",))

st.divider()

# ── PAGE: HOME ──────────────────────────────────────────────────────────────
if st.session_state.page == "Home":
    st.subheader("Welcome to Your Neighborhood Hub")
    st.write("Supporting Boston Public Schools families with essential local resources.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="action-box"><h2>🏠</h2><h3>Housing</h3></div>', unsafe_allow_html=True)
        st.button("Search Listings", key="h_btn", use_container_width=True, on_click=ch_page, args=("Housing",))
    with col2:
        st.markdown('<div class="action-box"><h2>📍</h2><h3>Resources</h3></div>', unsafe_allow_html=True)
        st.button("Find Support", key="r_btn", use_container_width=True, on_click=ch_page, args=("Resources",))
    with col3:
        st.markdown('<div class="action-box"><h2>📰</h2><h3>News</h3></div>', unsafe_allow_html=True)
        st.button("Local Updates", key="n_btn", use_container_width=True, on_click=ch_page, args=("News",))

# ── PAGE: HOUSING ───────────────────────────────────────────────────────────
elif st.session_state.page == "Housing":
    st.subheader("Affordability-First Housing")
    
    with st.expander("Filter Options"):
        max_r = st.slider("Max Rent", 500, 2000, 1500)
    
    filtered = [h for h in HOUSING if h['rent'] <= max_r]
    
    m1 = folium.Map(location=[42.33, -71.08], zoom_start=12)
    for h in filtered:
        folium.Marker([h["lat"], h["lon"]], tooltip=h['name']).add_to(m1)
    
    st_folium(m1, height=400, use_container_width=True)
    
    for h in filtered:
        st.markdown(f'<div class="info-card"><h4>{h["name"]}</h4><p>${h["rent"]}/mo • {h["beds"]} Bed • {h["type"]}</p></div>', unsafe_allow_html=True)

# ── PAGE: RESOURCES ────────────────────────────────────────────────────────
elif st.session_state.page == "Resources":
    st.header("📍 Community Support")
    t1, t2, t3, t4 = st.tabs(["📶 Wi-Fi/Library", "🏠 Community", "❄️ Cooling", "🩺 Health/Food"])
    
    with t1:
        for item in WIFI_CENTERS:
            st.markdown(f'<div class="info-card"><h4>{item["name"]}</h4><p>{item["address"]}</p><small>{item["notes"]}</small></div>', unsafe_allow_html=True)
    with t2:
        for item in COMMUNITY_CENTERS:
            st.markdown(f'<div class="info-card"><h4>{item["name"]}</h4><p>{item["address"]}</p><small>{item["notes"]}</small></div>', unsafe_allow_html=True)
    with t3:
        for item in COOLING_CENTERS:
            st.markdown(f'<div class="info-card" style="border-left: 5px solid #3B82F6;"><h4>{item["name"]}</h4><p>{item["address"]}</p></div>', unsafe_allow_html=True)
    with t4:
        st.subheader("Medical & SNAP")
        m2 = folium.Map(location=[42.33, -71.08], zoom_start=12)
        for med in MEDICAL: folium.Marker([med["lat"], med["lon"]], icon=folium.Icon(color="red")).add_to(m2)
        for s in SNAP: folium.Marker([s["lat"], s["lon"]], icon=folium.Icon(color="orange")).add_to(m2)
        st_folium(m2, height=300, use_container_width=True)

# ── PAGE: NEWS ──────────────────────────────────────────────────────────────
elif st.session_state.page == "News":
    st.subheader("Neighborhood Updates")
    st.info("**Community Health Fair:** May 10th at BCYF Shelburne.")
    st.warning("**Registration:** BPS Summer program sign-ups close next week.")
    