import streamlit as st
from pathlib import Path
import sqlite3, pandas as pd
st.set_page_config(page_title="Camera Repair Dashboard", layout="wide")

CSS = "body {background-color:#0b0c0d;} h1{color:#e6eef8;text-align:center;} .kpi-card{border-radius:12px;padding:18px;color:#fff;text-align:center;} .alert-box{border-radius:10px;padding:14px;background:#5b2121;color:#fff;margin-top:18px;} .table-card{border-radius:10px;padding:8px;background:rgba(255,255,255,0.03);}"
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

DB = Path(__file__).parent / 'data' / 'devices.db'

if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None

def login_widget():
    st.sidebar.header("Sign in")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Sign in"):
        conn = sqlite3.connect(DB)
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
    st.info("Sign in (demo): admin/adminpass or viewer/Viewonly")
    st.stop()

st.sidebar.write(f"Signed in: **{st.session_state.user}** ({st.session_state.role})")
page = st.sidebar.radio("Navigation", ["Overview","Records","Import","Admin","Logout"])
if page == "Logout":
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()

page_map = {'Overview':'pages/overview.py','Records':'pages/records.py','Import':'pages/import_page.py','Admin':'pages/admin.py'}
if page in page_map:
    with open(Path(__file__).parent / page_map[page], 'r', encoding='utf-8') as f:
        code = compile(f.read(), page_map[page], 'exec')
        exec(code, globals())
else:
    st.write('Select a page from the sidebar')
