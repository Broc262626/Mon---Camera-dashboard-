
import streamlit as st

st.set_page_config(page_title="Fleet Dashboard", layout="wide")

# -------------------------
# LOGIN SYSTEM
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if (username == "admin" and password == "adminpass"):
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.experimental_rerun()

        elif (username == "viewer" and password == "viewonly"):
            st.session_state.logged_in = True
            st.session_state.role = "viewer"
            st.experimental_rerun()

        else:
            st.error("Invalid username or password")

# Show login screen if not logged_in
if not st.session_state.logged_in:
    login()
    st.stop()

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to:",
    ["Overview", "Data Table", "Settings"]
)

# Redirect to pages using switch_page()
if page == "Overview":
    st.switch_page("pages/1_Overview.py")

elif page == "Data Table":
    st.switch_page("pages/2_DataTable.py")

elif page == "Settings":
    if st.session_state.role != "admin":
        st.error("Access denied. Admin only.")
    else:
        st.switch_page("pages/3_Settings.py")

st.write("Use the sidebar to navigate.")
