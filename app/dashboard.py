# -------------------------------------------------
# IMPORTS
# -------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="Smart Reservoir Controller- ML Flood Prediction System",
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
st.subheader("Reservoir Monitoring + Gradient Boosting Forecast")

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
# SIDEBAR FILTERS
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

# -------------------------------------------------
# FILTERED DATA
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

c1, c2, c3 = st.columns(3)
c1.metric("Current Storage (BCM)", f"{current_storage:.2f}")
c2.metric("Capacity (BCM)", f"{capacity:.2f}")
c3.metric("Storage %", f"{storage_pct:.2f}%")

# -------------------------------------------------
# WEEKLY TREND
# -------------------------------------------------

st.markdown("---")
st.subheader("Weekly Storage Trend")

fig_weekly = go.Figure()
fig_weekly.add_trace(go.Scatter(
    x=res_df["DATE"],
    y=res_df["CURRENT STORAGE BCM"],
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

# Clean rainfall data
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

# -------------------------------------------------
# MACHINE LEARNING FORECAST
# -------------------------------------------------

st.markdown("---")
st.subheader("Gradient Boosting Forecast")

df_ml = merged_df.copy()

# Create lag features
df_ml["storage_lag1"] = df_ml["CURRENT STORAGE BCM"].shift(1)
df_ml["storage_lag2"] = df_ml["CURRENT STORAGE BCM"].shift(2)
df_ml["rain_lag1"] = df_ml["Rainfall_mm"].shift(1)
df_ml["rain_lag2"] = df_ml["Rainfall_mm"].shift(2)

df_ml = df_ml.dropna()

features = [
    "storage_lag1",
    "storage_lag2",
    "rain_lag1",
    "rain_lag2"
]

X = df_ml[features]
y = df_ml["CURRENT STORAGE BCM"]

# Time-aware split
split_index = int(len(df_ml) * 0.8)

X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

# Train model
model = GradientBoostingRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)

model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

st.markdown(f"Model MAE: {mae:.4f}")

# -------------------------------------------------
# 3-MONTH ITERATIVE FORECAST
# -------------------------------------------------

last_row = df_ml.iloc[-1]

storage_lag1 = last_row["CURRENT STORAGE BCM"]
storage_lag2 = df_ml.iloc[-2]["CURRENT STORAGE BCM"]
rain_lag1 = last_row["Rainfall_mm"]
rain_lag2 = df_ml.iloc[-2]["Rainfall_mm"]

forecast_values = []

for _ in range(3):

    X_future = np.array([[storage_lag1, storage_lag2, rain_lag1, rain_lag2]])
    pred = model.predict(X_future)[0]

    forecast_values.append(pred)

    storage_lag2 = storage_lag1
    storage_lag1 = pred

storage_forecast = pd.Series(forecast_values)

# -------------------------------------------------
# PLOT FORECAST
# -------------------------------------------------

historical_dates = pd.to_datetime(
    merged_df["Year"].astype(str) + "-" +
    merged_df["Month"].astype(str) + "-01"
)

future_dates = pd.date_range(
    start=historical_dates.iloc[-1],
    periods=4,
    freq="M"
)[1:]

fig_forecast = go.Figure()

fig_forecast.add_trace(go.Scatter(
    x=historical_dates,
    y=merged_df["CURRENT STORAGE BCM"],
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

# -------------------------------------------------
# RISK ASSESSMENT
# -------------------------------------------------

final_forecast = storage_forecast.iloc[-1]
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