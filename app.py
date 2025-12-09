import streamlit as st

st.set_page_config(page_title="Fleet Dashboard", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if (u=="admin" and p=="adminpass") or (u=="viewer" and p=="viewonly"):
            st.session_state.logged_in = True
            st.session_state.role = "admin" if u=="admin" else "viewer"
            st.experimental_rerun()
        else:
            st.error("Invalid login")

if not st.session_state.logged_in:
    login()
    st.stop()

st.sidebar.title("Navigation")
st.sidebar.page_link("pages/1_Overview.py","Overview")
st.sidebar.page_link("pages/2_DataTable.py","Data Table")
st.sidebar.page_link("pages/3_Settings.py","Settings (Admin Only)")

st.write("Use the sidebar to navigate.")
