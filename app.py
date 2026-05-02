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
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 1rem;
    }
    .info-card h4 { color: var(--text-color); margin: 0; font-weight: 700; }
    .info-card p { color: var(--text-color); opacity: 0.8; margin: 3px 0; font-size: 0.9rem; }
    .tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        background: #3B82F6;
        color: white;
        margin-top: 5px;
    }
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

# ── EXPANDED DATASET ───────────────────────────────────────────────────────
HOUSING = [
    {"name": "Roxbury Crossing Apts", "lat": 42.3315, "lon": -71.0952, "rent": 950, "beds": 2, "type": "Subsidized", "area": "Roxbury"},
    {"name": "JP Commons", "lat": 42.3100, "lon": -71.1130, "rent": 1100, "beds": 1, "type": "Affordable", "area": "Jamaica Plain"},
    {"name": "Dorchester Arms", "lat": 42.3010, "lon": -71.0680, "rent": 850, "beds": 2, "type": "Subsidized", "area": "Dorchester"},
    {"name": "Mattapan Village", "lat": 42.2770, "lon": -71.0920, "rent": 1300, "beds": 3, "type": "Market Rate", "area": "Mattapan"},
    {"name": "Eastie Waterfront", "lat": 42.3700, "lon": -71.0390, "rent": 1600, "beds": 1, "type": "Market Rate", "area": "East Boston"},
    {"name": "South End Gateway", "lat": 42.3420, "lon": -71.0740, "rent": 1200, "beds": 2, "type": "Affordable", "area": "South End"},
    {"name": "Lower Mills Lofts", "lat": 42.2720, "lon": -71.0690, "rent": 1450, "beds": 2, "type": "Market Rate", "area": "Dorchester"},
    {"name": "Mission Hill Heights", "lat": 42.3300, "lon": -71.1040, "rent": 1050, "beds": 3, "type": "Subsidized", "area": "Mission Hill"}
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

# ── PAGE: HOUSING (FIXED & EXPANDED) ──────────────────────────────────────────
elif st.session_state.page == "Housing":
    st.subheader("Affordable Housing Navigator")
    
    # ── Sidebar Filters
    with st.sidebar:
        st.header("Search Filters")
        max_rent = st.slider("Maximum Monthly Rent", 500, 2000, 1500, step=50)
        
        min_beds = st.selectbox("Minimum Bedrooms", [1, 2, 3], index=0)
        
        types = ["All", "Subsidized", "Affordable", "Market Rate"]
        selected_type = st.radio("Building Type", types)
        
        areas = ["All"] + sorted(list(set(h['area'] for h in HOUSING)))
        selected_area = st.selectbox("Neighborhood", areas)

    # ── Filter Logic
    filtered_h = [
        h for h in HOUSING 
        if h['rent'] <= max_rent 
        and h['beds'] >= min_beds
        and (selected_type == "All" or h['type'] == selected_type)
        and (selected_area == "All" or h['area'] == selected_area)
    ]

    # ── Map and List Display
    col_map, col_list = st.columns([2, 1])

    with col_map:
        st.write(f"Showing {len(filtered_h)} matching properties")
        m = folium.Map(location=[42.33, -71.08], zoom_start=12)
        for h in filtered_h:
            popup_text = f"{h['name']} - ${h['rent']}"
            folium.Marker(
                [h["lat"], h["lon"]], 
                tooltip=popup_text,
                icon=folium.Icon(color="blue", icon="home")
            ).add_to(m)
        st_folium(m, height=500, use_container_width=True)

    with col_list:
        if not filtered_h:
            st.warning("No listings match your current filters.")
        for h in filtered_h:
            st.markdown(f"""
            <div class="info-card">
                <h4>{h['name']}</h4>
                <p><b>{h['area']}</b></p>
                <p>${h['rent']}/mo | {h['beds']} BR</p>
                <span class="tag">{h['type']}</span>
            </div>
            """, unsafe_allow_html=True)

# ── PAGE: RESOURCES ────────────────────────────────────────────────────────
elif st.session_state.page == "Resources":
    st.header("📍 Community Support")
    t1, t2, t3 = st.tabs(["📶 Wi-Fi & Library", "🏠 Community Centers", "❄️ Cooling Centers"])
    
    with t1:
        for item in WIFI_CENTERS:
            st.markdown(f'<div class="info-card"><h4>{item["name"]}</h4><p>{item["address"]}</p><small>{item["notes"]}</small></div>', unsafe_allow_html=True)
    with t2:
        for item in COMMUNITY_CENTERS:
            st.markdown(f'<div class="info-card"><h4>{item["name"]}</h4><p>{item["address"]}</p><small>{item["notes"]}</small></div>', unsafe_allow_html=True)
    with t3:
        st.info("Official cooling sites active during heat emergencies.")
        for item in COOLING_CENTERS:
            st.markdown(f'<div class="info-card" style="border-left: 5px solid #3B82F6;"><h4>{item["name"]}</h4><p>{item["address"]}</p></div>', unsafe_allow_html=True)

# ── PAGE: NEWS ──────────────────────────────────────────────────────────────
elif st.session_state.page == "News":
    st.subheader("Neighborhood Updates")
    st.info("**Community Health Fair:** May 10th at BCYF Shelburne.")
    st.warning("**Registration:** BPS Summer program sign-ups close next week.")

    