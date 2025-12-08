import streamlit as st, pandas as pd
from pathlib import Path
import sqlite3
DB = Path(__file__).parent.parent / 'data' / 'devices.db'
conn = sqlite3.connect(DB)
df = pd.read_sql_query('SELECT * FROM devices', conn)
conn.close()
st.header('Records - Search & Filter')
c1,c2,c3,c4 = st.columns([2,2,2,1])
fleet_q = c1.text_input('Parent fleet contains')
server_q = c2.text_input('Server contains')
status_q = c3.multiselect('Status', options=sorted(df['status'].unique().tolist()), default=sorted(df['status'].unique().tolist()))
priority_q = c4.selectbox('Priority', options=['All','1','2','3',''], index=0)
filtered = df.copy()
if fleet_q:
    filtered = filtered[filtered['parent_fleet'].str.contains(fleet_q, case=False, na=False)]
if server_q:
    filtered = filtered[filtered['server'].str.contains(server_q, case=False, na=False)]
if status_q:
    filtered = filtered[filtered['status'].isin(status_q)]
if priority_q != 'All':
    filtered = filtered[filtered['priority']==priority_q]
search = st.text_input('Global search (fleet, server, registration, serial)')
if search:
    mask = (filtered['parent_fleet'].str.contains(search, case=False, na=False)) | (filtered['server'].str.contains(search, case=False, na=False)) | (filtered['registration'].str.contains(search, case=False, na=False)) | (filtered['serial_number'].str.contains(search, case=False, na=False))
    filtered = filtered[mask]
st.write(f'**{len(filtered)} results**')
per_page = st.selectbox('Per page', [5,10,20,50], index=1)
total = len(filtered)
max_page = max(1, (total-1)//per_page + 1)
page_num = st.number_input('Page', min_value=1, max_value=max_page, value=1, step=1)
start = (page_num-1)*per_page
page_df = filtered.iloc[start:start+per_page].reset_index(drop=True)
st.dataframe(page_df, use_container_width=True)
if st.session_state.role == 'admin':
    st.markdown('---')
    st.subheader('Admin actions')
    edited = st.data_editor(page_df, num_rows='dynamic')
    if st.button('Save edits to DB'):
        db = pd.read_sql_query('SELECT * FROM devices', __import__('sqlite3').connect(DB))
        for _, row in edited.iterrows():
            sn = row.get('serial_number')
            if sn and sn in db['serial_number'].values:
                db.loc[db['serial_number']==sn, :] = row.values
            else:
                db = pd.concat([db, pd.DataFrame([row])], ignore_index=True)
        db.to_sql('devices', __import__('sqlite3').connect(DB), if_exists='replace', index=False)
        st.success('Saved edits to DB')
    st.markdown('---')
    st.subheader('Delete selected rows')
    to_delete = []
    for idx, r in page_df.iterrows():
        key = f'del_{start+idx}'
        if st.checkbox(f"{r['parent_fleet']} | {r['registration']} | {r['serial_number']}", key=key):
            to_delete.append(r['serial_number'])
    if to_delete:
        if st.button('Delete selected rows'):
            with st.modal('Confirm deletion'):
                st.write(f"You are about to delete {len(to_delete)} rows. This action cannot be undone.")
                if st.button('Confirm delete'):
                    db = pd.read_sql_query('SELECT * FROM devices', __import__('sqlite3').connect(DB))
                    db = db[~db['serial_number'].isin(to_delete)]
                    db.to_sql('devices', __import__('sqlite3').connect(DB), if_exists='replace', index=False)
                    st.success(f"Deleted {len(to_delete)} rows")
else:
    st.info('View-only users cannot edit or delete')
