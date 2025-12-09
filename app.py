
import streamlit as st
import sqlite3

st.set_page_config(page_title="Fleet Dashboard", layout="wide")

# --- LOGIN SYSTEM ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if (username=="admin" and password=="adminpass") or (username=="viewer" and password=="viewonly"):
            st.session_state.logged_in = True
            st.session_state.role = "admin" if username=="admin" else "viewer"
            st.experimental_rerun()
        else:
            st.error("Invalid login")

if not st.session_state.logged_in:
    login()
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("Navigation")
st.sidebar.page_link("pages/1_Overview.py", label="Overview")
st.sidebar.page_link("pages/2_DataTable.py", label="Data Table")
st.sidebar.page_link("pages/3_Settings.py", label="Settings (Admin Only)")

st.write("Use sidebar to navigate.")
