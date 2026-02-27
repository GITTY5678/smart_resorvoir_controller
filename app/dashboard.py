# -------------------------------------------------
# IMPORTS
# -------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from statsmodels.tsa.arima.model import ARIMA

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="AQUA NEXUS - Automated Flood Prediction System",
    layout="wide"
)

# -------------------------------------------------
# THEME
# -------------------------------------------------

st.markdown("""
<style>
body, .stApp { background-color: #000000; color: #ff0000; }
.stSidebar { background-color: #0a0000 !important; }
.stButton>button {
    background-color: #220000 !important;
    color: #ff0000 !important;
    border: 1px solid #ff0000 !important;
}
.stMetric>div {
    background-color: #110000 !important;
    border: 1px solid #ff0000 !important;
}
h1, h2, h3 { color: #ff0000 !important; }
</style>
""", unsafe_allow_html=True)

st.title("AQUA NEXUS")
st.subheader("Reservoir Monitoring + Automated Rainfall-Based Forecasting")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

RES_PATH = os.path.join("data", "cwc_reservoirs.xlsx")
RAIN_PATH = os.path.join("data", "climate.xlsx")

if not os.path.exists(RES_PATH):
    st.error("Reservoir dataset not found.")
    st.stop()

if not os.path.exists(RAIN_PATH):
    st.error("Climate dataset not found.")
    st.stop()

res_df_full = pd.read_excel(RES_PATH)
rain_df_full = pd.read_excel(RAIN_PATH)

res_df_full["DATE"] = pd.to_datetime(res_df_full["DATE"])

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.header("Reservoir Filters")

regions = res_df_full["REGION"].unique()
selected_region = st.sidebar.selectbox("Select Region", regions)

region_df = res_df_full[res_df_full["REGION"] == selected_region]

states = region_df["STATE"].unique()
selected_state = st.sidebar.selectbox("Select State", states)

state_df = region_df[region_df["STATE"] == selected_state]

reservoirs = state_df["RESERVOIR"].unique()
selected_reservoir = st.sidebar.selectbox("Select Reservoir", reservoirs)

unit = st.sidebar.radio("Display Units", ["Percent", "BCM"])

# -------------------------------------------------
# FILTER DATA
# -------------------------------------------------

res_df = state_df[state_df["RESERVOIR"] == selected_reservoir].copy()
res_df = res_df.sort_values("DATE")

# -------------------------------------------------
# CURRENT STATUS
# -------------------------------------------------

st.header(f"Current Status — {selected_reservoir}")

latest = res_df.iloc[-1]
current_storage = latest["CURRENT STORAGE BCM"]
capacity = latest["FULL RESERVOIR LEVEL BCM"]
storage_pct = (current_storage / capacity) * 100

if unit == "BCM":
    display_storage = current_storage
    display_capacity = capacity
    label_storage = "Current Storage (BCM)"
    label_capacity = "Capacity (BCM)"
else:
    display_storage = storage_pct
    display_capacity = 100
    label_storage = "Current Storage (%)"
    label_capacity = "Capacity (%)"

c1, c2, c3 = st.columns(3)
c1.metric(label_storage, f"{display_storage:.2f}")
c2.metric(label_capacity, f"{display_capacity:.2f}")
c3.metric("Storage %", f"{storage_pct:.2f}%")

# -------------------------------------------------
# WEEKLY TREND
# -------------------------------------------------

st.markdown("---")
st.subheader("Weekly Storage Trend")

weekly_values = (
    res_df["CURRENT STORAGE BCM"]
    if unit == "BCM"
    else res_df["CURRENT STORAGE BCM"] / capacity * 100
)

fig_weekly = go.Figure()
fig_weekly.add_trace(go.Scatter(
    x=res_df["DATE"],
    y=weekly_values,
    mode="lines"
))

fig_weekly.update_layout(template="plotly_dark", height=400)
st.plotly_chart(fig_weekly, use_container_width=True)

# -------------------------------------------------
# MONTHLY AGGREGATION
# -------------------------------------------------

res_df["Year"] = res_df["DATE"].dt.year
res_df["Month"] = res_df["DATE"].dt.month

monthly_storage = res_df.groupby(
    ["Year", "Month", "REGION"]
)["CURRENT STORAGE BCM"].mean().reset_index()

rain_df_full = rain_df_full[[
    "Year",
    "Month No",
    "CWC Region",
    "Rainfall Actual (mm)"
]].copy()

rain_df_full = rain_df_full.rename(columns={
    "CWC Region": "REGION",
    "Month No": "Month",
    "Rainfall Actual (mm)": "Rainfall_mm"
})

monthly_rain = rain_df_full.groupby(
    ["Year", "Month", "REGION"]
)["Rainfall_mm"].mean().reset_index()

merged_df = pd.merge(
    monthly_storage,
    monthly_rain,
    on=["Year", "Month", "REGION"],
    how="inner"
)

if len(merged_df) < 12:
    st.warning("Not enough data for forecasting.")
    st.stop()

if unit == "Percent":
    merged_df["CURRENT STORAGE BCM"] = (
        merged_df["CURRENT STORAGE BCM"] / capacity * 100
    )

storage_series = merged_df["CURRENT STORAGE BCM"]
rain_series = merged_df["Rainfall_mm"]

# -------------------------------------------------
# FORECASTING
# -------------------------------------------------

st.markdown("---")
st.subheader("Automated Rainfall + Storage Forecast")

try:
    rain_model = ARIMA(rain_series, order=(2, 1, 2))
    rain_fit = rain_model.fit()

    forecast_steps = 3
    rain_forecast = rain_fit.forecast(steps=forecast_steps)

    st.markdown("### Predicted Rainfall (Next 3 Months)")
    st.line_chart(rain_forecast)

    storage_model = ARIMA(storage_series, exog=rain_series, order=(2, 1, 2))
    storage_fit = storage_model.fit()

    future_exog = rain_forecast.values.reshape(-1, 1)

    storage_forecast_result = storage_fit.get_forecast(
        steps=forecast_steps,
        exog=future_exog
    )

    storage_forecast = storage_forecast_result.predicted_mean

    last_year = int(merged_df.iloc[-1]["Year"])
    last_month = int(merged_df.iloc[-1]["Month"])

    future_dates = pd.date_range(
        start=f"{last_year}-{last_month}-01",
        periods=forecast_steps + 1,
        freq="M"
    )[1:]

    fig_forecast = go.Figure()

    historical_dates = pd.to_datetime(
        merged_df["Year"].astype(str) + "-" +
        merged_df["Month"].astype(str) + "-01"
    )

    fig_forecast.add_trace(go.Scatter(
        x=historical_dates,
        y=storage_series,
        mode="lines",
        name="Historical"
    ))

    fig_forecast.add_trace(go.Scatter(
        x=future_dates,
        y=storage_forecast,
        mode="lines",
        name="Forecast",
        line=dict(color="red")
    ))

    fig_forecast.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig_forecast, use_container_width=True)

    # Risk Assessment
    final_forecast = storage_forecast.iloc[-1]

    if unit == "Percent":
        forecast_pct = final_forecast
    else:
        forecast_pct = (final_forecast / capacity) * 100

    st.markdown("---")
    st.subheader("Forecast Risk Assessment")

    if forecast_pct > 95:
        st.error("Reservoir Likely to Overflow")
    elif forecast_pct > 85:
        st.warning("High Flood Risk Approaching")
    elif forecast_pct < 25:
        st.warning("Drought Risk")
    else:
        st.success("Storage Within Safe Limits")

    st.metric("Projected Storage % (3 Months)", f"{forecast_pct:.2f}%")

except Exception as e:
    st.error(f"Forecasting failed: {e}")