import streamlit as st
from pathlib import Path
st.set_page_config(page_title="Camera Repair Dashboard", layout="wide")

CSS = '''/* Dark background and typography */
body {background-color:#0b0c0d;}
.reportview-container .main .block-container{padding-top:1rem;}
h1{font-size:48px;color:#e6eef8;text-align:center;margin-bottom:0.2rem;}
.kpi-card{border-radius:12px;padding:18px;color:#fff;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,0.6);}
.kpi-label{font-size:18px;opacity:0.9;}
.kpi-value{font-size:36px;font-weight:700;margin-top:6px;}
.alert-box{border-radius:10px;padding:14px;background:#5b2121;color:#fff;margin-top:18px;}
.table-card{border-radius:10px;padding:8px;background:rgba(255,255,255,0.03);}
''' 
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# auth
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None

def login_widget():
    st.sidebar.header("Sign in")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Sign in"):
        import sqlite3, pandas as pd
        conn = sqlite3.connect(Path(__file__).parent / 'data' / 'devices.db')
        users = pd.read_sql_query("SELECT * FROM users", conn)
        conn.close()
        match = users[(users['username']==username) & (users['password']==password)]
        if not match.empty:
            st.session_state.user = username
            st.session_state.role = match.iloc[0]['role']
            st.success("Signed in as %s" % username)
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials")

if st.session_state.user is None:
    login_widget()
    st.markdown("<h1>Camera Repair Dashboard</h1>", unsafe_allow_html=True)
    st.info("Sign in (demo): admin/adminpass or viewer/viewpass")
    st.stop()

# sidebar navigation
st.sidebar.write(f"Signed in: **{st.session_state.user}** ({st.session_state.role})")
page = st.sidebar.radio("Navigation", ["Overview","Records","Import","Admin","Logout"])
if page == "Logout":
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()

# dispatch
page_map = {
    "Overview":"pages/overview.py",
    "Records":"pages/records.py",
    "Import":"pages/import_page.py",
    "Admin":"pages/admin.py"
}
if page in page_map:
    with open(Path(__file__).parent / page_map[page], "r", encoding="utf-8") as f:
        code = compile(f.read(), page_map[page], "exec")
        exec(code, globals())
else:
    st.write("Select a page")
