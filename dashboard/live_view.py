# Live streaming view - Minimal & Elegant

import streamlit as st
import time
import plotly.graph_objs as go
import numpy as np

from sensors.streaming import stream_signal
from utils.helpers import rolling_buffer
from services.streaming_detectors import detect_from_buffer
from services.alert_engine import get_alert
from config.settings import SAMPLE_RATE, WINDOW_DURATION, EVENT_LABELS
from services.detector import log_event

from dashboard.confidence_gauge import confidence_gauge
from dashboard.severity_bar import severity_bar
from services.severity import get_severity


UPDATE_INTERVAL = max(1, SAMPLE_RATE // 2)
DISPLAY_DOWNSAMPLE = 5

def show_live_view():
    st.markdown('<div class="page-title">📡 Live Streaming</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Real-time continuous monitoring</div>', unsafe_allow_html=True)
    
    # Controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        event_type = st.selectbox(
            "Stream Type",
            list(EVENT_LABELS.keys()),
            format_func=lambda x: EVENT_LABELS[x],
            key="stream_event"
        )
    with col2:
        if st.button("▶️ Start", type="primary", width="stretch", key="start_stream"):
            st.session_state.streaming = True
            st.session_state.stream_buffer = []
            st.session_state.stream_predictions = []
            st.rerun()
    with col3:
        if st.button("⏹️ Stop", width="stretch", key="stop_stream"):
            st.session_state.streaming = False
            st.rerun()
    
    st.divider()
    
    # Status
    if st.session_state.get('streaming', False):
        status_col1, status_col2 = st.columns([1, 3])
        with status_col1:
            st.markdown("**Status:** 🟢 Live")
        with status_col2:
            st.markdown(f"**Monitoring:** {EVENT_LABELS[event_type]}")
    else:
        st.info("Click Start to begin monitoring")
        return
    
    # Placeholders
    chart_placeholder = st.empty()
    metrics_placeholder = st.empty()
    alert_placeholder = st.empty()
    
    # Initialize buffer
    window_size = int(SAMPLE_RATE * WINDOW_DURATION)
    buffer = rolling_buffer(window_size)
    predictions_buffer = []
    
    # Streaming loop
    sample_count = 0
    for sample in stream_signal(event_type):
        if not st.session_state.get('streaming', False):
            break
        
        buffer.append(sample)
        sample_count += 1
        
        # Update display periodically
        if sample_count % UPDATE_INTERVAL == 0:
            # Prediction
            pred_raw, conf_raw = detect_from_buffer(buffer)
            pred = None
            conf = None
            if pred_raw is not None and conf_raw is not None:
                try:
                    pred = int(pred_raw)
                except (TypeError, ValueError):
                    pred = None
                try:
                    conf = float(conf_raw)
                except (TypeError, ValueError):
                    conf = None

            if pred is not None and conf is not None:
                predictions_buffer.append((pred, conf))

                # Keep last 20 predictions
                if len(predictions_buffer) > 20:
                    predictions_buffer = predictions_buffer[-20:]
            
            # Chart
            with chart_placeholder.container():
                display_buffer = list(buffer)[::DISPLAY_DOWNSAMPLE]
                color_map = {0: '#2563eb', 1: '#f59e0b', 2: '#ef4444'}
                pred_for_color = pred if pred is not None else 0
                line_color = color_map.get(pred_for_color, '#2563eb')
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=display_buffer,
                    mode="lines",
                    line=dict(color=line_color, width=2),
                    showlegend=False
                ))
                fig.update_layout(
                    xaxis_title="Sample",
                    yaxis_title="Amplitude (g)",
                    height=300,
                    template="plotly_white",
                    margin=dict(l=40, r=40, t=10, b=40),
                    hovermode='x'
                )
                st.plotly_chart(fig, width="stretch", key=f"chart_{sample_count}")
            
            # Status display (requested logic)
            with metrics_placeholder.container():
                if pred is None or conf is None:
                    st.info(f"Collecting data… {len(buffer)}/{buffer.maxlen} samples")
                else:
                    alert = st.session_state.alert_manager.get_alert(pred, conf)
                    level, color = st.session_state.alert_manager.get_severity(conf)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(
                            confidence_gauge(conf),
                            width="stretch",
                            key=f"confidence_gauge_{sample_count}",
                        )
                    with col2:
                        severity_bar(level, color)
                        st.markdown(f"### {alert}")

                    if pred != 0:
                        st.session_state.detector.log_event(pred, conf, alert)

            # Keep placeholder for layout consistency
            with alert_placeholder.container():
                pass
            
            time.sleep(0.05)
