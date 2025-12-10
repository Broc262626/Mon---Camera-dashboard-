
import streamlit as st
import pandas as pd
import sqlite3

st.title("⚙️ Settings — Admin Only")

if st.session_state.get('role') != 'admin':
    st.error('Access denied. Admin only.')
    st.stop()

uploaded = st.file_uploader('Upload Excel (must have columns: Server, Parent fleet, Fleet number, Registration, Repair status, Comments, Date created, Priority)', type=['xlsx','xls','csv'])
if uploaded:
    try:
        if uploaded.name.lower().endswith('.csv'):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)
        # Convert datetimes to strings
        for col in df.select_dtypes(include=['datetime','datetime64[ns]']).columns:
            df[col] = df[col].astype(str)
        # map source columns to DB columns (if present)
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
        df_renamed = {}
        for src, dst in mapping.items():
            if src in df.columns:
                df_renamed[dst] = df[src]
            else:
                df_renamed[dst] = [''] * len(df)
        df_out = pd.DataFrame(df_renamed)
        conn = sqlite3.connect('fleet_data.db')
        df_out.to_sql('fleet', conn, if_exists='replace', index=False)
        conn.close()
        st.success('Imported to DB successfully.')
    except Exception as e:
        st.error(f'Import error: {e}')
