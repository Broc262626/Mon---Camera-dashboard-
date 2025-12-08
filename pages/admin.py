import streamlit as st, pandas as pd
from pathlib import Path
DB = Path(__file__).parent.parent / 'data' / 'devices.db'
if st.session_state.role != 'admin':
    st.info('Admin area - admins only')
    st.stop()
st.header('Admin - User management')
conn = __import__('sqlite3').connect(DB)
users = pd.read_sql_query('SELECT username, role FROM users', conn)
conn.close()
st.table(users)
st.subheader('Create new user')
nu = st.text_input('Username', key='nu')
npw = st.text_input('Password', type='password', key='np')
nr = st.selectbox('Role', ['admin','viewer'], key='nr')
if st.button('Create user'):
    conn = __import__('sqlite3').connect(DB)
    cur = conn.cursor()
    cur.execute('INSERT INTO users (username,password,role) VALUES (?,?,?)', (nu,npw,nr))
    conn.commit()
    conn.close()
    st.success('User created')