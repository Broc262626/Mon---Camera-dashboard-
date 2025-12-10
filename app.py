import streamlit as st

st.set_page_config(page_title="Fleet Dashboard", layout="wide")

st.sidebar.page_link("pages/1_Overview.py", label="Overview")
st.sidebar.page_link("pages/2_DataTable.py", label="Data Table")
st.sidebar.page_link("pages/3_Settings.py", label="Settings")

st.title("Fleet Dashboard")
st.write("Use the sidebar to navigate between pages.")
