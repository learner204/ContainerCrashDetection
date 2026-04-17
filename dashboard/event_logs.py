# Event logs view - Minimal & Elegant

import streamlit as st
import pandas as pd
from database.db import get_connection
from config.settings import EVENT_LABELS

def show_event_logs():
    st.markdown('<div class="page-title">📜 Event History</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Complete log of detected events</div>', unsafe_allow_html=True)
    
    try:
        # Use DatabaseManager from session state
        db_mgr = st.session_state.db_manager
        conn = db_mgr.get_connection()
        df = pd.read_sql("SELECT * FROM events ORDER BY timestamp DESC", conn)
        conn.close()

        # Normalize schema differences (older code expected `prediction`, DB uses `predicted_label`).
        if 'prediction' not in df.columns and 'predicted_label' in df.columns:
            df['prediction'] = df['predicted_label']
        
        if df.empty:
            st.info("No events logged yet. Run some analyses to see results here.")
            return

        if 'prediction' not in df.columns:
            st.error("Events table is missing the prediction column. Expected `predicted_label` or `prediction`.")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Events", len(df))
        with col2:
            warnings = len(df[df['prediction'] == 1])
            st.metric("Warnings", warnings)
        with col3:
            critical = len(df[df['prediction'] == 2])
            st.metric("Critical", critical)
        with col4:
            if len(df) > 1:
                latest = pd.to_datetime(df['timestamp'].iloc[0])
                st.metric("Last Event", latest.strftime("%H:%M:%S"))
            else:
                st.metric("Last Event", "-")
        
        st.divider()
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.multiselect(
                "Filter by Type",
                options=[0, 1, 2, 3],
                format_func=lambda x: EVENT_LABELS.get(x, "Unknown"),
                default=[0, 1, 2, 3]
            )
        with col2:
            limit = st.slider("Show entries", 10, 100, 50, 10)
        
        # Filter data
        df_filtered = df[df['prediction'].isin(filter_type)].head(limit)
        
        # Format for display
        df_display = df_filtered.copy()
        status_icons = {0: '✅', 1: '⚠️', 2: '🚨', 3: '📦'}
        df_display['prediction'] = df_display['prediction'].map(
            lambda x: f"{status_icons.get(int(x), '❓')} {EVENT_LABELS.get(int(x), 'Unknown')}" if pd.notna(x) else "—"
        )
        if 'confidence' in df_display.columns:
            df_display['confidence'] = pd.to_numeric(df_display['confidence'], errors='coerce').map(
                lambda x: f"{x:.1%}" if pd.notna(x) else "—"
            )
        df_display['timestamp'] = pd.to_datetime(df_display['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Rename columns
        df_display = df_display.rename(columns={
            'id': 'ID',
            'timestamp': 'Time',
            'prediction': 'Event',
            'confidence': 'Confidence',
            'alert': 'Alert'
        })
        
        # Display table
        st.dataframe(
            df_display,
            width="stretch",
            height=400,
            hide_index=True
        )
        
        # Export
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            csv = df_display.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv,
                "events.csv",
                "text/csv",
                key="download_csv"
            )
        with col2:
            if st.button("🗑️ Clear All", type="secondary"):
                conn = st.session_state.db_manager.get_connection()
                conn.execute("DELETE FROM events")
                conn.commit()
                conn.close()
                st.success("All events cleared")
                st.rerun()
        
    except Exception as e:
        st.error(f"Error loading events: {str(e)}")
