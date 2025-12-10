
import streamlit as st

st.set_page_config(page_title="Fleet Dashboard", layout="wide")

# Simple login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

def show_login():
    st.title("🔐 Fleet Dashboard Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == "admin" and p == "adminpass":
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.experimental_rerun()
        elif u == "viewer" and p == "viewonly":
            st.session_state.logged_in = True
            st.session_state.role = "viewer"
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    show_login()
    st.stop()

st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to:", ["Overview", "Data Table", "Settings"])

if choice == "Overview":
    st.experimental_set_query_params(page="overview")
    st.experimental_rerun()
elif choice == "Data Table":
    st.experimental_set_query_params(page="table")
    st.experimental_rerun()
elif choice == "Settings":
    st.experimental_set_query_params(page="settings")
    st.experimental_rerun()

st.write("Use the sidebar to navigate.")
