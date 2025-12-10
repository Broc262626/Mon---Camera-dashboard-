
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')
st.title("📊 Overview Dashboard")

# connect DB
conn = sqlite3.connect("fleet_data.db")
try:
    df = pd.read_sql_query("SELECT * FROM fleet", conn)
except Exception as e:
    st.error(f"Database error: {e}")
    conn.close()
    st.stop()
conn.close()

if df.empty:
    st.warning("No data available. Please import data via the Settings page.")
    st.stop()

# support both possible column names
if 'Repair status' in df.columns:
    status_col = 'Repair status'
elif 'repairStatus' in df.columns:
    status_col = 'repairStatus'
elif 'Repair Status' in df.columns:
    status_col = 'Repair Status'
else:
    st.error("Column 'Repair status' not found in DB. Check your import.")
    st.stop()

# compute counts
status_counts = df[status_col].fillna('Unknown').value_counts()

# modern mixed KPI cards function
def kpi_card(title, value, emoji, gradient):
    st.markdown(f"""
    <style>
    .kpi-card {{ background: {gradient}; backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
                 padding: 18px; border-radius:14px; box-shadow: 0 6px 18px rgba(0,0,0,0.18);
                 text-align:center; color:white; border:1px solid rgba(255,255,255,0.08); }}
    .kpi-card:hover {{ transform: translateY(-6px) scale(1.02); transition: all .2s ease; }}
    </style>
    <div class="kpi-card">
      <div style="font-size:26px">{emoji}</div>
      <div style="font-size:16px; font-weight:600; margin-top:6px;">{title}</div>
      <div style="font-size:36px; font-weight:800; margin-top:6px;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def get_count(name):
    return int(status_counts.get(name, 0))

cols = st.columns(5)
with cols[0]:
    kpi_card('New', get_count('New'), '🟥', 'linear-gradient(135deg,#FF6B6B,#FF4B4B)')
with cols[1]:
    kpi_card('New - vetted', get_count('New - vetted'), '🟧', 'linear-gradient(135deg,#FFA751,#FF7C00)')
with cols[2]:
    kpi_card('Inspected - monitoring', get_count('inspected - monitoring'), '🟨', 'linear-gradient(135deg,#FFE259,#F5B916)')
with cols[3]:
    kpi_card('Awaiting material', get_count('Awaiting material'), '🟦', 'linear-gradient(135deg,#4DA3FF,#00B4FF)')
with cols[4]:
    kpi_card('Offline - pending vetting', get_count('Offline- pending vetting'), '🟩', 'linear-gradient(135deg,#43E97B,#38F9D7)')

st.markdown('---')

# bar chart
chart_df = status_counts.reset_index()
chart_df.columns = ['Status','Count']
fig = px.bar(chart_df, x='Status', y='Count', color='Status', title='Repair Status Distribution')
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.markdown('---')
st.subheader('📋 Quick View')
quick_cols = ['Parent fleet','Fleet number', status_col, 'Comments','Priority']
existing = [c for c in quick_cols if c in df.columns]
st.dataframe(df[existing].head(15), use_container_width=True)
