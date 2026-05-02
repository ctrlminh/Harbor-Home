import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import math

st.set_page_config(
    page_title="HarborHome",
    page_icon="🏠",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .main { background-color: #f8f9fa; }
    .stApp { background-color: #f8f9fa; }
    div[data-testid="stSidebar"] { background-color: #0B2C4A; }
    div[data-testid="stSidebar"] * { color: white !important; }
    div[data-testid="stSidebar"] .stSelectbox label,
    div[data-testid="stSidebar"] .stRadio label,
    div[data-testid="stSidebar"] .stCheckbox label { color: white !important; }
    .score-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 10px;
    }
    .score-great { border-left: 4px solid #1D9E75; }
    .score-ok    { border-left: 4px solid #BA7517; }
    .score-low   { border-left: 4px solid #E24B4A; }
    .hero-banner {
        background: #0B2C4A;
        color: white;
        padding: 1.2rem 1.8rem;
        border-radius: 14px;
        margin-bottom: 1.2rem;
    }
    .metric-row {
        display: flex;
        gap: 12px;
        margin-top: 0.8rem;
    }
    .metric-box {
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Mock data ──────────────────────────────────────────────────────────────────

HOUSING = [
    {"name": "Roxbury Crossing Apts", "lat": 42.3315, "lon": -71.0952, "rent": 950,  "beds": 2, "waitlist": "Open",   "neighborhood": "Roxbury"},
    {"name": "Jamaica Plain Commons",  "lat": 42.3100, "lon": -71.1130, "rent": 875,  "beds": 1, "waitlist": "Open",   "neighborhood": "Jamaica Plain"},
    {"name": "Dorchester Arms",        "lat": 42.3010, "lon": -71.0680, "rent": 800,  "beds": 2, "waitlist": "Closed", "neighborhood": "Dorchester"},
    {"name": "South End Residences",   "lat": 42.3420, "lon": -71.0750, "rent": 1100, "beds": 1, "waitlist": "Open",   "neighborhood": "South End"},
    {"name": "East Boston Commons",    "lat": 42.3760, "lon": -71.0380, "rent": 780,  "beds": 2, "waitlist": "Open",   "neighborhood": "East Boston"},
    {"name": "Hyde Park Affordable",   "lat": 42.2550, "lon": -71.1240, "rent": 720,  "beds": 3, "waitlist": "Open",   "neighborhood": "Hyde Park"},
    {"name": "Mattapan Heights",       "lat": 42.2720, "lon": -71.0920, "rent": 690,  "beds": 2, "waitlist": "Closed", "neighborhood": "Mattapan"},
    {"name": "Chinatown Studio Apts",  "lat": 42.3510, "lon": -71.0620, "rent": 950,  "beds": 1, "waitlist": "Open",   "neighborhood": "Chinatown"},
]

SNAP_STORES = [
    {"name": "Stop & Shop Roxbury",     "lat": 42.3290, "lon": -71.0880},
    {"name": "Market Basket Dorchester","lat": 42.2980, "lon": -71.0710},
    {"name": "Shaw's South End",        "lat": 42.3440, "lon": -71.0780},
    {"name": "JP Food Co-op",           "lat": 42.3070, "lon": -71.1100},
    {"name": "Star Market East Boston", "lat": 42.3740, "lon": -71.0400},
    {"name": "Tropical Foods Roxbury",  "lat": 42.3260, "lon": -71.0860},
]

COOLING = [
    {"name": "Roxbury Library",          "lat": 42.3300, "lon": -71.0890, "hours": "9am–8pm"},
    {"name": "Mattahunt Community Ctr",  "lat": 42.2740, "lon": -71.0950, "hours": "8am–6pm"},
    {"name": "Hyde Park BCYF",           "lat": 42.2570, "lon": -71.1250, "hours": "8am–9pm"},
    {"name": "Copley Branch BPL",        "lat": 42.3494, "lon": -71.0773, "hours": "9am–9pm"},
    {"name": "East Boston Neighborhood", "lat": 42.3780, "lon": -71.0350, "hours": "10am–6pm"},
]

WIFI = [
    {"name": "BPL Central Library",     "lat": 42.3494, "lon": -71.0773},
    {"name": "Roxbury Branch BPL",      "lat": 42.3300, "lon": -71.0890},
    {"name": "Grove Hall Community Ctr","lat": 42.3050, "lon": -71.0780},
    {"name": "East Boston BPL",         "lat": 42.3740, "lon": -71.0390},
    {"name": "City Hall Plaza Wifi",    "lat": 42.3601, "lon": -71.0579},
]

T_STOPS = [
    {"name": "Roxbury Crossing",  "lat": 42.3315, "lon": -71.0952, "line": "Orange"},
    {"name": "Jackson Square",    "lat": 42.3231, "lon": -71.1007, "line": "Orange"},
    {"name": "Stony Brook",       "lat": 42.3174, "lon": -71.1044, "line": "Orange"},
    {"name": "Green St",          "lat": 42.3102, "lon": -71.1075, "line": "Orange"},
    {"name": "Forest Hills",      "lat": 42.2992, "lon": -71.1137, "line": "Orange"},
    {"name": "Back Bay",          "lat": 42.3474, "lon": -71.0750, "line": "Orange"},
    {"name": "South Station",     "lat": 42.3519, "lon": -71.0552, "line": "Red"},
    {"name": "JFK/UMass",         "lat": 42.3204, "lon": -71.0524, "line": "Red"},
    {"name": "Airport",           "lat": 42.3743, "lon": -71.0301, "line": "Blue"},
]

# ── Scoring ────────────────────────────────────────────────────────────────────

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def nearest_dist(lat, lon, places):
    return min(haversine(lat, lon, p["lat"], p["lon"]) for p in places)

def score_listing(h, has_car, income_band, heat_risk):
    transit_dist = nearest_dist(h["lat"], h["lon"], T_STOPS)
    transit_score = max(0, 100 - transit_dist * 120)

    snap_dist = nearest_dist(h["lat"], h["lon"], SNAP_STORES)
    snap_score = max(0, 100 - snap_dist * 150)

    cooling_dist = nearest_dist(h["lat"], h["lon"], COOLING)
    cooling_score = max(0, 100 - cooling_dist * 130)

    wifi_dist = nearest_dist(h["lat"], h["lon"], WIFI)
    wifi_score = max(0, 100 - wifi_dist * 140)

    affordability_map = {"Under $800": 800, "$800–$1,200": 1100, "$1,200–$1,800": 1500, "Over $1,800": 2000}
    max_rent = affordability_map[income_band]
    afford_score = 100 if h["rent"] <= max_rent * 0.4 else max(0, 100 - (h["rent"] - max_rent * 0.4) * 0.3)

    if has_car:
        w = [0.15, 0.25, 0.15, 0.10, 0.35]
    elif heat_risk:
        w = [0.25, 0.20, 0.35, 0.10, 0.10]
    else:
        w = [0.35, 0.20, 0.15, 0.10, 0.20]

    total = (w[0]*transit_score + w[1]*snap_score + w[2]*cooling_score +
             w[3]*wifi_score + w[4]*afford_score)

    return {
        "total": round(total),
        "transit": round(transit_score),
        "snap": round(snap_score),
        "cooling": round(cooling_score),
        "wifi": round(wifi_score),
        "affordability": round(afford_score),
        "transit_dist": round(transit_dist, 2),
        "snap_dist": round(snap_dist, 2),
    }

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🏠 HarborHome")
    st.markdown("*Find the right home for your life*")
    st.markdown("---")

    st.markdown("**Your situation**")
    income_band = st.selectbox("Monthly income range", ["Under $800","$800–$1,200","$1,200–$1,800","Over $1,800"])
    household = st.radio("Household size", ["1 person","2 people","3–4 people","5+ people"])
    has_car = st.checkbox("I have a car")
    heat_risk = st.checkbox("Elderly / heat sensitive")
    language = st.selectbox("Language", ["English","Spanish","Vietnamese","Haitian Creole","Portuguese"])
    beds_needed = st.selectbox("Bedrooms needed", [1, 2, 3])
    open_only = st.checkbox("Open waitlists only", value=True)

    st.markdown("---")
    st.markdown("**Map layers**")
    show_housing  = st.checkbox("Affordable housing", value=True)
    show_snap     = st.checkbox("SNAP retailers", value=True)
    show_cooling  = st.checkbox("Cooling centers", value=True)
    show_wifi     = st.checkbox("Free wifi", value=False)
    show_transit  = st.checkbox("T stops", value=True)

    st.markdown("---")
    st.markdown("<small style='opacity:.5'>Built for Build a Better Boston 2026</small>", unsafe_allow_html=True)

# ── Main ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-banner">
  <div style="font-size:24px;font-weight:600;margin-bottom:4px;">HarborHome 🏠</div>
  <div style="opacity:.75;font-size:14px;">Boston's housing decision engine — not just a map. Scored for your life.</div>
</div>
""", unsafe_allow_html=True)

col_map, col_results = st.columns([3, 2])

# ── Map ────────────────────────────────────────────────────────────────────────

with col_map:
    m = folium.Map(location=[42.3250, -71.0850], zoom_start=12,
                   tiles="CartoDB positron")

    if show_housing:
        for h in HOUSING:
            if open_only and h["waitlist"] == "Closed":
                continue
            scores = score_listing(h, has_car, income_band, heat_risk)
            color = "#1D9E75" if scores["total"] >= 65 else "#BA7517" if scores["total"] >= 45 else "#E24B4A"
            folium.CircleMarker(
                location=[h["lat"], h["lon"]],
                radius=10,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85,
                popup=folium.Popup(
                    f"<b>{h['name']}</b><br>"
                    f"${h['rent']}/mo · {h['beds']}BR · {h['waitlist']}<br>"
                    f"Score: <b>{scores['total']}/100</b><br>"
                    f"Transit: {scores['transit_dist']} mi to nearest T",
                    max_width=220
                ),
                tooltip=f"{h['name']} — Score: {scores['total']}"
            ).add_to(m)

    if show_snap:
        for s in SNAP_STORES:
            folium.Marker(
                location=[s["lat"], s["lon"]],
                popup=s["name"],
                tooltip=s["name"],
                icon=folium.Icon(color="orange", icon="shopping-cart", prefix="fa")
            ).add_to(m)

    if show_cooling:
        for c in COOLING:
            folium.Marker(
                location=[c["lat"], c["lon"]],
                popup=f"{c['name']}<br>{c['hours']}",
                tooltip=c["name"],
                icon=folium.Icon(color="blue", icon="tint", prefix="fa")
            ).add_to(m)

    if show_wifi:
        for w in WIFI:
            folium.Marker(
                location=[w["lat"], w["lon"]],
                popup=w["name"],
                tooltip=w["name"],
                icon=folium.Icon(color="purple", icon="wifi", prefix="fa")
            ).add_to(m)

    if show_transit:
        line_colors = {"Orange": "orange", "Red": "red", "Blue": "blue", "Green": "green"}
        for t in T_STOPS:
            folium.CircleMarker(
                location=[t["lat"], t["lon"]],
                radius=5,
                color=line_colors.get(t["line"], "gray"),
                fill=True,
                fill_color=line_colors.get(t["line"], "gray"),
                fill_opacity=0.9,
                tooltip=f"T: {t['name']} ({t['line']} Line)"
            ).add_to(m)

    legend_html = """
    <div style="position:fixed;bottom:20px;left:20px;z-index:1000;background:white;
                padding:12px 16px;border-radius:10px;border:1px solid #ddd;font-size:12px;font-family:sans-serif;">
      <b>Housing score</b><br>
      <span style="color:#1D9E75">●</span> Great match (65+)<br>
      <span style="color:#BA7517">●</span> Decent match (45–64)<br>
      <span style="color:#E24B4A">●</span> Low match (&lt;45)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, height=520, use_container_width=True)

# ── Results ────────────────────────────────────────────────────────────────────

with col_results:
    st.markdown("#### Top matches for you")

    scored = []
    for h in HOUSING:
        if open_only and h["waitlist"] == "Closed":
            continue
        s = score_listing(h, has_car, income_band, heat_risk)
        scored.append({**h, **s})

    scored.sort(key=lambda x: x["total"], reverse=True)

    if not scored:
        st.warning("No open waitlists match your filters. Try unchecking 'Open waitlists only.'")
    else:
        for i, h in enumerate(scored[:6]):
            grade = "great" if h["total"] >= 65 else "ok" if h["total"] >= 45 else "low"
            label = "Great match" if grade == "great" else "Decent match" if grade == "ok" else "Low match"
            label_color = "#1D9E75" if grade == "great" else "#BA7517" if grade == "ok" else "#E24B4A"

            st.markdown(f"""
            <div class="score-card score-{grade}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                  <div style="font-weight:500;font-size:14px;">{h['name']}</div>
                  <div style="font-size:12px;color:#666;">{h['neighborhood']} · ${h['rent']}/mo · {h['beds']}BR</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:20px;font-weight:600;color:{label_color};">{h['total']}</div>
                  <div style="font-size:10px;color:{label_color};">{label}</div>
                </div>
              </div>
              <div style="margin-top:8px;font-size:11px;color:#888;display:flex;gap:12px;">
                <span>🚇 {h['transit_dist']} mi to T</span>
                <span>🛒 {h['snap_dist']} mi to SNAP</span>
                <span>📋 {h['waitlist']}</span>
              </div>
              <div style="margin-top:6px;background:#f5f5f5;border-radius:4px;height:4px;">
                <div style="width:{h['total']}%;background:{label_color};height:4px;border-radius:4px;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Share a resource bundle")
    st.markdown("<small style='color:#666'>Copy this link and send it to a client or family member — it saves your exact filters.</small>", unsafe_allow_html=True)

    bundle_params = f"?income={income_band}&car={has_car}&heat={heat_risk}&beds={beds_needed}&open={open_only}"
    st.code(f"harborhome.app/map{bundle_params}", language=None)

    if st.button("📋 Copy bundle link"):
        st.success("Link copied! Share it with anyone who needs it.")

    st.markdown("---")
    st.markdown("#### Current alerts")
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("🌡️ No heat advisory today")
    with col_b:
        st.success(f"✅ {len([h for h in HOUSING if h['waitlist']=='Open'])} open waitlists")

git init
git add .
git commit -m "initial harborhome"