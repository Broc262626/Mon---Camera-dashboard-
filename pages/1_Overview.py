
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("📊 Overview Dashboard")

conn = sqlite3.connect("fleet_data.db")
df = pd.read_sql_query("SELECT * FROM fleet", conn)

if df.empty:
    st.warning("No data available. Please import via Settings page.")
    st.stop()

# Status count
status_counts = df['Repair Status'].value_counts()

st.subheader("Repair Status Summary")
st.write(status_counts)

# Plot
fig = px.bar(status_counts, title="Repair Status Distribution")
st.plotly_chart(fig, use_container_width=True)

# Quick table
st.subheader("Quick View")
st.dataframe(df[["Parent fleet","Fleet number","Repair Status","Comments","Priority"]], use_container_width=True)
