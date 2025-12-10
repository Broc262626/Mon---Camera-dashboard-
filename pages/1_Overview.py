
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')
st.title("📊 Overview")

conn = sqlite3.connect("fleet_data.db")
try:
    df = pd.read_sql_query("SELECT * FROM fleet", conn)
except Exception as e:
    st.error(f"DB error: {e}")
    conn.close()
    st.stop()
conn.close()

if df.empty:
    st.warning("No data in database. Upload an Excel file via Settings.")
    st.stop()

# detect repair status column
status_col = None
for candidate in ['Repair status','repairStatus','Repair Status','Status']:
    if candidate in df.columns:
        status_col = candidate
        break
if status_col is None:
    st.error("Repair status column not found.")
    st.stop()

def normalize(v):
    if pd.isna(v): return 'Other'
    s = str(v).strip().lower()
    if 'new' in s and 'vetted' not in s: return 'New'
    if 'vetted' in s or 'po-approved' in s or 'po approved' in s: return 'New - vetted'
    if 'inspect' in s or 'monitor' in s: return 'Inspected - monitoring'
    if 'await' in s or 'material' in s: return 'Awaiting material'
    if 'offline' in s or 'pending' in s or 'vet' in s: return 'Offline- pending vetting'
    return 'Other'

df['_status_norm'] = df[status_col].apply(normalize)

counts = df['_status_norm'].value_counts()
statuses = ['New','New - vetted','Inspected - monitoring','Awaiting material','Offline- pending vetting']
colors = {'New':'linear-gradient(135deg,#FF6B6B,#FF4B4B)',
          'New - vetted':'linear-gradient(135deg,#FFA751,#FF7C00)',
          'Inspected - monitoring':'linear-gradient(135deg,#FFE259,#F5B916)',
          'Awaiting material':'linear-gradient(135deg,#4DA3FF,#00B4FF)',
          'Offline- pending vetting':'linear-gradient(135deg,#43E97B,#38F9D7)'}

cols = st.columns(5, gap='large')
for c, s in zip(cols, statuses):
    with c:
        val = int(counts.get(s, 0))
        st.markdown(f"""<div style='background:{colors[s]}; padding:18px; border-radius:14px; color:white; text-align:center; box-shadow:0 6px 18px rgba(0,0,0,0.18);'>
                        <div style='font-size:18px; font-weight:600'>{s}</div>
                        <div style='font-size:36px; font-weight:800; margin-top:8px'>{val}</div>
                       </div>""", unsafe_allow_html=True)

st.markdown('---')

chart_df = counts.reindex(statuses).fillna(0).reset_index()
chart_df.columns = ['Status','Count']
fig = px.bar(chart_df, x='Status', y='Count', color='Status', title='Repair Status Distribution')
fig.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

st.markdown('---')
quick_cols = ['Parent fleet','Fleet number', status_col, 'Comments', 'Priority']
existing = [c for c in quick_cols if c in df.columns]
st.subheader('Quick view (first 20 rows)')
st.dataframe(df[existing].head(20), use_container_width=True)
