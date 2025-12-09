import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("📊 Overview Dashboard")

conn = sqlite3.connect("fleet_data.db")
df = pd.read_sql_query("SELECT * FROM fleet", conn)

if df.empty:
    st.warning("No data available. Please import data via the Settings page.")
    st.stop()

if "Repair status" not in df.columns:
    st.error("❌ 'Repair status' column missing in database.")
    st.stop()

st.subheader("🛠 Repair Status Summary")
status_counts = df["Repair status"].value_counts()
st.write(status_counts)

fig = px.bar(
    status_counts,
    title="Repair Status Distribution",
    labels={"index": "Status", "value": "Count"},
    color=status_counts.index
)
st.plotly_chart(fig, use_container_width=True)

quick_cols = ["Parent fleet","Fleet number","Repair status","Comments","Priority"]
existing = [c for c in quick_cols if c in df.columns]
st.subheader("📋 Quick View")
st.dataframe(df[existing], use_container_width=True)
