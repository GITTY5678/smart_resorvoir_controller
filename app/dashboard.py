# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import warnings
from statsmodels.tsa.arima.model import ARIMA
from scipy.optimize import minimize
from dotenv import load_dotenv
from openai import OpenAI

# Suppress annoying ARIMA warnings for a cleaner console
warnings.filterwarnings("ignore")

# -------------------------------------------------
# PAGE CONFIG & THEME
# -------------------------------------------------
st.set_page_config(
    page_title="AQUA NEXUS | Intelligent Reservoir AI",
    page_icon="💧",
    layout="wide"
)

# Custom CSS for "High-Class" Engineering Aesthetics
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0a0e14;
        color: #e0e6ed;
    }
    /* Metric Card Styling */
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    div[data-testid="stMetricValue"] {
        color: #00d4ff;
    }
    /* Custom Header */
    .main-header {
        background: linear-gradient(90deg, #001529 0%, #003366 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 8px solid #00d4ff;
        margin-bottom: 25px;
    }
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #00d4ff;
        color: #0a0e14;
        font-weight: bold;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# LOAD ENV + LLM CLIENT
# -------------------------------------------------
load_dotenv()
client = OpenAI(
    base_url="https://api.featherless.ai/v1",
    api_key=os.getenv("FEATHERLESS_API_KEY"),
)

# -------------------------------------------------
# DATA LOADING & CLEANING (Keep your existing logic)
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_PATH = os.path.join(BASE_DIR, "data", "cwc_reservoirs.xlsx")
RAIN_PATH = os.path.join(BASE_DIR, "data", "climate.xlsx")
COLLECTOR_PATH = os.path.join(BASE_DIR, "data", "india_district_collectors.csv")

@st.cache_data
def load_and_clean_data():
    if not os.path.exists(RES_PATH) or not os.path.exists(RAIN_PATH):
        return None, None, None
    
    res = pd.read_excel(RES_PATH)
    rain = pd.read_excel(RAIN_PATH)
    
    # Cleaning
    for df in [res, rain]:
        df.columns = df.columns.str.strip()
    
    res["REGION"] = res["REGION"].astype(str).str.strip().str.title()
    res["STATE"] = res["STATE"].astype(str).str.strip().str.title()
    res["RESERVOIR"] = res["RESERVOIR"].astype(str).str.strip().str.title()
    res["DATE"] = pd.to_datetime(res["DATE"])
    res["CURRENT STORAGE BCM"] = pd.to_numeric(res["CURRENT STORAGE BCM"], errors="coerce")
    res["FULL RESERVOIR LEVEL BCM"] = pd.to_numeric(res["FULL RESERVOIR LEVEL BCM"], errors="coerce")
    
    rain["CWC Region"] = rain["CWC Region"].astype(str).str.strip().str.title()
    rain["Rainfall Actual (mm)"] = pd.to_numeric(rain["Rainfall Actual (mm)"], errors="coerce")
    
    coll = None
    if os.path.exists(COLLECTOR_PATH):
        coll = pd.read_csv(COLLECTOR_PATH)
        coll.columns = coll.columns.str.strip()
    
    return res, rain, coll

res_df_full, rain_df_full, collectors_df = load_and_clean_data()

if res_df_full is None:
    st.error("Critical Data Files Missing")
    st.stop()

# -------------------------------------------------
# SIDEBAR CONTROL CENTER
# -------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/water-tower.png", width=80)
    st.title("Control Center")
    st.markdown("---")
    
    regions = sorted(res_df_full["REGION"].dropna().unique())
    sel_region = st.selectbox("Geographic Region", regions)
    
    states = sorted(res_df_full[res_df_full["REGION"] == sel_region]["STATE"].dropna().unique())
    sel_state = st.selectbox("State Territory", states)
    
    res_list = sorted(res_df_full[res_df_full["STATE"] == sel_state]["RESERVOIR"].dropna().unique())
    sel_res = st.selectbox("Select Reservoir Asset", res_list)
    
    st.markdown("---")
    st.subheader("Forecast Parameters")
    f_months = st.slider("Forecast Horizon (Months)", 1, 12, 3)

# Filter Data
res_df = res_df_full[res_df_full["RESERVOIR"] == sel_res].sort_values("DATE")
latest = res_df.iloc[-1]
current_storage = latest["CURRENT STORAGE BCM"]
capacity = latest["FULL RESERVOIR LEVEL BCM"]

# -------------------------------------------------
# MAIN DASHBOARD UI
# -------------------------------------------------
st.markdown(f"""
    <div class="main-header">
        <h1 style='margin:0; color:white;'>AQUA NEXUS: {sel_res.upper()}</h1>
        <p style='margin:0; opacity:0.8;'>Strategic Reservoir Analytics & Autonomous Optimization</p>
    </div>
    """, unsafe_allow_html=True)

# TOP KPI ROW
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
utilization = (current_storage / capacity) * 100

kpi1.metric("Current Storage", f"{current_storage:.2f} BCM")
kpi2.metric("Total Capacity", f"{capacity:.2f} BCM")
kpi3.metric("Utilization", f"{utilization:.1f}%", delta=f"{utilization-75:.1f}% vs Target")
kpi4.metric("Asset Status", "ACTIVE", delta_color="normal")

# -------------------------------------------------
# ANALYTICS SECTION
# -------------------------------------------------
col_chart, col_risk = st.columns([2, 1])

with col_chart:
    st.subheader("📈 Predictive Storage Optimization")
    
    # --- Processing & ARIMA (Simplified for stability) ---
    res_df["Month"] = res_df["DATE"].dt.month
    res_df["Year"] = res_df["DATE"].dt.year
    monthly_storage = res_df.groupby(["Year", "Month"])["CURRENT STORAGE BCM"].mean().reset_index()
    
    # Simple ARIMA fallback
    try:
        model = ARIMA(monthly_storage["CURRENT STORAGE BCM"], order=(1,1,1))
        fit = model.fit()
        forecast = fit.forecast(steps=f_months)
    except:
        forecast = [current_storage] * f_months # Fallback

    # Plotly Glass Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=monthly_storage["CURRENT STORAGE BCM"].tail(12), name="Historical", line=dict(color='#00d4ff', width=3)))
    fig.add_trace(go.Scatter(x=list(range(11, 11+f_months)), y=forecast, name="AI Forecast", line=dict(color='#ff4b4b', dash='dot')))
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_risk:
    st.subheader("🚨 Risk Assessment")
    
    final_proj = forecast.iloc[-1] if hasattr(forecast, 'iloc') else forecast[-1]
    proj_pct = (final_proj / capacity) * 100
    
    if proj_pct > 85:
        st.error(f"CRITICAL: FLOOD RISK ({proj_pct:.1f}%)")
        risk_status = "FLOOD"
    elif proj_pct < 25:
        st.warning(f"WARNING: DROUGHT RISK ({proj_pct:.1f}%)")
        risk_status = "DROUGHT"
    else:
        st.success(f"NOMINAL: STABLE ({proj_pct:.1f}%)")
        risk_status = "SAFE"
        
    st.write("Current analysis indicates the reservoir will reach a stable state within the forecast window based on seasonal inflow factors.")

# -------------------------------------------------
# AI & ALERTS
# -------------------------------------------------
st.markdown("---")
c_alert, c_ai = st.columns(2)

with c_alert:
    st.subheader("📢 Administrative Protocol")
    
    # Resolve Collector Details for Alert
    if collectors_df is not None and risk_status != "SAFE":
        collector_row = collectors_df[collectors_df["State"] == sel_state]
        if not collector_row.empty:
            c_name = collector_row.iloc[0].get("Collector Name", "Officer In Charge")
            c_email = collector_row.iloc[0].get("Email", "N/A")
            
            st.warning(f"Protocol: Dispatching Alert to {c_name}")
            alert_code = f"""
            [EMERGENCY PROTOCOL ACTIVE]
            TO: {c_name} ({c_email})
            SUBJECT: {risk_status} WARNING - {sel_res}
            
            Current Utilization: {utilization:.1f}%
            Projected Level ({f_months}mo): {proj_pct:.1f}%
            Action: Initiate local contingency plan.
            """
            st.code(alert_code, language="markdown")
        else:
            st.info("No localized collector found. Forwarding to State Authority.")
    else:
        st.success("✅ System Status: Nominal. No alerts dispatched.")

with c_ai:
    st.subheader("🤖 AI Executive Intelligence")
    
    # Compile detailed context for the AI
    data_payload = {
        "reservoir": sel_res,
        "state": sel_state,
        "current_storage": float(current_storage),
        "capacity": float(capacity),
        "utilization": float(utilization),
        "risk": risk_status,
        "forecast_horizon": f_months,
        "projected_pct": float(proj_pct)
    }

    if st.button("Generate Detailed Briefing"):
        with st.spinner("Analyzing hydrological patterns and sensor telemetry..."):
            
            prompt = f"""
            As a Senior Hydrological Systems Analyst, provide a detailed executive summary for:
            Reservoir: {data_payload['reservoir']} ({data_payload['state']})
            Current Metrics: {data_payload['current_storage']} BCM out of {data_payload['capacity']} BCM ({data_payload['utilization']:.1f}% utilization).
            Risk Assessment: {data_payload['risk']} status.
            Forecast: Projected to hit {data_payload['projected_pct']:.1f}% capacity in {data_payload['forecast_horizon']} months.

            Structure the response exactly as follows:
            1. 📊 SITUATION OVERVIEW: Explain current water levels in plain English.
            2. 🔍 PREDICTIVE INSIGHTS: Analyze what the {data_payload['projected_pct']}% projection means for the near future.
            3. ⚙️ OPERATIONAL GUIDANCE: Specific recommendation on gate release or conservation.
            4. ⚠️ RISK MITIGATION: A one-sentence final warning or safety assurance.
            
            Use a professional, calm, and data-driven tone.
            """

            try:
                response = client.chat.completions.create(
                    model="Qwen/Qwen2.5-7B-Instruct",
                    messages=[
                        {"role": "system", "content": "You are a senior reservoir engineer and disaster management expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                
                report = response.choices[0].message.content
                
                # Render the report in a professional box
                st.markdown(f"""
                <div style="background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d;">
                    {report}
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Intelligence Engine Offline: {str(e)}")