import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px
from io import BytesIO

ROOT = Path(__file__).parent
DB_PATH = ROOT / "data" / "devices.db"

st.set_page_config(page_title='Camera Repair Dashboard', layout='wide')

STATUS_COLORS = {
    'New': '#1976D2',
    'In Progress': '#FBC02D',
    'AwaitingPO': '#FB8C00',
    'Awaiting Parts': '#FB8C00',
    'Inspected -Monitoring': '#9C27B0',
    'Repaired': '#2E7D32'
}

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data
def load_devices():
    conn = get_conn()
    df = pd.read_sql_query('SELECT * FROM devices', conn)
    conn.close()
    return df

def save_devices(df):
    conn = get_conn()
    df.to_sql('devices', conn, if_exists='replace', index=False)
    conn.close()

def append_devices(df_new):
    conn = get_conn()
    df_old = pd.read_sql_query('SELECT * FROM devices', conn)
    df_combined = pd.concat([df_old, df_new], ignore_index=True)
    df_combined.to_sql('devices', conn, if_exists='replace', index=False)
    conn.close()

def get_users():
    conn = get_conn()
    df = pd.read_sql_query('SELECT * FROM users', conn)
    conn.close()
    return df

# Auth session state
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None

def login_page():
    st.sidebar.header('Sign in')
    username = st.sidebar.text_input('Username')
    password = st.sidebar.text_input('Password', type='password')
    if st.sidebar.button('Sign in'):
        users = get_users()
        match = users[(users['username']==username) & (users['password']==password)]
        if not match.empty:
            st.session_state.user = username
            st.session_state.role = match.iloc[0]['role']
            st.experimental_rerun()
        else:
            st.sidebar.error('Invalid credentials')

if st.session_state.user is None:
    login_page()
    st.markdown("<div style='text-align:center;margin-top:30px'><h2>Camera Repair Dashboard</h2></div>", unsafe_allow_html=True)
    st.info('Use the sidebar to login. Demo: admin/adminpass or viewer/viewpass')
    st.stop()

USER = st.session_state.user
ROLE = st.session_state.role

st.markdown(f"<div style='text-align:center;'><h1>Camera Repair Dashboard</h1><p>Signed in as <strong>{USER}</strong> ({ROLE})</p></div>", unsafe_allow_html=True)
st.markdown('<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">', unsafe_allow_html=True)

page = st.sidebar.selectbox('Page', ['Overview', 'Records', 'Import', 'Admin', 'Logout'])
if page == 'Logout':
    st.session_state.user = None
    st.session_state.role = None
    st.experimental_rerun()

# KPI helpers
@st.cache_data
def kpi_counts(df):
    return df['status'].value_counts().to_dict()

def fleet_summary(df):
    if df.empty:
        return pd.DataFrame(columns=['Fleet','Total Issues','Open','Completed','Priority 1'])
    out = []
    for fleet, g in df.groupby('parent_fleet'):
        total = len(g)
        open_count = int(g[~g['status'].isin(['Repaired'])].shape[0])
        completed = int((g['status']=='Repaired').sum())
        p1 = int((g['priority']=='1').sum())
        out.append({'Fleet': fleet, 'Total Issues': total, 'Open': open_count, 'Completed': completed, 'Priority 1': p1})
    return pd.DataFrame(out).sort_values('Total Issues', ascending=False)

# Normalize uploaded columns
def normalize_columns(df):
    new_cols = {}
    for c in df.columns:
        nc = c.strip()
        new_cols[c] = nc
    df = df.rename(columns=new_cols)
    mapping = {
        'Server':'server', 'Parent fleet':'parent_fleet', 'Fleet number':'fleet_number', 'Fleet number ':'fleet_number',
        'Registration':'registration', 'Status':'status', 'Comments':'comments', 'Date created':'date_created', 'Date created ':'date_created',
        'Priority':'priority', 'serial_number':'serial_number'
    }
    df_cols = {}
    for c in df.columns:
        key = c.strip()
        if key in mapping:
            df_cols[c] = mapping[key]
        else:
            df_cols[c] = c.strip().lower().replace(' ','_')
    df = df.rename(columns=df_cols)
    req = ['server','parent_fleet','fleet_number','registration','status','comments','date_created','priority','serial_number']
    for r in req:
        if r not in df.columns:
            df[r] = ''
    try:
        df['date_created'] = pd.to_datetime(df['date_created']).dt.date.astype(str)
    except Exception:
        df['date_created'] = df['date_created'].astype(str)
    df['priority'] = df['priority'].astype(str)
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()
    return df[req]

# Pages implementation
if page == 'Overview':
    df = load_devices()
    counts = kpi_counts(df)
    cols = st.columns(4, gap='large')
    display_statuses = ['New','In Progress','AwaitingPO','Repaired']
    for i, s in enumerate(display_statuses):
        with cols[i]:
            cnt = counts.get(s,0)
            color = STATUS_COLORS.get(s, '#6c757d')
            st.markdown(f"""<div style='width:180px;height:140px;border-radius:12px;box-shadow:0 6px 18px rgba(0,0,0,0.08); background:{color};display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;margin:8px auto;'> <div style='font-size:28px;'><i class='fa-solid fa-circle'></i></div> <div style='font-weight:700;font-size:28px;margin-top:6px;'>{cnt}</div> <div style='opacity:0.95;margin-top:6px;'>{s}</div> </div>""", unsafe_allow_html=True)
    st.markdown('---')
    left, right = st.columns([2,1])
    with left:
        st.subheader('Status distribution')
        pie_df = pd.DataFrame({'status':list(counts.keys()), 'count':[counts[k] for k in counts.keys()]})
        fig = px.pie(pie_df, names='status', values='count', color='status', color_discrete_map=STATUS_COLORS, hole=0.35)
        fig.update_traces(textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader('Quick stats')
        st.metric('Total devices', df.shape[0])
        st.metric('Priority 1 devices', int((df['priority']=='1').sum()))
    st.markdown('---')
    st.subheader('Parent Fleet summary')
    st.dataframe(fleet_summary(df).reset_index(drop=True), use_container_width=True)
    p1_count = int((df['priority']=='1').sum())
    if p1_count > 0:
        st.markdown(f"<div style='border-radius:8px;padding:12px;margin-top:12px;color:#fff;background:#dc3545'>🚨 <strong>{p1_count} devices with Priority 1</strong></div>", unsafe_allow_html=True)
    else:
        st.info('No Priority 1 devices at the moment.')

elif page == 'Records':
    st.header('Records - Search, Filter, Edit, Delete')
    df = load_devices()
    c1, c2, c3, c4 = st.columns([2,2,2,1])
    fleet_q = c1.text_input('Parent fleet contains')
    server_q = c2.text_input('Server contains')
    status_q = c3.multiselect('Status', options=sorted(df['status'].unique().tolist()), default=sorted(df['status'].unique().tolist()))
    priority_q = c4.selectbox('Priority', options=['All','1','2','3',''], index=0)
    filtered = df.copy()
    if fleet_q:
        filtered = filtered[filtered['parent_fleet'].str.contains(fleet_q, case=False, na=False)]
    if server_q:
        filtered = filtered[filtered['server'].str.contains(server_q, case=False, na=False)]
    if status_q:
        filtered = filtered[filtered['status'].isin(status_q)]
    if priority_q != 'All':
        filtered = filtered[filtered['priority']==priority_q]
    search = st.text_input('Global search (fleet, server, registration, serial)')
    if search:
        mask = (filtered['parent_fleet'].str.contains(search, case=False, na=False)) | (filtered['server'].str.contains(search, case=False, na=False)) | (filtered['registration'].str.contains(search, case=False, na=False)) | (filtered['serial_number'].str.contains(search, case=False, na=False))
        filtered = filtered[mask]
    st.write(f'**{len(filtered)} results**')
    per_page = st.selectbox('Per page', [5,10,20,50], index=1)
    total = len(filtered)
    max_page = max(1, (total-1)//per_page + 1)
    page_num = st.number_input('Page', min_value=1, max_value=max_page, value=1, step=1)
    start = (page_num-1)*per_page
    page_df = filtered.iloc[start:start+per_page].reset_index(drop=True)
    st.dataframe(page_df, use_container_width=True)
    def to_excel_bytes(df):
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='devices')
        out.seek(0)
        return out.getvalue()
    if st.button('Export filtered to Excel'):
        st.download_button('Download .xlsx', to_excel_bytes(filtered), file_name='devices_filtered.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if ROLE == 'admin':
        st.markdown('---')
        st.subheader('Admin: Edit rows (in current page)')
        edited = st.data_editor(page_df, num_rows='dynamic')
        if st.button('Save edits to DB'):
            db = load_devices()
            for _, row in edited.iterrows():
                sn = row.get('serial_number')
                if sn and sn in db['serial_number'].values:
                    db.loc[db['serial_number']==sn, :] = row.values
                else:
                    db = pd.concat([db, pd.DataFrame([row])], ignore_index=True)
            save_devices(db)
            st.success('Saved edits to database.')
        st.markdown('---')
        st.subheader('Admin: Delete rows (select below)')
        to_delete = []
        for idx, r in page_df.iterrows():
            key = f'del_{start + idx}'
            if st.checkbox(f"{r['parent_fleet']} | {r['registration']} | {r['serial_number']}", key=key):
                to_delete.append(r['serial_number'])
        if to_delete:
            if st.button('Delete selected rows'):
                with st.modal('Confirm deletion'):
                    st.write(f'You are about to delete {len(to_delete)} rows. This action cannot be undone.')
                    if st.button('Confirm delete'):
                        db = load_devices()
                        db = db[~db['serial_number'].isin(to_delete)]
                        save_devices(db)
                        st.success(f'Deleted {len(to_delete)} rows.')
    else:
        st.info('View-only users cannot edit or delete.')

elif page == 'Import':
    st.header('Import Excel / CSV (Admin only)')
    if ROLE != 'admin':
        st.info('Only admins can import data.')
    uploaded = st.file_uploader('Upload .xlsx or .csv', type=['xlsx','csv'])
    if uploaded and ROLE == 'admin':
        try:
            if uploaded.name.endswith('.xlsx'):
                raw = pd.read_excel(uploaded, engine='openpyxl', dtype=str)
            else:
                raw = pd.read_csv(uploaded, dtype=str)
            st.write('Preview of uploaded file (first 10 rows):')
            st.dataframe(raw.head(10))
            cleaned = normalize_columns(raw)
            st.write('Preview after normalization (first 10 rows):')
            st.dataframe(cleaned.head(10))
            action = st.radio('Action', ['Append to database','Replace database'], index=0)
            if st.button('Confirm import'):
                if action.startswith('Append'):
                    append_devices(cleaned)
                    st.success('Appended to database.')
                else:
                    save_devices(cleaned)
                    st.success('Replaced database with uploaded data.')
        except Exception as e:
            st.error(f'Import failed: {e}')

elif page == 'Admin':
    st.header('Admin: User management & settings')
    if ROLE != 'admin':
        st.info('Admin area. Only visible to admins.')
    else:
        users = get_conn().cursor().execute('SELECT username,role FROM users').fetchall()
        st.write('Existing users:')
        st.table(pd.DataFrame(users, columns=['username','role']))
        st.markdown('---')
        st.subheader('Add new user (username, password, role)')
        newu = st.text_input('Username', key='newuser')
        newp = st.text_input('Password', type='password', key='newpass')
        newr = st.selectbox('Role', options=['admin','viewer'], key='newrole')
        if st.button('Create user'):
            conn = get_conn()
            cur = conn.cursor()
            cur.execute('INSERT INTO users (username,password,role) VALUES (?,?,?)', (newu,newp,newr))
            conn.commit()
            conn.close()
            st.success('User created.')