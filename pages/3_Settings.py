import streamlit as st
import pandas as pd

st.title("Settings")

file = st.file_uploader("Upload Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    st.session_state["uploaded_data"] = df
    st.success("Upload successful!")
    st.write(df.head())
