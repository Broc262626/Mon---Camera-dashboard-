import streamlit as st
import pandas as pd
import sqlite3

st.title("⚙️ Settings — Admin Only")

if st.session_state.get("role") != "admin":
    st.error("Access denied. Admin only.")
    st.stop()

uploaded = st.file_uploader("Upload Excel", type=["xlsx"])

if uploaded:
    df = pd.read_excel(uploaded)

    for col in df.select_dtypes(include=["datetime","datetime64[ns]"]).columns:
        df[col] = df[col].astype(str)

    conn = sqlite3.connect("fleet_data.db")
    df.to_sql("fleet", conn, if_exists="replace", index=False)
    st.success("Data imported successfully!")
