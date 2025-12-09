
import streamlit as st
import pandas as pd
import sqlite3

st.header("Settings")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.stop()

if st.session_state.get("role") != "admin":
    st.warning("Settings are admin-only.")
    st.stop()

DB_PATH = "fleet_data.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def save_to_db(df):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM fleet")
    for _, r in df.iterrows():
        cur.execute(
            """INSERT INTO fleet 
            (server, parentFleet, fleetNumber, registration, repairStatus, comments, dateCreated, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                r.get("Server",""),
                r.get("Parent fleet",""),
                r.get("Fleet number",""),
                r.get("Registration",""),
                r.get("Repair status",""),
                r.get("Comments",""),
                r.get("Date created",""),
                int(r.get("Priority",0)) if str(r.get("Priority","")).isdigit() else 0
            )
        )
    conn.commit()
    conn.close()

st.subheader("Import Excel Data")

uploaded = st.file_uploader("Upload Excel file", type=["xlsx","xls"])

if uploaded:
    try:
        df = pd.read_excel(uploaded)

        required = [
            "Server","Parent fleet","Fleet number","Registration",
            "Repair status","Comments","Date created","Priority"
        ]

        missing = [c for c in required if c not in df.columns]
        if missing:
            st.error(f"Missing required columns: {missing}")
        else:
            save_to_db(df)
            st.success("Data imported successfully!")
            st.info("Go to Overview or Data Table to view your updated data.")
    except Exception as e:
        st.error(f"Error processing file: {e}")
