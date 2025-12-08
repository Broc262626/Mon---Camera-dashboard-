
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Camera Repair Dashboard", layout="wide")

st.title("Camera Repair Dashboard")

# Session state table
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["ID","Name","Category","Value","Timestamp"])

# File upload
uploaded = st.file_uploader("Import Excel", type=["xlsx"])
if uploaded:
    st.session_state.df = pd.read_excel(uploaded)
    st.success("Data imported successfully")

df = st.session_state.df

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("New", len(df[df["Category"]=="New"]))
col2.metric("In Progress", len(df[df["Category"]=="In Progress"]))
col3.metric("Awaiting Parts", len(df[df["Category"]=="Awaiting Parts"]))
col4.metric("Repaired", len(df[df["Category"]=="Repaired"]))

st.subheader("Edit Table")
edited = st.data_editor(df, num_rows="dynamic")
st.session_state.df = edited

# Export
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.download_button("Download Excel", data=to_excel(st.session_state.df),
                   file_name="export.xlsx")

st.write("Data Table")
st.dataframe(st.session_state.df)
