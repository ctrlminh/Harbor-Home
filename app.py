import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import math

# ── Configuration ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HarborHome | Youth & Family Engine",
    page_icon="🏘️",
    layout="wide"
)

# ── Enhanced Styling (Softer, Welcoming Design) ──────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Make sidebar lighter and more welcoming */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Metric Card Styling */
    .score-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid #E0E4E8;
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .score-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    .score-great { border-left: 6px solid #10B981; } /* Friendly Green */
    .score-ok    { border-left: 6px solid #F59E0B; }
    .score-low   { border-left: 6px solid #EF4444; }
    
    /* Hero Banner - Warm and Welcoming */
    .hero-banner {
        background: linear-gradient(135deg, #3B82F6 0%, #2DD4BF 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(45, 212, 191, 0.2);
    }
    
    .hero-banner h1 { color: white; font-weight: 700; margin-bottom: 0.5rem; }
    
    /* Custom Tags */
    .tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        margin-right: 5px;
    }
    .tag-blue { background: #DBEAFE; color: #1E40AF; }
    .tag-green { background: #D1FAE5; color: #065F46; }
    
    /* News Card */
    .news-card {
        background: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Data & Content ───────────────────────────────────────────────────────────
HOUSING = [
    {"name": "Roxbury Crossing Apts", "lat": 42.3315, "lon": -71.0952, "rent": 950,  "beds": 2, "waitlist": "Open",   "neighborhood": "Roxbury"},
    {"name": "Jamaica Plain Commons",  "lat": 42.3100, "lon": -71.1130, "rent": 875,  "beds": 1, "waitlist": "Open",   "neighborhood": "Jamaica Plain"},
    {"name": "Dorchester Arms",        "lat": 42.3010, "lon": -71.0680, "rent": 800,  "beds": 2, "waitlist": "Closed", "neighborhood": "Dorchester"},
]

MEDICAL = [
    {"name": "Whittier Street Health Center", "lat": 42.3320, "lon": -71.0920, "type": "Community Clinic"},
    {"name": "Codman Square Health", "lat": 42.2900, "lon": -71.0690, "type": "Community Clinic"},
]

SNAP_STORES = [{"name": "Stop & Shop", "lat": 42.3290, "lon": -71.0880}, {"name": "Market Basket", "lat": 42.2980, "lon": -71.0710}]
WIFI_SPOTS = [{"name": "Roxbury Free Public Library", "lat": 42.3300, "lon": -71.0890}, {"name": "Community Center Hub", "lat": 42.3150, "lon": -71.0950}]
WATER_STATIONS = [{"name": "Boston Common Splash Pad", "lat": 42.3550, "lon": -71.0650}, {"name": "Franklin Park Fountain", "lat": 42.3000, "lon": -71.0900}]

NEWS = [
    {"title": "📢 City Council Meeting: Expanding Youth Housing Subsidies", "date": "May 5, 2026", "location": "City Hall / Virtual"},
    {"title": "🎒 BPS Social Worker Training: Navigating HarborHome", "date": "May 10, 2026", "location": "Boston Public Library"},
    {"title": "🍎 Summer SNAP Benefits Registration Drive", "date": "May 12, 2026", "location": "All Community Centers"},
]

# Simple Language Dictionary
LANG = {
    "English": {
        "title": "HarborHome Education Hub 🏘️",
        "subtitle": "Empowering school counselors and social workers to secure stable housing and resources for students.",
        "nav_house": "🏠 Housing Match",
        "nav_res": "📍 Local Resources",
        "nav_news": "📰 Community News",
        "pro_tip": "💡 Pro-tip: Activate 'Student Profile' to prioritize family-friendly neighborhoods."
    },
    "Español": {
        "title": "Centro Educativo HarborHome 🏘️",
        "subtitle": "Capacitando a trabajadores sociales para asegurar vivienda y recursos para estudiantes.",
        "nav_house": "🏠 Búsqueda de Vivienda",
        "nav_res": "📍 Recursos Locales",
        "nav_news": "📰 Noticias de la Comunidad",
        "pro_tip": "💡 Consejo: Active el 'Perfil de Estudiante' para priorizar vecindarios familiares."
    }
}

# ── Logic ────────────────────────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlam = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def nearest_dist(lat, lon, places):
    return min([haversine(lat, lon, p["lat"], p["lon"]) for p in places]) if places else 99

def calculate_scores(h, has_car, income_band, youth_focus):
    m_dist = nearest_dist(h["lat"], h["lon"], MEDICAL)
    s_dist = nearest_dist(h["lat"], h["lon"], SNAP_STORES)
    
    medical_score = max(0, 100 - (m_dist * 60))
    food_score = max(0, 100 - (s_dist * 70))
    
    w_med, w_food, w_afford = 0.3, 0.3, 0.4
    if youth_focus:
        w_food = 0.5 # Prioritize food access for youth
        
    total = (medical_score * w_med) + (food_score * w_food) + (80 * w_afford)
    
    return {"total": int(total), "medical_dist": round(m_dist, 2), "food_dist": round(s_dist, 2)}

# ── Sidebar Navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3281/3281323.png", width=60)
    
    language = st.selectbox("🌐 Language / Idioma", ["English", "Español"])
    text = LANG[language]
    
    st.title("Navigation")
    page = st.radio("Go to:", [text["nav_house"], text["nav_res"], text["nav_news"]], label_visibility="collapsed")
    
    st.markdown("---")
    st.info(text["pro_tip"])

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-banner">
    <h1>{text['title']}</h1>
    <p style="font-size: 1.1rem; opacity: 0.9;">{text['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

# ── Page 1: Housing Match ────────────────────────────────────────────────────
if page == text["nav_house"]:
    col_left, col_right = st.columns([3, 2])
    
    with col_right:
        st.subheader("Client Profile (Counselor Entry)")
        income = st.selectbox("Family Monthly Income", ["Under $800", "$800-$1500", "$1500+"])
        youth_focus = st.toggle("BPS Student Household (Prioritizes Food/Transit)", value=True)
        beds = st.slider("Bedrooms Needed", 1, 4, 2)
        
        st.markdown("---")
        st.subheader("Top Matches")
        
        scored_listings = []
        for h in HOUSING:
            s = calculate_scores(h, False, income, youth_focus)
            scored_listings.append({**h, **s})
        
        scored_listings.sort(key=lambda x: x["total"], reverse=True)
        
        for h in scored_listings:
            status_class = "great" if h["total"] > 70 else "ok"
            st.markdown(f"""
            <div class="score-card score-{status_class}">
                <div style="display:flex; justify-content:space-between;">
                    <span style="font-weight:700; color:#1E293B;">{h['name']}</span>
                    <span style="font-weight:bold; color:#10B981;">{h['total']}% Match</span>
                </div>
                <div style="margin: 8px 0;">
                    <span class="tag tag-blue">{h['neighborhood']}</span>
                    <span class="tag tag-green">${h['rent']}/mo</span>
                </div>
                <div style="font-size:0.85rem; color:#64748B;">
                    🏥 {h['medical_dist']} mi | 🛒 {h['food_dist']} mi to SNAP
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_left:
        st.subheader("Neighborhood Map")
        m = folium.Map(location=[42.3150, -71.0850], zoom_start=12, tiles="CartoDB positron")
        for h in HOUSING:
            folium.Marker([h["lat"], h["lon"]], popup=h['name'], icon=folium.Icon(color="green", icon="home")).add_to(m)
        st_folium(m, height=500, use_container_width=True)

# ── Page 2: Local Resources ──────────────────────────────────────────────────
elif page == text["nav_res"]:
    st.subheader("📍 Interactive Resource Finder")
    st.write("Enter a student's address or neighborhood to find immediate basic needs nearby.")
    
    search_col, filter_col = st.columns([3, 1])
    with search_col:
        address = st.text_input("Search Address or Neighborhood (e.g., 'Roxbury, Boston')", placeholder="Type here...")
    with filter_col:
        resource_type = st.selectbox("Show Resource", ["All", "🛒 SNAP Stores", "📶 Free WiFi", "💧 Water Stations"])
    
    # Mock geocoding behavior for the hackathon map
    map_center = [42.3300, -71.0850] # Default Roxbury
    if "dorchester" in address.lower(): map_center = [42.3010, -71.0680]
    
    m2 = folium.Map(location=map_center, zoom_start=14, tiles="CartoDB positron")
    
    if resource_type in ["All", "🛒 SNAP Stores"]:
        for s in SNAP_STORES: folium.Marker([s["lat"], s["lon"]], popup=s["name"], icon=folium.Icon(color="orange", icon="shopping-cart")).add_to(m2)
    if resource_type in ["All", "📶 Free WiFi"]:
        for w in WIFI_SPOTS: folium.Marker([w["lat"], w["lon"]], popup=w["name"], icon=folium.Icon(color="blue", icon="wifi")).add_to(m2)
    if resource_type in ["All", "💧 Water Stations"]:
        for w in WATER_STATIONS: folium.Marker([w["lat"], w["lon"]], popup=w["name"], icon=folium.Icon(color="lightblue", icon="tint")).add_to(m2)

    st_folium(m2, height=450, use_container_width=True)

# ── Page 3: Community News ───────────────────────────────────────────────────
elif page == text["nav_news"]:
    st.subheader("📰 Community & Council News")
    st.write("Stay updated on city council meetings, housing policies, and school worker training events.")
    
    for item in NEWS:
        st.markdown(f"""
        <div class="news-card">
            <h4 style="margin:0; color:#1E293B;">{item['title']}</h4>
            <p style="margin:5px 0 0 0; color:#64748B; font-size:0.9rem;">
                📅 <strong>{item['date']}</strong> | 📍 {item['location']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        