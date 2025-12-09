import streamlit as st
import pandas as pd
import sqlite3

if not st.session_state.get('logged_in', False):
    st.warning('Please login from the main page first.')
    st.stop()

st.header('Settings')
if st.session_state.get('role') != 'admin':
    st.warning('Settings are admin-only.')
    st.stop()

DB_PATH = 'fleet_data.db'
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def df_from_db():
    conn = get_conn()
    try:
        df = pd.read_sql_query('SELECT * FROM fleet', conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

if st.button('Export full DB to Excel'):
    df_all = df_from_db()
    df_all.to_excel('full_export.xlsx', index=False)
    with open('full_export.xlsx','rb') as f:
        st.download_button('Download full DB', data=f, file_name='fleet_full_export.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if st.button('Clear all data (DELETE)'):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM fleet')
    conn.commit()
    conn.close()
    st.success('All data cleared.')