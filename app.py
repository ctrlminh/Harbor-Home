import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import math

# ── Configuration ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HarborHome | Boston Housing Engine",
    page_icon="🏠",
    layout="wide"
)

# ── Enhanced Styling ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Sidebar styling */
    div[data-testid="stSidebar"] {
        background-color: #0E1117;
        border-right: 1px solid #2D2D2D;
    }
    
    /* Metric Card Styling */
    .score-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid #E0E4E8;
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .score-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .score-great { border-left: 6px solid #1D9E75; }
    .score-ok    { border-left: 6px solid #F59E0B; }
    .score-low   { border-left: 6px solid #EF4444; }
    
    /* Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0B2C4A 0%, #174E7D 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(11, 44, 74, 0.2);
    }
    
    /* Custom Tags */
    .tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        margin-right: 5px;
    }
    .tag-blue { background: #E1EFFE; color: #1E429F; }
    .tag-green { background: #DEF7EC; color: #03543F; }
</style>
""", unsafe_allow_html=True)

# ── Data (Added Medical) ─────────────────────────────────────────────────────
HOUSING = [
    {"name": "Roxbury Crossing Apts", "lat": 42.3315, "lon": -71.0952, "rent": 950,  "beds": 2, "waitlist": "Open",   "neighborhood": "Roxbury"},
    {"name": "Jamaica Plain Commons",  "lat": 42.3100, "lon": -71.1130, "rent": 875,  "beds": 1, "waitlist": "Open",   "neighborhood": "Jamaica Plain"},
    {"name": "Dorchester Arms",        "lat": 42.3010, "lon": -71.0680, "rent": 800,  "beds": 2, "waitlist": "Closed", "neighborhood": "Dorchester"},
    {"name": "South End Residences",   "lat": 42.3420, "lon": -71.0750, "rent": 1100, "beds": 1, "waitlist": "Open",   "neighborhood": "South End"},
    {"name": "East Boston Commons",    "lat": 42.3760, "lon": -71.0380, "rent": 780,  "beds": 2, "waitlist": "Open",   "neighborhood": "East Boston"},
    {"name": "Hyde Park Affordable",   "lat": 42.2550, "lon": -71.1240, "rent": 720,  "beds": 3, "waitlist": "Open",   "neighborhood": "Hyde Park"},
]

MEDICAL = [
    {"name": "Whittier Street Health Center", "lat": 42.3320, "lon": -71.0920, "type": "Community Clinic"},
    {"name": "Codman Square Health", "lat": 42.2900, "lon": -71.0690, "type": "Community Clinic"},
    {"name": "South End Community Health", "lat": 42.3390, "lon": -71.0790, "type": "Urgent Care"},
    {"name": "East Boston Neighborhood Health", "lat": 42.3720, "lon": -71.0360, "type": "Full Service"},
    {"name": "Bowdoin Street Medical", "lat": 42.3070, "lon": -71.0650, "type": "Clinic"},
]

SNAP_STORES = [{"name": "Stop & Shop", "lat": 42.3290, "lon": -71.0880}, {"name": "Market Basket", "lat": 42.2980, "lon": -71.0710}]
COOLING = [{"name": "Roxbury Library", "lat": 42.3300, "lon": -71.0890, "hours": "9am–8pm"}]
T_STOPS = [{"name": "Roxbury Crossing", "lat": 42.3315, "lon": -71.0952, "line": "Orange"}]

# ── Logic ────────────────────────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlam = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def nearest_dist(lat, lon, places):
    return min([haversine(lat, lon, p["lat"], p["lon"]) for p in places]) if places else 99

def calculate_scores(h, has_car, income_band, heat_sensitive):
    # Proximity metrics
    t_dist = nearest_dist(h["lat"], h["lon"], T_STOPS)
    m_dist = nearest_dist(h["lat"], h["lon"], MEDICAL)
    s_dist = nearest_dist(h["lat"], h["lon"], SNAP_STORES)
    
    # Base sub-scores (0-100)
    transit_score = max(0, 100 - (t_dist * 80))
    medical_score = max(0, 100 - (m_dist * 60))
    food_score = max(0, 100 - (s_dist * 70))
    
    # Weighting adjustments based on user profile
    w_transit, w_med, w_food, w_afford = 0.3, 0.2, 0.2, 0.3
    if heat_sensitive:
        w_med, w_transit = 0.45, 0.15 # Prioritize healthcare for vulnerable populations
    if has_car:
        w_transit, w_food = 0.1, 0.3
        
    total = (transit_score * w_transit) + (medical_score * w_med) + (food_score * w_food) + (80 * w_afford)
    
    return {
        "total": int(total),
        "medical_dist": round(m_dist, 2),
        "transit_dist": round(t_dist, 2),
        "food_dist": round(s_dist, 2)
    }

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/609/609803.png", width=50)
    st.title("HarborHome")
    st.markdown("---")
    
    with st.expander("👤 Personal Profile", expanded=True):
        income = st.selectbox("Monthly Income", ["Under $800", "$800-$1500", "$1500+"])
        heat_sensitive = st.toggle("Heat Sensitive / Elderly", value=False)
        has_car = st.toggle("Access to Vehicle", value=False)
        beds = st.slider("Bedrooms Needed", 1, 4, 2)

    with st.expander("🗺️ Map Layers", expanded=True):
        show_med = st.checkbox("Medical Centers", value=True)
        show_housing = st.checkbox("Housing Projects", value=True)
        show_food = st.checkbox("SNAP Retailers", value=True)
    
    st.info("💡 Pro-tip: Listings are ranked by your specific health and transit needs.")

# ── Main UI ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-banner">
    <h1>HarborHome Boston 🏠</h1>
    <p>Data-driven housing placement for a healthier, more connected life.</p>
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([3, 2])

with col_left:
    # ── Map Implementation ──
    m = folium.Map(location=[42.3300, -71.0850], zoom_start=13, tiles="CartoDB positron")
    
    if show_med:
        for med in MEDICAL:
            folium.Marker(
                [med["lat"], med["lon"]],
                tooltip=med["name"],
                icon=folium.Icon(color="red", icon="plus-med", prefix="fa")
            ).add_to(m)
            
    if show_housing:
        for h in HOUSING:
            score_data = calculate_scores(h, has_car, income, heat_sensitive)
            color = "#1D9E75" if score_data["total"] > 70 else "#F59E0B" if score_data["total"] > 50 else "#EF4444"
            folium.CircleMarker(
                [h["lat"], h["lon"]],
                radius=12, color=color, fill=True, fill_opacity=0.7,
                popup=f"{h['name']} - Match: {score_data['total']}%"
            ).add_to(m)

    st_folium(m, height=550, use_container_width=True)

with col_right:
    st.subheader("Top Matches")
    
    tabs = st.tabs(["Listings", "Nearby Care", "Resources"])
    
    with tabs[0]: # Listings
        scored_listings = []
        for h in HOUSING:
            s = calculate_scores(h, has_car, income, heat_sensitive)
            scored_listings.append({**h, **s})
        
        scored_listings.sort(key=lambda x: x["total"], reverse=True)
        
        for h in scored_listings:
            status_class = "great" if h["total"] > 70 else "ok" if h["total"] > 50 else "low"
            st.markdown(f"""
            <div class="score-card score-{status_class}">
                <div style="display:flex; justify-content:space-between;">
                    <span style="font-weight:600; color:#0B2C4A;">{h['name']}</span>
                    <span style="font-weight:bold; color:#1D9E75;">{h['total']}% Match</span>
                </div>
                <div style="margin: 8px 0;">
                    <span class="tag tag-blue">{h['neighborhood']}</span>
                    <span class="tag tag-green">${h['rent']}/mo</span>
                </div>
                <div style="font-size:0.8rem; color:#666; display:grid; grid-template-columns: 1fr 1fr; gap:5px;">
                    <span>🏥 {h['medical_dist']} mi to Health</span>
                    <span>🚇 {h['transit_dist']} mi to T-Stop</span>
                    <span>🛒 {h['food_dist']} mi to Grocery</span>
                    <span>🛏️ {h['beds']} Bedrooms</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    with tabs[1]: # Nearby Care
        st.write("Community Health Resources")
        for med in MEDICAL:
            st.write(f"**{med['name']}**")
            st.caption(f"Type: {med['type']} | Distance: Calculating...")
            
    with tabs[2]: # Resources
        st.markdown("""
        - [Apply for SNAP](https://www.mass.gov/snap-benefits-formerly-food-stamps)
        - [Boston Housing Authority](https://www.bostonhousing.org/)
        - [Emergency Cooling Centers](https://www.boston.gov/departments/public-health-commission/keeping-cool-heat)
        """)

# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
f_col1, f_col2, f_col3 = st.columns(3)
with f_col1:
    st.metric("Open Waitlists", "12 Active")
with f_col2:
    st.metric("Avg. Match Score", "68%", "+5%")
with f_col3:
    st.button("📧 Email Bundle to Client", use_container_width=True)
    