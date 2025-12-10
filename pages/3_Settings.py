
import streamlit as st
import pandas as pd
import sqlite3

st.title("⚙️ Settings — Admin Only")

if st.session_state.get('role') != 'admin':
    st.error("Access denied. Admin only.")
    st.stop()

uploaded = st.file_uploader('Upload Excel/CSV (columns: Server, Parent fleet, Fleet number, Registration, Repair status, Comments, Date created, Priority)', type=['xlsx','xls','csv'])
if uploaded:
    try:
        if uploaded.name.lower().endswith('.csv'):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)
        for col in df.select_dtypes(include=['datetime','datetime64[ns]']).columns:
            df[col] = df[col].astype(str)
        mapping = {
            'Server':'server',
            'Parent fleet':'parentFleet',
            'Fleet number':'fleetNumber',
            'Registration':'registration',
            'Repair status':'repairStatus',
            'Comments':'comments',
            'Date created':'dateCreated',
            'Priority':'priority'
        }
        out = {}
        for src, dst in mapping.items():
            if src in df.columns:
                out[dst] = df[src]
            else:
                out[dst] = [''] * len(df)
        df_out = pd.DataFrame(out)
        conn = sqlite3.connect('fleet_data.db')
        df_out.to_sql('fleet', conn, if_exists='replace', index=False)
        conn.close()
        st.success('Imported to DB successfully.')
    except Exception as e:
        st.error(f'Import error: {e}')
