import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AQUA NEXUS - Advanced Reservoir AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# FUTURISTIC SCI-FI DESIGN SYSTEM
# -------------------------------------------------
st.markdown("""
<style>
    :root {
        --primary: #00d4ff;
        --secondary: #ff006e;
        --accent: #8338ec;
        --danger: #ff006e;
        --success: #00ff88;
        --bg-dark: #0a0e27;
        --bg-card: #141829;
        --border-color: #1f2937;
        --text-primary: #e0e7ff;
    }

    * {
        margin: 0;
        padding: 0;
    }

    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%) !important;
        color: #e0e7ff !important;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%) !important;
        color: #e0e7ff !important;
    }

    /* GLOWING HEADERS */
    h1 {
        background: linear-gradient(135deg, #00d4ff 0%, #ff006e 50%, #8338ec 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
        font-size: 3.5rem !important;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.3) !important;
        letter-spacing: 2px !important;
        margin-bottom: 20px !important;
    }

    h2 {
        color: #00d4ff !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.2) !important;
        margin-top: 30px !important;
    }

    h3 {
        color: #ff006e !important;
        font-weight: 600 !important;
        text-shadow: 0 0 15px rgba(255, 0, 110, 0.2) !important;
    }

    /* METRIC CARDS - GLASSMORPHISM */
    [data-testid="stMetric"] {
        background: rgba(20, 24, 41, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 15px !important;
        padding: 25px !important;
        margin: 10px 0 !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.15), inset 0 0 20px rgba(131, 56, 236, 0.05) !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stMetric"]:hover {
        border-color: rgba(255, 0, 110, 0.6) !important;
        box-shadow: 0 0 40px rgba(255, 0, 110, 0.3), inset 0 0 30px rgba(131, 56, 236, 0.1) !important;
        transform: translateY(-5px) !important;
    }

    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.1), transparent);
        animation: shimmer 3s infinite;
    }

    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    /* PROGRESS BARS */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #00ff88 0%, #00d4ff 50%, #8338ec 100%) !important;
        height: 8px !important;
        border-radius: 10px !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.5) !important;
    }

    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, #8338ec 0%, #00d4ff 100%) !important;
        color: #0a0e27 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 12px 30px !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 20px rgba(131, 56, 236, 0.4) !important;
    }

    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.6) !important;
    }

    /* SELECTBOX & INPUT */
    .stSelectbox, .stSlider, .stRadio {
        background: rgba(20, 24, 41, 0.6) !important;
    }

    .stSelectbox > div > div {
        border: 2px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 10px !important;
        background: rgba(20, 24, 41, 0.9) !important;
    }

    /* DIVIDER */
    hr {
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        margin: 30px 0 !important;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: rgba(20, 24, 41, 0.95) !important;
        border-right: 2px solid rgba(0, 212, 255, 0.2) !important;
    }

    /* TEXT STYLING */
    .stMarkdown {
        color: #e0e7ff !important;
    }

    /* RADIO BUTTONS */
    .stRadio > div {
        background: rgba(0, 212, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 15px !important;
        border: 2px solid rgba(0, 212, 255, 0.2) !important;
    }

    /* SLIDERS */
    .stSlider > div > div > div {
        background: rgba(0, 212, 255, 0.2) !important;
    }

    /* WARNING BOXES */
    .stAlert {
        background: rgba(255, 0, 110, 0.1) !important;
        border: 2px solid rgba(255, 0, 110, 0.4) !important;
        border-radius: 10px !important;
        color: #ff9ff3 !important;
    }

    /* SUCCESS BOXES */
    .stSuccess {
        background: rgba(0, 255, 136, 0.1) !important;
        border: 2px solid rgba(0, 255, 136, 0.4) !important;
        border-radius: 10px !important;
        color: #00ff88 !important;
    }

    /* CUSTOM SCROLLBAR */
    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(0, 212, 255, 0.05);
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00d4ff, #8338ec);
        border-radius: 5px;
    }

    /* ANIMATED BORDERS */
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 255, 0.3); }
        50% { box-shadow: 0 0 40px rgba(255, 0, 110, 0.4); }
    }

    /* NEON LINES */
    .divider-neon {
        height: 2px;
        background: linear-gradient(90deg, transparent, #00d4ff, transparent);
        margin: 30px 0;
        animation: glow 3s ease-in-out infinite;
    }
</style>

<script>
    // Animated background effect
    const canvas = document.createElement('canvas');
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.zIndex = '-1';
    canvas.style.opacity = '0.1';
    document.body.appendChild(canvas);
</script>
""", unsafe_allow_html=True)

# TITLE WITH ANIMATION
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1>🌌 AQUA NEXUS</h1>
    <p style="font-size: 1.2rem; color: #00d4ff; letter-spacing: 3px; margin-top: -10px;">
        ADVANCED AUTONOMOUS RESERVOIR CONTROL SYSTEM
    </p>
    <div class="divider-neon"></div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SAMPLE RESERVOIR DATA
# -------------------------------------------------
dams = {
    "Mettur Dam": 78,
    "Bhavanisagar Dam": 62,
    "Vaigai Dam": 91,
    "Amaravathi Dam": 45
}

dam_capacities = {
    "Mettur Dam": 32700,
    "Bhavanisagar Dam": 13000,
    "Vaigai Dam": 3300,
    "Amaravathi Dam": 5500
}

dam_descriptions = {
    "Mettur Dam": "Primary water supply & hydroelectric facility",
    "Bhavanisagar Dam": "Irrigation & flood control system",
    "Vaigai Dam": "Agricultural water distribution hub",
    "Amaravathi Dam": "Regional conservation matrix"
}

# -------------------------------------------------
# SIMULATION FUNCTIONS
# -------------------------------------------------
def simulate_inflow(days):
    base = 600
    trend = np.linspace(0, 150, days)
    noise = np.random.normal(0, 40, days)
    return base + trend + noise

def simulate_storage_projection(current_storage, inflow, release_rate):
    storage = current_storage
    storage_history = []

    for daily_inflow in inflow:
        evaporation_loss = 0.15
        storage += (daily_inflow / 1000)
        storage -= (release_rate / 1000)
        storage -= evaporation_loss
        storage = max(0, min(100, storage))
        storage_history.append(storage)

    return storage_history

def calculate_days_to_threshold(storage_history, threshold):
    for i, value in enumerate(storage_history):
        if value >= threshold:
            return i + 1
    return None

def classify(storage):
    if storage >= 95:
        return "CRITICAL HIGH ⚠️"
    elif storage >= 75:
        return "OPTIMAL 🟢"
    elif storage >= 40:
        return "MODERATE 🟡"
    else:
        return "CRITICAL LOW 🔴"

def get_status_color(storage):
    if storage >= 95:
        return "#ff006e"  # Danger red
    elif storage >= 75:
        return "#00ff88"  # Success green
    elif storage >= 40:
        return "#ffd000"  # Warning yellow
    else:
        return "#ff1744"  # Critical red

# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 30px; padding: 20px; 
border-radius: 10px; background: rgba(0, 212, 255, 0.1); border: 2px solid rgba(0, 212, 255, 0.3);">
    <h3 style="color: #00d4ff; margin: 0;">⚡ NEXUS CONTROL</h3>
    <p style="color: #8338ec; margin: 5px 0 0 0; font-size: 0.9rem;">v2.1 NEURAL</p>
</div>
""", unsafe_allow_html=True)

mode = st.sidebar.radio(
    "🎯 OPERATIONAL MODE",
    ["Public Dashboard", "Advanced Analytics", "Risk Analysis"],
    help="Select system mode for viewing"
)

st.sidebar.markdown("---")

# Display system status
st.sidebar.markdown("""
<div style="background: rgba(0, 255, 136, 0.1); border: 2px solid rgba(0, 255, 136, 0.3); 
border-radius: 10px; padding: 15px; text-align: center;">
    <p style="color: #00ff88; font-weight: bold; margin: 0; font-size: 1.1rem;">✓ SYSTEM ONLINE</p>
    <p style="color: #00d4ff; font-size: 0.85rem; margin: 5px 0 0 0;">All sensors operational</p>
</div>
""", unsafe_allow_html=True)

# =================================================
# MODE 1: PUBLIC DASHBOARD
# =================================================
if mode == "Public Dashboard":
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(131, 56, 236, 0.1)); 
    border: 2px solid rgba(0, 212, 255, 0.3); border-radius: 15px; padding: 25px; margin: 20px 0;">
        <h2 style="margin-top: 0;">🛰️ REAL-TIME RESERVOIR NETWORK STATUS</h2>
        <p style="color: #00d4ff; font-size: 1.1rem;">Live monitoring of all regional water facilities</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    
    for idx, (dam, level) in enumerate(dams.items()):
        col = cols[idx % 2]
        
        with col:
            status_color = get_status_color(level)
            status_text = classify(level)
            capacity = dam_capacities[dam]
            description = dam_descriptions[dam]
            
            st.markdown(f"""
            <div style="background: rgba(20, 24, 41, 0.8); backdrop-filter: blur(10px); 
            border: 2px solid {status_color}; border-radius: 15px; padding: 25px; margin: 15px 0;
            box-shadow: 0 0 30px rgba({status_color}, 0.2);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #00d4ff;">{dam}</h3>
                    <span style="background: {status_color}; color: white; padding: 5px 15px; 
                    border-radius: 20px; font-weight: bold; font-size: 0.9rem;">{status_text}</span>
                </div>
                
                <p style="color: #a0aec0; margin: 10px 0; font-size: 0.95rem;">{description}</p>
                
                <div style="background: linear-gradient(90deg, #8338ec, #00d4ff); 
                background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                font-size: 2.5rem; font-weight: bold; margin: 15px 0;">
                    {level}%
                </div>
                
                <div style="margin: 15px 0;">
                    <div style="background: rgba(0, 212, 255, 0.2); height: 12px; border-radius: 10px; overflow: hidden;">
                        <div style="width: {level}%; height: 100%; background: linear-gradient(90deg, #00ff88, #00d4ff, #ff006e); 
                        box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);"></div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px;">
                    <div style="background: rgba(0, 212, 255, 0.1); padding: 10px; border-radius: 8px; border-left: 3px solid #00d4ff;">
                        <p style="color: #00d4ff; font-size: 0.85rem; margin: 0; font-weight: bold;">CAPACITY</p>
                        <p style="color: #e0e7ff; font-size: 1.1rem; margin: 5px 0 0 0;">{capacity:,} Mm³</p>
                    </div>
                    <div style="background: rgba(255, 0, 110, 0.1); padding: 10px; border-radius: 8px; border-left: 3px solid #ff006e;">
                        <p style="color: #ff006e; font-size: 0.85rem; margin: 0; font-weight: bold;">CURRENT</p>
                        <p style="color: #e0e7ff; font-size: 1.1rem; margin: 5px 0 0 0;">{int(capacity * level / 100):,} Mm³</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# =================================================
# MODE 2: ADVANCED ANALYTICS
# =================================================
elif mode == "Advanced Analytics":
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(131, 56, 236, 0.1)); 
    border: 2px solid rgba(0, 212, 255, 0.3); border-radius: 15px; padding: 25px; margin: 20px 0;">
        <h2 style="margin-top: 0;">📊 PREDICTIVE ANALYTICS ENGINE</h2>
        <p style="color: #00d4ff; font-size: 1.1rem;">AI-powered forecasting and optimization</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        dam_name = st.selectbox("🎯 SELECT RESERVOIR", list(dams.keys()))
    
    with col2:
        forecast_days = st.slider("📅 FORECAST HORIZON", 3, 30, 14)
    
    with col3:
        release_factor = st.slider("💧 RELEASE STRATEGY", 0.3, 1.0, 0.6, step=0.1)

    current_storage = dams[dam_name]
    inflow = simulate_inflow(forecast_days)
    avg_inflow = np.mean(inflow)
    recommended_release = int(avg_inflow * release_factor)

    storage_projection = simulate_storage_projection(
        current_storage,
        inflow,
        recommended_release
    )

    days_to_full = calculate_days_to_threshold(storage_projection, 100)
    days_to_critical_high = calculate_days_to_threshold(storage_projection, 95)
    days_to_critical_low = calculate_days_to_threshold(storage_projection, 20)

    st.markdown("---")
    
    # KEY METRICS
    st.markdown("### ⚡ KEY PERFORMANCE METRICS")
    
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        st.metric(
            "🔋 CURRENT LEVEL",
            f"{current_storage}%",
            delta=f"{current_storage - 50} %",
            delta_color="inverse"
        )
    
    with metric_cols[1]:
        st.metric(
            "📈 AVG INFLOW",
            f"{int(avg_inflow)} m³/s",
            delta=f"+{int(avg_inflow * 0.05)} per day"
        )
    
    with metric_cols[2]:
        st.metric(
            "💧 RECOMMENDED RELEASE",
            f"{recommended_release} m³/s",
            delta=f"{int(recommended_release * 0.1)} efficiency"
        )
    
    with metric_cols[3]:
        evaporation_est = np.mean(inflow) * 0.15
        st.metric(
            "☀️ EVAPORATION LOSS",
            f"{int(evaporation_est)} m³/s",
            delta="-2% vs avg"
        )

    st.markdown("---")
    
    # PROJECTION FORECAST
    st.markdown("### 🎯 STORAGE FORECAST")
    
    projection_df = pd.DataFrame({
        "Day": range(1, forecast_days + 1),
        "Projected Storage (%)": storage_projection
    })

    # Create interactive Plotly chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=projection_df["Day"],
        y=projection_df["Projected Storage (%)"],
        mode='lines+markers',
        name='Storage Level',
        line=dict(color='#00d4ff', width=3),
        marker=dict(size=8, color='#8338ec', symbol='diamond'),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 255, 0.15)',
        hovertemplate='<b>Day %{x}</b><br>Storage: %{y:.1f}%<extra></extra>'
    ))
    
    # Add threshold lines
    fig.add_hline(y=100, line_dash="dash", line_color="#ff006e", 
                  annotation_text="MAX CAPACITY", annotation_position="right")
    fig.add_hline(y=95, line_dash="dot", line_color="#ffd000", 
                  annotation_text="CRITICAL HIGH", annotation_position="right")
    fig.add_hline(y=20, line_dash="dot", line_color="#ff1744", 
                  annotation_text="CRITICAL LOW", annotation_position="right")
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(10, 14, 39, 0.95)',
        plot_bgcolor='rgba(20, 24, 41, 0.95)',
        font=dict(family='Arial', size=12, color='#e0e7ff'),
        title=dict(text='<b>Storage Level Projection</b>', font=dict(size=16, color='#00d4ff')),
        xaxis_title='Days',
        yaxis_title='Storage Level (%)',
        hovermode='x unified',
        margin=dict(l=0, r=0, t=40, b=0),
        height=450,
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0, 212, 255, 0.1)'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0, 212, 255, 0.1)'),
    )
    
    st.plotly_chart(fig, width='stretch')

    st.markdown("---")
    
    # PROJECTION STATUS
    st.markdown("### 🔮 PREDICTIVE ALERTS")
    
    alert_cols = st.columns(3)
    
    with alert_cols[0]:
        if days_to_full:
            st.success(f"✓ FULL CAPACITY in ~{days_to_full} days", icon="✅")
        else:
            st.info("Will not reach full capacity", icon="ℹ️")
    
    with alert_cols[1]:
        if days_to_critical_high:
            st.warning(f"⚠️ CRITICAL HIGH in ~{days_to_critical_high} days", icon="⚠️")
        else:
            st.info("High levels unlikely", icon="ℹ️")
    
    with alert_cols[2]:
        if days_to_critical_low:
            st.error(f"🔴 CRITICAL LOW in ~{days_to_critical_low} days", icon="🔴")
        else:
            st.success("Low levels unlikely", icon="✅")

    st.markdown("---")
    
    # INFLOW DISTRIBUTION
    st.markdown("### 📊 INFLOW DISTRIBUTION ANALYSIS")
    
    inflow_df = pd.DataFrame({
        "Day": range(1, forecast_days + 1),
        "Inflow (m³/s)": inflow
    })
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=inflow_df["Day"],
        y=inflow_df["Inflow (m³/s)"],
        name='Daily Inflow',
        marker=dict(
            color=inflow_df["Inflow (m³/s)"],
            colorscale=['#8338ec', '#00d4ff', '#ff006e'],
            showscale=True,
            colorbar=dict(title="Inflow m³/s")
        ),
        hovertemplate='<b>Day %{x}</b><br>Inflow: %{y:.0f} m³/s<extra></extra>'
    ))
    
    fig2.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(10, 14, 39, 0.95)',
        plot_bgcolor='rgba(20, 24, 41, 0.95)',
        font=dict(family='Arial', size=12, color='#e0e7ff'),
        title=dict(text='<b>Water Inflow Pattern</b>', font=dict(size=16, color='#00d4ff')),
        xaxis_title='Days',
        yaxis_title='Inflow (m³/s)',
        hovermode='x unified',
        margin=dict(l=0, r=0, t=40, b=0),
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig2, width='stretch')

    st.markdown("---")
    
    # RISK ASSESSMENT
    st.markdown("### ⚠️ RISK CLASSIFICATION")
    
    risk_col1, risk_col2 = st.columns([1, 2])
    
    with risk_col1:
        status = classify(current_storage)
        color = get_status_color(current_storage)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2), transparent);
        border: 2px solid {color}; border-radius: 15px; padding: 20px; text-align: center;">
            <h3 style="margin: 0; color: {color}; font-size: 1.8rem;">{status}</h3>
            <p style="color: #a0aec0; margin: 10px 0 0 0;">Current status</p>
        </div>
        """, unsafe_allow_html=True)
    
    with risk_col2:
        risk_data = {
            'Very Low (0-20%)': len([s for s in storage_projection if s < 20]),
            'Low (20-40%)': len([s for s in storage_projection if 20 <= s < 40]),
            'Moderate (40-75%)': len([s for s in storage_projection if 40 <= s < 75]),
            'High (75-95%)': len([s for s in storage_projection if 75 <= s < 95]),
            'Critical (95-100%)': len([s for s in storage_projection if s >= 95])
        }
        
        fig3 = go.Figure(data=[go.Pie(
            labels=list(risk_data.keys()),
            values=list(risk_data.values()),
            marker=dict(colors=['#ff1744', '#ffd000', '#00d4ff', '#00ff88', '#ff006e']),
            hovertemplate='<b>%{label}</b><br>Days: %{value}<extra></extra>'
        )])
        
        fig3.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(10, 14, 39, 0)',
            font=dict(family='Arial', size=11, color='#e0e7ff'),
            margin=dict(l=0, r=0, t=20, b=0),
            height=350
        )
        
        st.plotly_chart(fig3, width='stretch')

# =================================================
# MODE 3: RISK ANALYSIS
# =================================================
else:
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255, 0, 110, 0.1), rgba(131, 56, 236, 0.1)); 
    border: 2px solid rgba(255, 0, 110, 0.3); border-radius: 15px; padding: 25px; margin: 20px 0;">
        <h2 style="margin-top: 0;">🚨 CRITICAL RISK ANALYSIS</h2>
        <p style="color: #ff006e; font-size: 1.1rem;">Deep-dive risk assessment and mitigation strategies</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎯 RISK MATRIX", "🔍 ANOMALY DETECTION", "💡 RECOMMENDATIONS"])
    
    with tab1:
        st.markdown("### NETWORK RISK ASSESSMENT")
        
        risk_matrix = []
        for dam, level in dams.items():
            risk_matrix.append({
                'Reservoir': dam,
                'Current Level (%)': level,
                'Capacity (Mm³)': dam_capacities[dam],
                'Evaporation Risk': 'HIGH' if level > 80 else 'MEDIUM' if level > 50 else 'LOW',
                'Overflow Risk': 'CRITICAL' if level > 95 else 'HIGH' if level > 85 else 'MODERATE',
                'Drought Risk': 'CRITICAL' if level < 20 else 'HIGH' if level < 40 else 'LOW'
            })
        
        risk_df = pd.DataFrame(risk_matrix)
        
        st.dataframe(
            risk_df.style.format({
                'Current Level (%)': '{:.0f}',
                'Capacity (Mm³)': '{:,.0f}'
            }).applymap(
                lambda x: 'background-color: rgba(255, 0, 110, 0.3); color: #ff006e;' if 'CRITICAL' in str(x) 
                else 'background-color: rgba(255, 208, 0, 0.3); color: #ffd000;' if 'HIGH' in str(x) 
                else 'background-color: rgba(0, 255, 136, 0.3); color: #00ff88;'
                if 'LOW' in str(x) or (isinstance(x, str) and x.isdigit()) else ''
            ),
            width='stretch'
        )
    
    with tab2:
        st.markdown("### ANOMALY DETECTION ENGINE")
        
        selected_dam = st.selectbox("📍 Analyze Reservoir", list(dams.keys()), key="anomaly_select")
        
        # Simulate anomaly detection
        normal_inflow = simulate_inflow(30)
        anomaly_days = np.random.choice(range(30), 3, replace=False)
        anomalous_inflow = normal_inflow.copy()
        for day in anomaly_days:
            anomalous_inflow[day] *= np.random.uniform(0.5, 2.0)
        
        anomaly_df = pd.DataFrame({
            'Day': range(1, 31),
            'Normal Pattern': normal_inflow,
            'Current Reading': anomalous_inflow,
            'Deviation': np.abs(anomalous_inflow - normal_inflow)
        })
        
        fig4 = go.Figure()
        
        fig4.add_trace(go.Scatter(
            x=anomaly_df['Day'],
            y=anomaly_df['Normal Pattern'],
            name='Expected Pattern',
            line=dict(color='#00d4ff', width=2, dash='dash'),
            hovertemplate='<b>Day %{x}</b><br>Expected: %{y:.0f}<extra></extra>'
        ))
        
        fig4.add_trace(go.Scatter(
            x=anomaly_df['Day'],
            y=anomaly_df['Current Reading'],
            name='Current Reading',
            line=dict(color='#ff006e', width=3),
            marker=dict(size=6),
            hovertemplate='<b>Day %{x}</b><br>Current: %{y:.0f}<extra></extra>'
        ))
        
        fig4.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(10, 14, 39, 0.95)',
            plot_bgcolor='rgba(20, 24, 41, 0.95)',
            font=dict(family='Arial', size=12, color='#e0e7ff'),
            title=dict(text='<b>Inflow Pattern Anomaly Detection</b>', font=dict(size=16, color='#ff006e')),
            xaxis_title='Days',
            yaxis_title='Inflow (m³/s)',
            hovermode='x unified',
            height=450,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig4, width='stretch')
        
        st.markdown(f"**Anomalies Detected:** {len(anomaly_days)} events")
        for day in anomaly_days:
            deviation = anomaly_df.loc[day, 'Deviation']
            st.warning(f"📊 Day {day + 1}: {deviation:.0f} m³/s deviation from baseline")
    
    with tab3:
        st.markdown("### 💡 INTELLIGENT MITIGATION STRATEGIES")
        
        for dam, level in dams.items():
            status_color = get_status_color(level)
            
            if level >= 95:
                rec = "IMMEDIATE ACTION: Increase spillway release to prevent overflow. Coordinate downstream communication."
                icon = "🚨"
            elif level >= 85:
                rec = "PREVENTIVE: Gradually increase release rates. Monitor weather forecast for additional inflow."
                icon = "⚠️"
            elif level >= 60:
                rec = "OPTIMAL: Maintain current release strategy. System operating within safe parameters."
                icon = "✓"
            elif level >= 40:
                rec = "ADVISORY: Monitor drought conditions. Begin conservation protocols if extended dry period expected."
                icon = "📋"
            else:
                rec = "CRITICAL: Implement emergency water conservation. Prepare for potential supply disruption."
                icon = "🔴"
            
            st.markdown(f"""
            <div style="background: rgba({int(status_color[1:3], 16)}, {int(status_color[3:5], 16)}, {int(status_color[5:7], 16)}, 0.1);
            border-left: 4px solid {status_color}; border-radius: 8px; padding: 15px; margin: 10px 0;">
                <p style="margin: 0; color: {status_color}; font-weight: bold; font-size: 1.1rem;">
                    {icon} {dam} ({level}%)
                </p>
                <p style="margin: 10px 0 0 0; color: #e0e7ff;">
                    {rec}
                </p>
            </div>
            """, unsafe_allow_html=True)