import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# Block access if not logged in
if not st.session_state.get('logged_in', False):
    st.warning('Please login from the main page first.')
    st.stop()

DB_PATH = 'fleet_data.db'

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def df_from_db():
    conn = get_conn()
    try:
        df = pd.read_sql_query('SELECT * FROM fleet', conn)
    except Exception:
        df = pd.DataFrame(columns=['id','server','parentFleet','fleetNumber','registration','repairStatus','comments','dateCreated','priority'])
    conn.close()
    return df

# Read data
df = df_from_db()

# Clean column names differences (flexible)
col_map = {}
for col in df.columns:
    if col.strip().lower() == 'status':
        col_map[col] = 'repairStatus'
    if col.strip().lower() == 'fleet number':
        col_map[col] = 'fleetNumber'
    if col.strip().lower() == 'date created':
        col_map[col] = 'dateCreated'
if col_map:
    df = df.rename(columns=col_map)

# Sidebar-like filters placed at top of page for Overview
st.markdown('<div style="display:flex;gap:20px;align-items:center">', unsafe_allow_html=True)
status_options = ['All'] + sorted(df['repairStatus'].dropna().unique().tolist()) if not df.empty else ['All']
status = st.selectbox('Repair Status', options=status_options, index=0)
priority = st.selectbox('Priority', options=['All','1','2','3'], index=0)
search = st.text_input('Search (fleet, reg, comments)')
st.markdown('</div>', unsafe_allow_html=True)

# Apply filters
def apply_filters(d):
    dd = d.copy()
    if status != 'All':
        dd = dd[dd['repairStatus'] == status]
    if priority != 'All':
        dd = dd[dd['priority'].astype(str) == str(priority)]
    if search:
        dd = dd[dd].apply(lambda r: search.lower() in ' '.join(map(str,[r.get('parentFleet',''), r.get('fleetNumber',''), r.get('registration',''), r.get('comments','')])).lower(), axis=1) if len(dd)>0 else dd
    return dd

filtered = df.copy()
if status != 'All':
    filtered = filtered[filtered['repairStatus'] == status]
if priority != 'All':
    filtered = filtered[filtered['priority'].astype(str) == str(priority)]
if search:
    filtered = filtered[filtered.apply(lambda r: search.lower() in ' '.join(map(str,[r.get('parentFleet',''), r.get('fleetNumber',''), r.get('registration',''), r.get('comments','')])).lower(), axis=1)]

# Prepare counts
order = ['New','New - vetted','inspected - monitoring','Awaiting material','Offline- pending vetting']
counts = {s: int(filtered[filtered['repairStatus']==s].shape[0]) for s in order}

st.header('Overview')
kcols = st.columns(5)
colors = {'New':'#ef4444','New - vetted':'#f59e0b','inspected - monitoring':'#facc15','Awaiting material':'#60a5fa','Offline- pending vetting':'#34d399'}
for c,s in zip(kcols, order):
    c.markdown(f"<div style='background:{colors[s]};padding:18px;border-radius:8px;text-align:center;color:#081224;'><h4 style='margin:0'>{s}</h4><h2 style='margin:0'>{counts[s]}</h2></div>", unsafe_allow_html=True)

st.markdown('---')

# Chart
chart_df = pd.DataFrame({'status': list(counts.keys()), 'count': list(counts.values())})
fig = px.bar(chart_df, x='status', y='count', color='status', color_discrete_map=colors)
fig.update_layout(plot_bgcolor='#071123',paper_bgcolor='#071123',font_color='white',xaxis_title='',yaxis_title='')
st.plotly_chart(fig, use_container_width=True, theme=None)

st.markdown('---')
st.subheader('Quick table (Overview style)')
quick = df[['parentFleet','fleetNumber','repairStatus','comments','priority']].copy() if not df.empty else pd.DataFrame(columns=['parentFleet','fleetNumber','repairStatus','comments','priority'])
quick.columns = ['Parent Fleet','Fleet number','Repair status','Comments','Priority']
if status != 'All':
    quick = quick[quick['Repair status']==status]
if priority != 'All':
    quick = quick[quick['Priority'].astype(str)==str(priority)]
if search:
    quick = quick[quick.apply(lambda r: search.lower() in ' '.join(map(str,[r.get('Parent Fleet',''), r.get('Fleet number',''), r.get('Comments','')])).lower(), axis=1)]
# show top 10
st.table(quick.head(10))
