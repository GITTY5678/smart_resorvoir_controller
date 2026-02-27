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

# Suppress warnings for a professional console output
warnings.filterwarnings("ignore")

# -------------------------------------------------
# PAGE CONFIG & THEME
# -------------------------------------------------
st.set_page_config(
    page_title="AQUA NEXUS | Intelligent Reservoir AI",
    page_icon="💧",
    layout="wide"
)

# High-Class Custom CSS for Glassmorphism, Premium Hover, and Engineering UI
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
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetricValue"] {
        color: #00d4ff;
        font-weight: 700;
    }
    
    /* Custom Header Gradient */
    .main-header {
        background: linear-gradient(90deg, #001529 0%, #003366 100%);
        padding: 25px;
        border-radius: 15px;
        border-left: 10px solid #00d4ff;
        margin-bottom: 30px;
    }
    
    /* AI Report Text Box */
    .ai-report-box {
        background-color: #161b22;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #30363d;
        line-height: 1.6;
        font-size: 1.05rem;
    }
    
    /* HIGH-CLASS BUTTON HOVER EFFECTS */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #00d4ff;
        color: #0a0e14 !important;
        font-weight: bold;
        height: 3.5em;
        border: none;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2);
        cursor: pointer;
    }

    .stButton>button:hover {
        background-color: #ffffff !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff;
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.6);
        transform: translateY(-3px); /* Subtle lift effect */
    }

    .stButton>button:active {
        transform: translateY(1px);
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
# DATA LOADING & CLEANING
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
    st.error("Critical Data Assets Missing from /data directory.")
    st.stop()

# -------------------------------------------------
# SIDEBAR CONTROL CENTER
# -------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/water-tower.png", width=80)
    st.title("Command Center")
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

# -------------------------------------------------
# CALCULATIONS
# -------------------------------------------------
res_df = res_df_full[res_df_full["RESERVOIR"] == sel_res].sort_values("DATE")
latest = res_df.iloc[-1]
current_storage = latest["CURRENT STORAGE BCM"]
capacity = latest["FULL RESERVOIR LEVEL BCM"]
utilization = (current_storage / capacity) * 100

# -------------------------------------------------
# MAIN DASHBOARD UI
# -------------------------------------------------
st.markdown(f"""
    <div class="main-header">
        <h1 style='margin:0; color:white; letter-spacing: 1px;'>AQUA NEXUS: {sel_res.upper()}</h1>
        <p style='margin:0; opacity:0.8; font-weight: 300;'>Hydrological Intelligence & Autonomous Optimization Protocol</p>
    </div>
    """, unsafe_allow_html=True)

# TOP KPI ROW
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Current Storage", f"{current_storage:.2f} BCM")
kpi2.metric("Total Capacity", f"{capacity:.2f} BCM")
kpi3.metric("Utilization", f"{utilization:.1f}%", delta=f"{utilization-75:.1f}% vs Goal")
kpi4.metric("System Health", "NOMINAL", delta_color="normal")

# -------------------------------------------------
# ANALYTICS SECTION
# -------------------------------------------------
st.markdown("---")
col_chart, col_risk = st.columns([2, 1])

with col_chart:
    st.subheader("📈 Predictive Storage Optimization")
    
    res_df["Month"] = res_df["DATE"].dt.month
    res_df["Year"] = res_df["DATE"].dt.year
    monthly_storage = res_df.groupby(["Year", "Month"])["CURRENT STORAGE BCM"].mean().reset_index()
    
    try:
        model = ARIMA(monthly_storage["CURRENT STORAGE BCM"], order=(1,1,1))
        fit = model.fit()
        forecast = fit.forecast(steps=f_months)
    except:
        forecast = pd.Series([current_storage] * f_months)

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=monthly_storage["CURRENT STORAGE BCM"].tail(12), name="Historical (12m)", line=dict(color='#00d4ff', width=3)))
    fig.add_trace(go.Scatter(x=list(range(11, 11+f_months)), y=forecast, name="AI Projection", line=dict(color='#ff4b4b', dash='dot', width=3)))
    
    fig.update_layout(
        template="plotly_dark", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        height=400, 
        margin=dict(l=0,r=0,t=20,b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, width="stretch")

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
        
    st.info(f"Asset utilization: {utilization:.1f}%. Predicted trend toward {proj_pct:.1f}% capacity.")

# -------------------------------------------------
# AI & ADMINISTRATIVE PROTOCOLS
# -------------------------------------------------
st.markdown("---")
c_alert, c_ai = st.columns(2)

with c_alert:
    st.subheader("📢 Administrative Protocol")
    if collectors_df is not None and risk_status != "SAFE":
        
        # KEY ERROR FIX: Dynamic column identification
        possible_state_cols = ["State", "STATE", "State Name", "State/UT"]
        actual_state_col = next((c for c in possible_state_cols if c in collectors_df.columns), None)

        if actual_state_col:
            collector_row = collectors_df[collectors_df[actual_state_col].astype(str).str.title() == sel_state]
            
            if not collector_row.empty:
                c_name = collector_row.iloc[0].get("Collector Name", "District Collector")
                st.warning(f"Protocol: High-Priority Alert generated for {c_name}")
                
                alert_code = f"""
                [EMERGENCY PROTOCOL ACTIVE]
                ASSET: {sel_res} | RISK: {risk_status}
                CURRENT UTIL: {utilization:.1f}%
                PROJECTION: {proj_pct:.1f}%
                ACTION: Contact {c_name} for immediate localized contingency.
                """
                st.code(alert_code, language="markdown")
            else:
                st.info(f"No specific collector mapping found for {sel_state}.")
        else:
            st.error("Column 'State' not detected in Collector CSV.")
    else:
        st.success("✅ Protocol Status: System Nominal.")

with c_ai:
    st.subheader("🤖 AI Intelligence Briefing")
    # This button now uses the premium CSS hover effects
    if st.button("Generate Detailed Strategic Report"):
        with st.spinner("Synthesizing multi-modal hydrological data..."):
            prompt = f"""
            Act as a Senior Hydrological Engineer. Provide a briefing for:
            Reservoir: {sel_res}, State: {sel_state}
            Current: {current_storage} BCM ({utilization:.1f}% full).
            Risk: {risk_status}. Forecast: {proj_pct:.1f}% in {f_months} months.

            Provide 4 structured sections:
            1. 📊 SITUATION: Current state analysis.
            2. 🔍 PREDICTIVE: Implications of the {proj_pct:.1f}% projection.
            3. ⚙️ OPERATIONAL: Gate/Release recommendations.
            4. ⚠️ SUMMARY: Final security statement.
            """
            try:
                response = client.chat.completions.create(
                    model="Qwen/Qwen2.5-7B-Instruct",
                    messages=[{"role": "user", "content": prompt}]
                )
                report = response.choices[0].message.content
                st.markdown(f'<div class="ai-report-box">{report}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Intelligence Module Error: {str(e)}")