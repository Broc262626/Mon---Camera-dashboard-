import streamlit as st
import pandas as pd
import sqlite3
import io
import plotly.express as px

DB_PATH = "fleet_data.db"
REQUIRED_COLUMNS = ["Server","Parent fleet","Fleet number","Registration","Repair status","Comments","Date created","Priority"]

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fleet (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server TEXT,
        parentFleet TEXT,
        fleetNumber TEXT,
        registration TEXT,
        repairStatus TEXT,
        comments TEXT,
        dateCreated TEXT,
        priority INTEGER
    )
    """)
    conn.commit()
    conn.close()

def df_from_db():
    conn = get_conn()
    try:
        df = pd.read_sql_query("SELECT * FROM fleet", conn)
    except Exception:
        df = pd.DataFrame(columns=['id','server','parentFleet','fleetNumber','registration','repairStatus','comments','dateCreated','priority'])
    conn.close()
    return df

def replace_db_from_df(df):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM fleet")
    conn.commit()
    for _, row in df.iterrows():
        cur.execute(
            "INSERT INTO fleet (server,parentFleet,fleetNumber,registration,repairStatus,comments,dateCreated,priority) VALUES (?,?,?,?,?,?,?,?)",
            (str(row.get("Server","")), str(row.get("Parent fleet","")), str(row.get("Fleet number","")), str(row.get("Registration","")),
             str(row.get("Repair status","")), str(row.get("Comments","")), str(row.get("Date created","")), int(row.get("Priority") if pd.notna(row.get("Priority")) and row.get("Priority")!='' else 0))
        )
    conn.commit()
    conn.close()

def update_row(rowid, data):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE fleet SET server=?, parentFleet=?, fleetNumber=?, registration=?, repairStatus=?, comments=?, dateCreated=?, priority=? WHERE id=?",
                (data.get("server",""), data.get("parentFleet",""), str(data.get("fleetNumber","")), data.get("registration",""),
                 data.get("repairStatus",""), data.get("comments",""), data.get("dateCreated",""), int(data.get("priority",0)), rowid))
    conn.commit()
    conn.close()

def delete_row(rowid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM fleet WHERE id=?", (rowid,))
    conn.commit()
    conn.close()

# init DB
init_db()

# Session state defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# Simple login page (Option A)
def login_page():
    st.title("Fleet Health Dashboard — Login")
    with st.form("login"):
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if user == "admin" and pwd == "adminpass":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.experimental_rerun()
            elif user == "viewer" and pwd == "viewonly":
                st.session_state.logged_in = True
                st.session_state.role = "viewer"
                st.experimental_rerun()
            else:
                st.error("Invalid credentials. Demo: admin/adminpass or viewer/viewonly")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# Top bar and navigation
st.set_page_config(page_title="Fleet Health Dashboard", layout="wide")
col1, col2 = st.columns([6,1])
with col1:
    st.markdown("## Fleet Health Dashboard")
with col2:
    st.markdown(f"**Role:** {st.session_state.role.capitalize()}")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.experimental_rerun()

page = st.sidebar.selectbox("Page", ["Overview","Data Table","Settings"])

# Admin upload
st.sidebar.markdown("### Upload (Admin only)")
if st.session_state.role == "admin":
    uploaded = st.sidebar.file_uploader("Upload Excel or CSV", type=["xlsx","xls","csv"])
    if uploaded is not None:
        try:
            if uploaded.name.lower().endswith(".csv"):
                df_up = pd.read_csv(uploaded)
            else:
                df_up = pd.read_excel(uploaded)
        except Exception as e:
            st.sidebar.error(f"Cannot read file: {e}")
            df_up = None
        if df_up is not None:
            missing = [c for c in REQUIRED_COLUMNS if c not in df_up.columns]
            if missing:
                st.sidebar.error(f"Missing columns: {missing}")
            else:
                st.sidebar.success("File looks good.")
                if st.sidebar.button("Replace database with uploaded file"):
                    df_clean = df_up[REQUIRED_COLUMNS].copy()
                    df_clean.fillna("", inplace=True)
                    replace_db_from_df(df_clean)
                    st.sidebar.success("Database replaced.")
else:
    st.sidebar.info("Login as admin to upload data.")

# Read DB
df = df_from_db()

# Filters (sidebar)
st.sidebar.markdown("---")
st.sidebar.header("Filters")
statuses = sorted(df['repairStatus'].dropna().unique().tolist()) if not df.empty else []
status_filter = st.sidebar.selectbox("Repair Status", options=["All"] + statuses)
priority_filter = st.sidebar.selectbox("Priority", options=["All","1","2","3"])
search = st.sidebar.text_input("Search (fleet, reg, comments)")

def apply_filters(df_local):
    d = df_local.copy()
    if status_filter != "All":
        d = d[d['repairStatus'] == status_filter]
    if priority_filter != "All":
        d = d[d['priority'].astype(str) == str(priority_filter)]
    if search:
        mask = d.apply(lambda r: search.lower() in ' '.join(map(str,[r.get('parentFleet',''), r.get('fleetNumber',''), r.get('registration',''), r.get('comments','')])).lower(), axis=1)
        d = d[mask]
    return d

# Overview page (dark)
if page == "Overview":
    st.markdown("""<style>body{background:#0f1720;color:#fff} .stApp{background:#0f1720}</style>""", unsafe_allow_html=True)
    st.header("Overview")
    order = ["New","New - vetted","inspected - monitoring","Awaiting material","Offline- pending vetting"]
    counts = {s: int(df[df['repairStatus']==s].shape[0]) if not df.empty else 0 for s in order}
    cols = st.columns(5)
    for c,s in zip(cols, order):
        c.markdown(f"""<div style='background:#111827;padding:18px;border-radius:8px;text-align:center;'><h4 style='color:#ddd'>{s}</h4><h2 style='color:#fff'>{counts[s]}</h2></div>""", unsafe_allow_html=True)
    st.markdown("---")
    chart_df = pd.DataFrame({'status': list(counts.keys()), 'count': list(counts.values())})
    fig = px.bar(chart_df, x='status', y='count', color='status', color_discrete_map={
        'New':'#ef4444','New - vetted':'#f59e0b','inspected - monitoring':'#facc15','Awaiting material':'#60a5fa','Offline- pending vetting':'#34d399'
    })
    fig.update_layout(plot_bgcolor='#071123',paper_bgcolor='#071123',font_color='white',xaxis_title='',yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('---')
    st.subheader('Quick table')
    quick = df[['parentFleet','fleetNumber','repairStatus','comments','priority']].copy()
    quick.columns = ['Parent Fleet','Fleet number','Repair status','Comments','Priority']
    quick = apply_filters(quick)
    st.table(
    quick.head(10)
    .style.set_table_styles([
        {'selector': 'th', 'props': [('color', 'white'), ('background-color', '#0b1220')]},
        {'selector': 'td', 'props': [('color', 'white'), ('background-color', '#071225')]}
    ])
)

# Data Table page (light)
if page == "Data Table":
    st.markdown("""<style>body{background:#ffffff;color:#111} .stApp{background:#ffffff}</style>""", unsafe_allow_html=True)
    st.header("Data Table")
    d = df.copy()
    d = apply_filters(d)
    # Pagination
    per_page = st.selectbox("Rows per page", [10,25,50], index=1)
    total = len(d)
    total_pages = max(1, (total + per_page -1)//per_page)
    page_num = st.number_input("Page number", min_value=1, value=1, max_value=total_pages)
    start = (page_num-1)*per_page
    end = start + per_page
    slice_df = d.iloc[start:end]
    st.write(f"Showing {total} results — page {page_num} of {total_pages}")
    # Export
    if st.button("Export current view to Excel"):
        to_export = d.copy()
        to_export.to_excel("export.xlsx", index=False)
        with open("export.xlsx","rb") as f:
            st.download_button(label="Download Excel", data=f, file_name="fleet_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    # Table rows with actions
    for _, row in slice_df.iterrows():
        c1,c2,c3,c4,c5,c6 = st.columns([2,1,1,2,1,1])
        c1.write(row.get('parentFleet',''))
        c2.write(row.get('fleetNumber',''))
        c3.write(row.get('registration',''))
        c4.write(row.get('repairStatus',''))
        c5.write(row.get('priority',''))
        with c6:
            if st.session_state.role == 'admin':
                if st.button(f"Edit_{int(row['id'])}", key=f"e_{int(row['id'])}"):
                    with st.form(f"form_{int(row['id'])}"):
                        server = st.text_input("Server", value=row.get('server',''))
                        parent = st.text_input("Parent Fleet", value=row.get('parentFleet',''))
                        fleetnum = st.text_input("Fleet Number", value=row.get('fleetNumber',''))
                        reg = st.text_input("Registration", value=row.get('registration',''))
                        status = st.selectbox("Repair Status", options=order, index=0)
                        comments = st.text_area("Comments", value=row.get('comments',''))
                        pr = st.selectbox("Priority", options=[1,2,3], index=(int(row.get('priority',1))-1 if row.get('priority') else 0))
                        if st.form_submit_button("Save"):
                            update_row(int(row['id']), {'server':server,'parentFleet':parent,'fleetNumber':fleetnum,'registration':reg,'repairStatus':status,'comments':comments,'dateCreated':row.get('dateCreated',''),'priority':pr})
                            st.success("Saved")
                            st.experimental_rerun()
                if st.button(f"Delete_{int(row['id'])}", key=f"d_{int(row['id'])}"):
                    delete_row(int(row['id']))
                    st.success("Deleted")
                    st.experimental_rerun()
            else:
                st.write("View only")

# Settings page
if page == "Settings":
    st.header("Settings")
    if st.session_state.role != 'admin':
        st.warning("Admin only.")
    else:
        if st.button("Export full DB to Excel"):
            df_all = df_from_db()
            df_all.to_excel("full_export.xlsx", index=False)
            with open("full_export.xlsx","rb") as f:
                st.download_button("Download full DB", data=f, file_name="fleet_full_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if st.button("Clear all data (DELETE) "):
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM fleet")
            conn.commit()
            conn.close()
            st.success("Cleared")