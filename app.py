# Fixed app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Cameras & Tasks Repair Dashboard", page_icon="assets/logo.png", layout="wide")

DATA_PATH = Path("data")
DATA_PATH.mkdir(exist_ok=True)
CSV_FILE = DATA_PATH / "devices.csv"

STATUS_OPTIONS = ["New","In Progress","Awaiting Parts","Completed","Closed"]

def load_data():
    if CSV_FILE.exists():
        return pd.read_csv(CSV_FILE, dtype=str).fillna("")
    return pd.DataFrame(columns=["server","status","date_created","comments"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    st.title("Login")
    pwd = st.text_input("Password", type="password")
    if st.button("Login") and pwd:
        st.session_state.logged_in = True
        st.experimental_rerun()

def main_dashboard():
    st.sidebar.title("Menu")
    page = st.sidebar.radio("Go to",["Overview","Records","Import","About"])
    df = load_data()

    if page=="Overview":
        st.header("Overview")
        if not df.empty and "status" in df:
            counts = df["status"].value_counts().reset_index()
            counts.columns = ["status","count"]
            st.bar_chart(counts.set_index("status"))
        else:
            st.info("No data.")

    if page=="Records":
        st.header("Records")
        if df.empty:
            st.info("Empty.")
        else:
            edited = st.data_editor(df)
            if st.button("Save"):
                save_data(edited)
                st.success("Saved.")

    if page=="Import":
        st.header("Import CSV")
        up = st.file_uploader("Upload CSV", type="csv")
        if up:
            new = pd.read_csv(up, dtype=str)
            save_data(new)
            st.success("Imported.")

    if page=="About":
        st.write("Fixed dashboard.")

if not st.session_state.get("logged_in", False):
    login()
else:
    main_dashboard()
