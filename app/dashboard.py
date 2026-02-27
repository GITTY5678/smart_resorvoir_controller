# -------------------------------------------------
# IMPORTS
# -------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

from statsmodels.tsa.arima.model import ARIMA
from scipy.optimize import minimize
from dotenv import load_dotenv
from openai import OpenAI

# -------------------------------------------------
# LOAD ENV + LLM CLIENT
# -------------------------------------------------

load_dotenv()

client = OpenAI(
    base_url="https://api.featherless.ai/v1",
    api_key=os.getenv("FEATHERLESS_API_KEY"),
)

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="AQUA NEXUS - Intelligent Reservoir System",
    layout="wide"
)

st.title("AQUA NEXUS")
st.subheader("Rainfall Forecast + Dynamic Optimization + AI Intelligence")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RES_PATH = os.path.join(BASE_DIR, "data", "cwc_reservoirs.xlsx")
RAIN_PATH = os.path.join(BASE_DIR, "data", "climate.xlsx")
COLLECTOR_PATH = os.path.join(BASE_DIR, "data", "india_district_collectors.csv")

if not os.path.exists(RES_PATH):
    st.error("Reservoir dataset not found.")
    st.stop()

if not os.path.exists(RAIN_PATH):
    st.error("Climate dataset not found.")
    st.stop()

res_df_full = pd.read_excel(RES_PATH)
rain_df_full = pd.read_excel(RAIN_PATH)

# Load collector dataset (NEW)
if os.path.exists(COLLECTOR_PATH):
    collectors_df = pd.read_csv(COLLECTOR_PATH)
    collectors_df.columns = collectors_df.columns.str.strip()
    collectors_df.columns = collectors_df.columns.str.strip()

    # Normalize possible state column names
    if "State" in collectors_df.columns:
        state_col = "State"
    elif "STATE" in collectors_df.columns:
        state_col = "STATE"
    elif "State Name" in collectors_df.columns:
        state_col = "State Name"
    elif "State/UT" in collectors_df.columns:
        state_col = "State/UT"
    else:
        st.error("State column not found in collector dataset.")
        st.stop()

    collectors_df[state_col] = (
        collectors_df[state_col].astype(str).str.strip().str.title()
    )
else:
    collectors_df = None

# -------------------------------------------------
# CLEAN DATA
# -------------------------------------------------

res_df_full.columns = res_df_full.columns.str.strip()
rain_df_full.columns = rain_df_full.columns.str.strip()

res_df_full["REGION"] = res_df_full["REGION"].astype(str).str.strip().str.title()
res_df_full["STATE"] = res_df_full["STATE"].astype(str).str.strip().str.title()
res_df_full["RESERVOIR"] = res_df_full["RESERVOIR"].astype(str).str.strip().str.title()

rain_df_full["CWC Region"] = rain_df_full["CWC Region"].astype(str).str.strip().str.title()

res_df_full["CURRENT STORAGE BCM"] = pd.to_numeric(
    res_df_full["CURRENT STORAGE BCM"], errors="coerce"
)

res_df_full["FULL RESERVOIR LEVEL BCM"] = pd.to_numeric(
    res_df_full["FULL RESERVOIR LEVEL BCM"], errors="coerce"
)

rain_df_full["Rainfall Actual (mm)"] = pd.to_numeric(
    rain_df_full["Rainfall Actual (mm)"], errors="coerce"
)

res_df_full["DATE"] = pd.to_datetime(res_df_full["DATE"])

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------

st.sidebar.header("Reservoir Filters")

regions = sorted(res_df_full["REGION"].dropna().unique())
selected_region = st.sidebar.selectbox("Select Region", regions)

region_df = res_df_full[res_df_full["REGION"] == selected_region]

states = sorted(region_df["STATE"].dropna().unique())
selected_state = st.sidebar.selectbox("Select State", states)

state_df = region_df[region_df["STATE"] == selected_state]

reservoirs = sorted(state_df["RESERVOIR"].dropna().unique())
selected_reservoir = st.sidebar.selectbox("Select Reservoir", reservoirs)

res_df = state_df[state_df["RESERVOIR"] == selected_reservoir].copy()
res_df = res_df.sort_values("DATE")

if res_df.empty:
    st.warning("No data available.")
    st.stop()

latest = res_df.iloc[-1]
current_storage = latest["CURRENT STORAGE BCM"]
capacity = latest["FULL RESERVOIR LEVEL BCM"]

# -------------------------------------------------
# USER INPUTS
# -------------------------------------------------

st.sidebar.markdown("### Forecast Settings")

forecast_months = st.sidebar.number_input(
    "Forecast Horizon (Months)",
    min_value=1,
    max_value=12,
    value=1
)

expected_level = st.sidebar.number_input(
    "Expected Water Level (BCM)",
    min_value=0.0,
    max_value=float(capacity),
    value=float(current_storage)
)

# -------------------------------------------------
# CURRENT STATUS
# -------------------------------------------------

st.header(f"Current Status — {selected_reservoir}")

c1, c2 = st.columns(2)
c1.metric("Current Storage (BCM)", f"{current_storage:.2f}")
c2.metric("Capacity (BCM)", f"{capacity:.2f}")

# -------------------------------------------------
# MONTHLY AGGREGATION
# -------------------------------------------------

res_df["Year"] = res_df["DATE"].dt.year
res_df["Month"] = res_df["DATE"].dt.month

monthly_storage = res_df.groupby(
    ["Year", "Month", "REGION"]
)["CURRENT STORAGE BCM"].mean().reset_index()

rain_df_clean = rain_df_full.copy()

if "Month" in rain_df_clean.columns and "Month No" in rain_df_clean.columns:
    rain_df_clean = rain_df_clean.drop(columns=["Month"])

rain_df_clean = rain_df_clean.rename(columns={
    "CWC Region": "REGION",
    "Month No": "Month",
    "Rainfall Actual (mm)": "Rainfall_mm"
})

rain_df_clean["Month"] = pd.to_numeric(rain_df_clean["Month"], errors="coerce")
rain_df_clean["Rainfall_mm"] = pd.to_numeric(rain_df_clean["Rainfall_mm"], errors="coerce")

monthly_rain = rain_df_clean.groupby(
    ["Year", "Month", "REGION"]
)["Rainfall_mm"].mean().reset_index()

merged_df = pd.merge(
    monthly_storage,
    monthly_rain,
    on=["Year", "Month", "REGION"],
    how="left"
)

merged_df["Rainfall_mm"] = merged_df["Rainfall_mm"].fillna(0)

if len(merged_df) < 12:
    st.warning("Not enough data for forecasting.")
    st.stop()

# -------------------------------------------------
# RAINFALL FORECAST
# -------------------------------------------------

st.markdown("---")
st.subheader("Rainfall Forecast")

rain_series = merged_df["Rainfall_mm"]

rain_model = ARIMA(rain_series, order=(1,1,1))
rain_fit = rain_model.fit()
rain_forecast = rain_fit.forecast(steps=forecast_months)

st.line_chart(rain_forecast)

# -------------------------------------------------
# INFLOW SCALING
# -------------------------------------------------

historical_change = merged_df["CURRENT STORAGE BCM"].diff().abs().mean()
avg_rain = merged_df["Rainfall_mm"].mean()
inflow_factor = max(historical_change / avg_rain, 0.001)

# -------------------------------------------------
# DYNAMIC OPTIMIZATION
# -------------------------------------------------

def dynamic_optimization(current_storage, rainfall_forecast, capacity):

    horizon = len(rainfall_forecast)

    def objective(releases):

        storage = current_storage
        total_cost = 0

        for t in range(horizon):
            inflow = rainfall_forecast[t] * inflow_factor
            storage = storage + inflow - releases[t]
            storage = max(0, min(storage, capacity))

            overflow_penalty = max(0, storage - capacity) ** 2
            drought_penalty = max(0, 0.3 * capacity - storage) ** 2

            total_cost += (
                10 * overflow_penalty +
                5 * drought_penalty
            )

        return total_cost

    initial_guess = np.full(horizon, 0.1 * capacity)
    bounds = [(0, capacity) for _ in range(horizon)]
    result = minimize(objective, initial_guess, bounds=bounds)

    return result.x

optimal_releases = dynamic_optimization(
    current_storage,
    rain_forecast.values,
    capacity
)

# -------------------------------------------------
# SIMULATION
# -------------------------------------------------

storage_sim = []
storage = current_storage

for i in range(forecast_months):
    inflow = rain_forecast.values[i] * inflow_factor
    storage = storage + inflow - optimal_releases[i]
    storage = max(0, min(storage, capacity))
    storage_sim.append(storage)

# -------------------------------------------------
# PLOT STORAGE
# -------------------------------------------------

fig_opt = go.Figure()
fig_opt.add_trace(go.Scatter(
    y=storage_sim,
    mode="lines+markers",
    name="Optimized Storage"
))
fig_opt.update_layout(template="plotly_dark", height=400)
st.plotly_chart(fig_opt, width="stretch")

# -------------------------------------------------
# RISK ASSESSMENT
# -------------------------------------------------

final_storage = storage_sim[-1]
forecast_pct = (final_storage / capacity) * 100

st.markdown("---")
st.subheader("Risk Assessment")

risk_status = "SAFE"

if final_storage >= capacity:
    st.error("Reservoir At Maximum Capacity")
    risk_status = "CRITICAL"
elif forecast_pct > 85:
    st.warning("High Flood Risk")
    risk_status = "FLOOD"
elif forecast_pct < 25:
    st.warning("Drought Risk")
    risk_status = "DROUGHT"
else:
    st.success("Safe Operating Zone")

st.metric("Projected Storage %", f"{forecast_pct:.2f}%")

# -------------------------------------------------
# 🚨 DISTRICT COLLECTOR ALERT SYSTEM (ADDED)
# -------------------------------------------------

st.markdown("---")
st.header("District Collector Alert System")

if collectors_df is not None and risk_status != "SAFE":

    collector_row = collectors_df[
        collectors_df["State"] == selected_state
    ]

    if not collector_row.empty:
        collector_name = collector_row.iloc[0]["Collector Name"]
        collector_email = collector_row.iloc[0]["Email"]
        collector_phone = collector_row.iloc[0]["Phone"]

        alert_message = f"""
        ALERT NOTICE

        Reservoir: {selected_reservoir}
        State: {selected_state}
        Risk Level: {risk_status}
        Projected Storage: {forecast_pct:.2f}%

        Immediate administrative attention required.
        """

        st.error("🚨 ALERT TRIGGERED")
        st.code(alert_message)

        st.write(f"Collector: {collector_name}")
        st.write(f"Email: {collector_email}")
        st.write(f"Phone: {collector_phone}")

    else:
        st.warning("Collector mapping not found.")

elif collectors_df is None:
    st.info("Collector dataset not loaded.")
else:
    st.success("No emergency alert required.")

# -------------------------------------------------
# AI EXECUTIVE SUMMARY (UNCHANGED)
# -------------------------------------------------

st.markdown("---")
st.header("AI Executive Summary")

def generate_ai_summary(data_dict):

    prompt = f"""
    Generate a professional reservoir management summary.

    Reservoir: {data_dict['reservoir']}
    Current Storage: {data_dict['current_storage']} BCM
    Capacity: {data_dict['capacity']} BCM
    Forecast Months: {data_dict['months']}
    Projected Storage: {data_dict['projected']} BCM
    Projected %: {data_dict['projected_pct']}%
    Recommended Average Release: {data_dict['release']} BCM
    Expected Level: {data_dict['expected']} BCM
    """

    try:
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[
                {"role": "system", "content": "You are a reservoir systems analyst."},
                {"role": "user", "content": prompt}
            ],
        )

        return response.model_dump()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"AI Summary Failed: {str(e)}"

release_avg = float(np.mean(optimal_releases))

data_payload = {
    "reservoir": selected_reservoir,
    "current_storage": float(current_storage),
    "capacity": float(capacity),
    "months": forecast_months,
    "projected": float(final_storage),
    "projected_pct": float(forecast_pct),
    "release": release_avg,
    "expected": float(expected_level),
}

if st.button("Generate AI Summary"):
    with st.spinner("Generating intelligent analysis..."):
        summary = generate_ai_summary(data_payload)
    st.write(summary)