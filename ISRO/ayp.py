import streamlit as st
from PIL import Image
from utils.charts import radiation_chart
from components.cards import status_card
from components.mission_control import show_mission_control

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="JADA Space Tech",
    page_icon="🚀",
    layout="wide"
)

# -----------------------------
# LOAD CSS
# -----------------------------
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -----------------------------
# LOAD IMAGE
# -----------------------------
hero = Image.open("assets/earth.png")

# -----------------------------
# NAVBAR
# -----------------------------

col1, col2, col3 = st.columns([2,6,2])

with col1:
    st.markdown(
        "<h2 style='color:#00E5FF;'>🚀 JADA</h2>",
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div style='text-align:center; padding-top:15px; font-size:18px; color:white;'>
            Mission &nbsp;&nbsp; Dashboard &nbsp;&nbsp; Forecast &nbsp;&nbsp; Satellites &nbsp;&nbsp; About
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.success("🟢 Online")

st.divider()

# -----------------------------
# HERO SECTION
# -----------------------------

left, right = st.columns([1.3, 1])

with left:

    st.markdown("""
    <h1 style='font-size:60px; line-height:1.1;'>
    Forecasting <span style='color:#00E5FF;'>Space Radiation</span><br>
    Before It Happens.
    </h1>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='font-size:20px; color:#CCCCCC;'>
    JADA Space Tech uses Artificial Intelligence and Space Weather
    analytics to forecast energetic particle radiation affecting
    geostationary satellites.
    </p>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.button("🚀 Launch Dashboard")

    with c2:
        st.button("📖 Learn More")

    st.write("")

    a, b, c = st.columns(3)

    with a:
        st.metric("Forecast", "45 min")

    with b:
        st.metric("Accuracy", "97.3%")

    with c:
        st.metric("Satellites", "12")

with right:
    st.image(
        hero,
        use_container_width=True
    )
# -----------------------------
# MISSION STATUS
# -----------------------------

st.markdown("## 🚀 Mission Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    status_card(
        "Radiation",
        "HIGH",
        "+12%",
        "☢"
    )

with col2:
    status_card(
        "Solar Wind",
        "742 km/s",
        "LIVE",
        "☀"
    )

with col3:
    status_card(
        "Accuracy",
        "97.3%",
        "AI Model",
        "🤖"
    )

with col4:
    status_card(
        "Satellites",
        "12",
        "Protected",
        "🛰"
    )

# -----------------------------
# RADIATION FORECAST
# -----------------------------

st.divider()

st.header("📈 Radiation Forecast")

radiation_chart()

show_mission_control()

# -----------------------------
# ABOUT
# -----------------------------

st.header("About JADA")

st.write("""
JADA Space Tech is an intelligent radiation forecasting platform designed
to predict energetic particle events affecting geostationary satellites.

Using AI, satellite telemetry, and space weather data,
the platform provides early warnings to help mission operators
protect valuable space assets.
""")

st.divider()

st.caption("© 2026 JADA Space Tech")