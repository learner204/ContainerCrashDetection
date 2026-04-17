# Streamlit entry point

import streamlit as st
import plotly.graph_objs as go
import time

from sensors.signal_generator import SignalGenerator
from services.detector import CrashDetector
from services.alert_engine import AlertManager
from config.settings import EVENT_LABELS
from database.db import DatabaseManager
from dashboard.event_logs import show_event_logs
from dashboard.live_view import show_live_view
from dashboard.confidence_gauge import confidence_gauge
from dashboard.severity_bar import severity_bar

# Page configuration must be first Streamlit command
st.set_page_config(
    page_title="Container Crash Detection System",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling with modern color palette
st.markdown("""
    <style>
    /* Professional Color Palette */
    :root {
        --primary-blue: #1565C0;
        --primary-dark: #0D47A1;
        --primary-light: #42A5F5;
        --secondary-teal: #00897B;
        --secondary-light: #4DB6AC;
        --accent-orange: #FF6F00;
        --accent-amber: #FFA726;
        --success-green: #2E7D32;
        --success-light: #4CAF50;
        --danger-red: #C62828;
        --danger-light: #EF5350;
        --warning-yellow: #F57C00;
        --neutral-dark: #424242;
        --neutral-medium: #757575;
        --neutral-light: #BDBDBD;
        --bg-primary: #F5F7FA;
        --bg-secondary: #E3F2FD;
        --bg-accent: #E1F5FE;
    }
    
    /* Main Headers */
    .main-header {
        font-size: 2.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-teal) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    
    /* Sub Headers */
    .sub-header {
        font-size: 1.15rem;
        color: var(--neutral-medium);
        margin-bottom: 2.5rem;
        font-weight: 400;
        line-height: 1.6;
    }
    
    /* Status Legend Card */
    .status-legend {
        background: linear-gradient(135deg, #FFFFFF 0%, #FFFEF9 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(139, 120, 100, 0.15);
        box-shadow: 0 4px 12px rgba(139, 120, 100, 0.08);
        margin: 1.5rem 0;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .status-item:hover {
        background-color: rgba(21, 101, 192, 0.05);
        transform: translateX(4px);
    }
    
    .status-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
        width: 2.5rem;
        text-align: center;
    }
    
    .status-text {
        flex: 1;
    }
    
    .status-title {
        font-weight: 600;
        color: var(--neutral-dark);
        margin-bottom: 0.25rem;
    }
    
    .status-desc {
        font-size: 0.9rem;
        color: var(--neutral-medium);
        line-height: 1.4;
    }
    
    /* Metric Containers */
    .metric-container {
        background: linear-gradient(135deg, #FFFFFF 0%, #FFFEF9 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid var(--primary-blue);
        box-shadow: 0 4px 12px rgba(139, 120, 100, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    }
    
    .metric-container:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(21, 101, 192, 0.2);
        border-left-width: 6px;
    }
    
    /* Info Boxes */
    .info-box {
        background: linear-gradient(135deg, var(--bg-accent) 0%, var(--bg-secondary) 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid var(--secondary-teal);
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 137, 123, 0.12);
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-left: 4px solid;
    }
    
    /* Background - Beige/Mild Colors */
    .main .block-container {
        background: linear-gradient(135deg, #FAF8F3 0%, #F5F1E8 100%);
        padding-top: 2rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #F5F1E8 0%, #FAF8F3 100%);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFEF9 0%, #FAF8F3 100%);
        border-right: 1px solid rgba(139, 120, 100, 0.15);
    }
    
    [data-testid="stSidebar"] .element-container {
        padding: 0.5rem 0;
    }
    
    /* Navigation Radio Buttons - Custom Styling */
    .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .stRadio > div > label {
        background: linear-gradient(135deg, #FFFFFF 0%, #FAF8F3 100%);
        border: 2px solid rgba(139, 120, 100, 0.2);
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
        margin: 0.25rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        font-weight: 500;
        color: #5D4037;
    }
    
    .stRadio > div > label:hover {
        background: linear-gradient(135deg, #FFFEF9 0%, #F5F1E8 100%);
        border-color: rgba(21, 101, 192, 0.4);
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .stRadio > div > label[data-baseweb="radio"] {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-color: #1565C0;
        box-shadow: 0 4px 12px rgba(21, 101, 192, 0.2);
        font-weight: 600;
        color: #1565C0;
    }
    
    /* Button Styling */
    .stButton > button {
        border-radius: 0.75rem;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Selectbox Styling */
    .stSelectbox label {
        color: var(--neutral-dark);
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: var(--bg-secondary);
        border-radius: 0.75rem;
        font-weight: 600;
        color: var(--primary-blue);
        padding: 1rem;
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: rgba(21, 101, 192, 0.1);
    }
    
    /* Metric Styling */
    [data-testid="stMetricValue"] {
        color: var(--primary-blue);
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: var(--neutral-dark);
    }
    
    /* Chart Container */
    .js-plotly-plot {
        border-radius: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }
    
    /* Section Headers */
    h3 {
        color: var(--primary-blue);
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary-blue), transparent);
        margin: 2rem 0;
    }
    
    /* Card Container */
    .card-container {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .card-container:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }
    
    /* Smooth transitions */
    * {
        transition: color 0.2s ease, background-color 0.2s ease;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize application state objects
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'detector' not in st.session_state:
    st.session_state.detector = CrashDetector()
if 'alert_manager' not in st.session_state:
    st.session_state.alert_manager = AlertManager()
if 'signal_generator' not in st.session_state:
    st.session_state.signal_generator = SignalGenerator()

# Initialize database
try:
    st.session_state.db_manager.init_db()
except Exception as e:
    st.error(f"⚠️ Database initialization warning: {str(e)}")

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0 2rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🚢</div>
        <h1 style="font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #1565C0 0%, #00897B 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0;">
            Crash Detection
        </h1>
        <p style="color: #8B7868; font-size: 0.8rem; margin: 0.5rem 0 0 0; font-weight: 500;">ML-Powered Monitoring</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Custom styled navigation
    st.markdown("""
    <div style="padding: 0.5rem 0;">
        <p style="color: #5D4037; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem; padding-left: 0.5rem;">Navigation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation options with icons
    nav_options = {
        "📊 Analysis": "Live Monitoring",
        "📡 Streaming": "Live Streaming",
        "📜 History": "Event Logs"
    }
    
    selected_nav = st.radio(
        "Navigation Menu",
        list(nav_options.keys()),
        label_visibility="collapsed"
    )
    
    # Map to original page names
    page = nav_options[selected_nav]
    
    st.markdown("---")
    
    # System Info Card with beige theme
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FFFEF9 0%, #FAF8F3 100%); padding: 1.25rem; border-radius: 0.75rem; border: 1px solid rgba(139, 120, 100, 0.2); margin: 1rem 0; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);">
        <h3 style="color: #5D4037; font-size: 1rem; font-weight: 700; margin: 0 0 0.75rem 0;">ℹ️ About</h3>
        <p style="color: #6D4C41; font-size: 0.85rem; line-height: 1.6; margin: 0.5rem 0;">
            Real-time monitoring and analysis of container sensor data for crash detection and impact assessment.
        </p>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(139, 120, 100, 0.15);">
            <p style="color: #5D4037; font-size: 0.8rem; margin: 0.25rem 0; font-weight: 600;">Key Features:</p>
            <ul style="color: #6D4C41; font-size: 0.8rem; margin: 0.5rem 0; padding-left: 1.25rem; line-height: 1.8;">
                <li>Real-time signal analysis</li>
                <li>ML-powered detection</li>
                <li>Event logging</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Status Legend with beige theme
    st.markdown("""
    <div style="margin-top: 1.5rem; padding: 1rem; background: linear-gradient(135deg, #FFFEF9 0%, #FAF8F3 100%); border-radius: 0.75rem; border: 1px solid rgba(139, 120, 100, 0.15);">
        <p style="color: #5D4037; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.75rem;">📋 Status Guide</p>
        <div style="font-size: 0.8rem; line-height: 2;">
            <div style="color: #2E7D32; display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="margin-right: 0.5rem;">✅</span> Normal
            </div>
            <div style="color: #FF6F00; display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="margin-right: 0.5rem;">⚠️</span> Warning
            </div>
            <div style="color: #C62828; display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="margin-right: 0.5rem;">🚨</span> Critical
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Page content based on selection
if page == "Live Monitoring":
    st.markdown('<h1 class="main-header">📊 Signal Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Single-shot analysis and simulation tool for testing crash detection algorithms</p>', unsafe_allow_html=True)
    
    # Information box
    with st.expander("ℹ️ How to use this tool", expanded=False):
        st.markdown("""
        **Instructions:**
        1. Select an event type from the dropdown below to simulate different scenarios
        2. The system will generate a synthetic sensor signal for the selected event
        3. The ML model will analyze the signal and provide predictions
        4. Results include prediction type, confidence level, and alert status
        5. Non-normal events are automatically logged to the event history
        """)
    
    st.markdown("---")
    
    # Event simulation controls
    col1, col2 = st.columns([2, 1])
    with col1:
        label = st.selectbox(
            "**Select Event Type to Simulate**",
            list(EVENT_LABELS.keys()),
            format_func=lambda x: EVENT_LABELS[x],
            help="Choose a scenario to test the detection system"
        )
    with col2:
        analyze_btn = st.button("🔍 Analyze Signal", type="primary", width="stretch")
    
    if analyze_btn or 'last_analysis' not in st.session_state:
        with st.spinner("🔄 Analyzing sensor signal..."):
            # Use objects from session state
            signal = st.session_state.signal_generator.generate_signal(label)
            pred, conf = st.session_state.detector.predict(signal)
            
            # Ensure proper type conversion
            pred = int(pred)
            conf = float(conf)
            
            alert = st.session_state.alert_manager.get_alert(pred, conf)
            
            # Store results in session state
            st.session_state.last_analysis = {
                'signal': signal,
                'pred': pred,
                'conf': conf,
                'alert': alert,
                'label': label,
                'analysis_id': time.time(),
            }
            
            # Log event if not normal
            if pred != 0:
                st.session_state.detector.log_event(pred, conf, alert)
                st.success("✅ Event has been logged to the event history")
    
    # Display results if available
    if 'last_analysis' in st.session_state:
        result = st.session_state.last_analysis
        
        # Display signal chart
        st.markdown("### 📊 Sensor Signal Visualization")
        fig = go.Figure()
        
        # Color based on prediction
        line_color = '#1565C0' if result['pred'] == 0 else '#FF6F00' if result['pred'] == 1 else '#C62828'
        
        fig.add_trace(go.Scatter(
            y=result['signal'], 
            mode="lines", 
            name="Sensor Signal",
            line=dict(color=line_color, width=2.5),
            fill='tozeroy',
            fillcolor='rgba(21, 101, 192, 0.1)' if result['pred'] == 0 else 'rgba(255, 111, 0, 0.1)' if result['pred'] == 1 else 'rgba(198, 40, 40, 0.1)'
        ))
        fig.update_layout(
            title={
                'text': f"Signal Analysis: {EVENT_LABELS[result['label']]}",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#1565C0'}
            },
            xaxis_title="Sample Index",
            yaxis_title="Amplitude (g)",
            height=450,
            template="plotly_white",
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#424242', size=12)
        )
        st.plotly_chart(fig, width="stretch")
        
        # Display metrics with professional styling
        st.markdown("### 📈 Analysis Results")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            pred_color = "#1565C0" if result['pred'] == 0 else "#FF6F00" if result['pred'] == 1 else "#C62828"
            st.markdown(f'<p style="margin:0; color: {pred_color}; font-weight: 600; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.5px;">Predicted Event</p>', unsafe_allow_html=True)
            st.markdown(f'<h2 style="margin:0.75rem 0; color: {pred_color}; font-size: 1.75rem; font-weight: 700;">{EVENT_LABELS[result["pred"]]}</h2>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            conf_color = "#2E7D32" if result['conf'] > 0.7 else "#FF6F00" if result['conf'] > 0.4 else "#757575"
            st.markdown(f'<p style="margin:0; color: {conf_color}; font-weight: 600; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.5px;">Confidence Level</p>', unsafe_allow_html=True)
            st.markdown(f'<h2 style="margin:0.75rem 0; color: {conf_color}; font-size: 1.75rem; font-weight: 700;">{result["conf"]:.1%}</h2>', unsafe_allow_html=True)
            # Confidence indicator bar
            bar_width = result['conf'] * 100
            st.markdown(f'<div style="width: 100%; height: 6px; background: rgba(0,0,0,0.1); border-radius: 3px; overflow: hidden; margin-top: 0.5rem;"><div style="width: {bar_width}%; height: 100%; background: {conf_color}; transition: width 0.3s ease;"></div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            status_icon = "✅" if result['pred'] == 0 else "⚠️" if result['pred'] == 1 else "🚨"
            status_color = "#2E7D32" if result['pred'] == 0 else "#FF6F00" if result['pred'] == 1 else "#C62828"
            status_text = "Normal" if result['pred'] == 0 else "Warning" if result['pred'] == 1 else "Critical"
            st.markdown(f'<p style="margin:0; color: {status_color}; font-weight: 600; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.5px;">System Status</p>', unsafe_allow_html=True)
            st.markdown(f'<h2 style="margin:0.75rem 0; color: {status_color}; font-size: 1.75rem; font-weight: 700;">{status_icon}</h2>', unsafe_allow_html=True)
            st.markdown(f'<p style="margin:0; color: {status_color}; font-size: 0.9rem; font-weight: 500;">{status_text}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Reuse live components: confidence gauge + severity bar
        st.markdown("### 🚦 Severity & Confidence")
        level, color = st.session_state.alert_manager.get_severity(result['conf'])
        gauge_col, severity_col = st.columns(2)
        analysis_id = result.get('analysis_id', 0)
        with gauge_col:
            st.plotly_chart(
                confidence_gauge(result['conf']),
                width="stretch",
                key=f"confidence_gauge_single_{analysis_id}",
            )
        with severity_col:
            severity_bar(level, color)
            st.markdown(f"### {result['alert']}")
        
        # Status Legend
        st.markdown("---")
        st.markdown("### 📋 Status Legend")
        st.markdown("""
        <div class="status-legend">
            <div class="status-item">
                <div class="status-icon">✅</div>
                <div class="status-text">
                    <div class="status-title">Normal Operation</div>
                    <div class="status-desc">System is operating within normal parameters. No anomalies detected.</div>
                </div>
            </div>
            <div class="status-item">
                <div class="status-icon">⚠️</div>
                <div class="status-text">
                    <div class="status-title">Warning - Mild Impact</div>
                    <div class="status-desc">A mild impact or container shift has been detected. Monitor closely for any escalation.</div>
                </div>
            </div>
            <div class="status-item">
                <div class="status-icon">🚨</div>
                <div class="status-text">
                    <div class="status-title">Critical - Severe Crash</div>
                    <div class="status-desc">A severe crash or significant impact has been detected. Immediate attention required.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display alert with appropriate styling
        st.markdown("---")
        if result['pred'] == 0:
            st.success(f"**{result['alert']}** - System operating within normal parameters.")
        elif result['pred'] == 2:
            st.error(f"**{result['alert']}** - Immediate attention required. Severe impact detected with {result['conf']:.1%} confidence.")
        else:
            st.warning(f"**{result['alert']}** - Monitor closely. Mild impact detected with {result['conf']:.1%} confidence.")

elif page == "Live Streaming":
    show_live_view()

elif page == "Event Logs":
    show_event_logs()
