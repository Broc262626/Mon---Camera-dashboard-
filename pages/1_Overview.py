import streamlit as st
import pandas as pd

st.title("Overview")

df = st.session_state.get("uploaded_data")

if df is None:
    st.warning("Upload an Excel file in Settings.")
else:
    st.subheader("Repair Status Summary")
    st.write(df['Repair status'].value_counts())
