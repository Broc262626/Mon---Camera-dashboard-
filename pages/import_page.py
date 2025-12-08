import streamlit as st
import pandas as pd
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "devices.db"

st.header("Import - Upload Excel/CSV (Admin only)")
if st.session_state.role != "admin":
    st.info("Only admins can import data.")
    st.stop()

uploaded = st.file_uploader("Upload .xlsx or .csv", type=["xlsx","csv"])
if uploaded:
    try:
        if uploaded.name.endswith(".xlsx"):
            raw = pd.read_excel(uploaded, engine="openpyxl", dtype=str)
        else:
            raw = pd.read_csv(uploaded, dtype=str)
        st.write("Preview of uploaded file (first 10 rows):")
        st.dataframe(raw.head(10))
        # normalize
        def normalize_columns(df):
            new_cols = {}
            for c in df.columns:
                new_cols[c] = c.strip()
            df = df.rename(columns=new_cols)
            mapping = {'Server':'server', 'Parent fleet':'parent_fleet', 'Fleet number':'fleet_number', 'Fleet number ':'fleet_number', 'Registration':'registration', 'Status':'status', 'Comments':'comments', 'Date created':'date_created', 'Date created ':'date_created', 'Priority':'priority', 'serial_number':'serial_number'}
            df_cols = {}
            for c in df.columns:
                key = c.strip()
                if key in mapping:
                    df_cols[c] = mapping[key]
                else:
                    df_cols[c] = c.strip().lower().replace(" ","_")
            df = df.rename(columns=df_cols)
            req = ['server','parent_fleet','fleet_number','registration','status','comments','date_created','priority','serial_number']
            for r in req:
                if r not in df.columns:
                    df[r] = ''
            try:
                df['date_created'] = pd.to_datetime(df['date_created']).dt.date.astype(str)
            except Exception:
                df['date_created'] = df['date_created'].astype(str)
            df['priority'] = df['priority'].astype(str)
            for c in df.columns:
                if df[c].dtype == object:
                    df[c] = df[c].astype(str).str.strip()
            return df[req]
        cleaned = normalize_columns(raw)
        st.write("Normalized preview:")
        st.dataframe(cleaned.head(10))
        action = st.radio("Action", ["Append to DB", "Replace DB"])
        if st.button("Confirm import"):
            if action.startswith("Append"):
                conn = __import__("sqlite3").connect(DB)
                old = pd.read_sql_query("SELECT * FROM devices", conn)
                conn.close()
                merged = pd.concat([old, cleaned], ignore_index=True)
                merged.to_sql("devices", __import__("sqlite3").connect(DB), if_exists="replace", index=False)
                st.success("Appended to DB")
            else:
                cleaned.to_sql("devices", __import__("sqlite3").connect(DB), if_exists="replace", index=False)
                st.success("Replaced DB with uploaded data")
    except Exception as e:
        st.error(f"Import failed: {e}")
