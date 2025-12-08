
import streamlit as st

# Simple auth demo
USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
    "viewer": {"password": "viewerpass", "role": "viewer"},
}

def login_page():
    st.title("Sign In")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign in"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.authenticated = True
            st.session_state.role = USERS[username]["role"]
            st.rerun()
        else:
            st.error("Invalid credentials")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_page()
else:
    st.title("Camera Dashboard Overview")
    st.write(f"Logged in as **{st.session_state.role}**")
    st.write("Placeholder dashboard — full version will load here.")
