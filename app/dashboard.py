import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Reservoir Control Panel",
    layout="wide"
)

# -----------------------------
# GREEN + BLACK TERMINAL STYLE
# -----------------------------
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-size: 13px !important;
}

.stApp {
    background-color: #000000;
    color: #00ff66;
}

h1, h2, h3 {
    color: #00ff66;
    font-weight: 600;
}

div[data-testid="stMetric"] {
    background-color: #0d0d0d;
    padding: 10px;
    border-radius: 6px;
    border: 1px solid #00ff66;
}

div[data-testid="stProgressBar"] > div > div {
    background-color: #00ff66;
}

.stButton>button {
    background-color: #001a00;
    color: #00ff66;
    border: 1px solid #00ff66;
}
</style>
""", unsafe_allow_html=True)

st.title("🟢 Reservoir Monitoring Console")

# -----------------------------
# SAMPLE DATA
# -----------------------------
dams = {
    "Mettur Dam": 78,
    "Bhavanisagar Dam": 62,
    "Vaigai Dam": 91,
    "Amaravathi Dam": 45
}

# -----------------------------
# SIMULATION FUNCTIONS
# -----------------------------
def simulate_inflow(days):
    return np.random.randint(400, 900, days)

def estimate_days_to_fill(current_storage, avg_inflow):
    # Very simple estimation logic (replace later with real model)
    remaining_capacity = 100 - current_storage
    fill_rate = avg_inflow / 1000  # scaled
    if fill_rate <= 0:
        return "Not Increasing"
    days = remaining_capacity / fill_rate
    return int(days)

def classify(storage):
    if storage >= 95:
        return "CRITICAL"
    elif storage >= 75:
        return "HIGH"
    elif storage >= 40:
        return "MODERATE"
    else:
        return "LOW"

# -----------------------------
# DASHBOARD MODE
# -----------------------------
mode = st.sidebar.radio(
    "Select View",
    ["Public View", "Reservoir Analysis"]
)

# =====================================================
# PUBLIC VIEW
# =====================================================
if mode == "Public View":

    st.subheader("Nearby Reservoir Status")

    for dam, level in dams.items():
        st.markdown(f"### {dam}")
        st.metric("Current Level", f"{level}%")
        st.progress(level / 100)
        st.write(f"Status: {classify(level)}")
        st.write("---")

# =====================================================
# ADMIN / ANALYSIS VIEW
# =====================================================
else:

    dam_name = st.selectbox("Select Reservoir", list(dams.keys()))
    current_storage = dams[dam_name]

    forecast_days = st.slider("Forecast Days", 1, 14, 7)

    inflow = simulate_inflow(forecast_days)
    avg_inflow = np.mean(inflow)

    recommended_release = int(avg_inflow * 0.6)
    days_to_fill = estimate_days_to_fill(current_storage, avg_inflow)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Current Level", f"{current_storage}%")
        st.progress(current_storage / 100)

    with col2:
        st.metric("Avg Inflow (m³/s)", int(avg_inflow))

    with col3:
        st.metric("Recommended Release (m³/s)", recommended_release)

    st.subheader("Estimated Time to Full Capacity")

    if isinstance(days_to_fill, int):
        st.write(f"At current inflow trend, reservoir may fill in approximately **{days_to_fill} days**.")
    else:
        st.write("Reservoir level not increasing significantly.")

    st.subheader("Inflow Forecast")

    dates = [datetime.today() + timedelta(days=i) for i in range(forecast_days)]
    df = pd.DataFrame({
        "Date": dates,
        "Predicted Inflow": inflow
    })

    st.line_chart(df.set_index("Date"))

    st.write(f"Risk Level: {classify(current_storage)}")