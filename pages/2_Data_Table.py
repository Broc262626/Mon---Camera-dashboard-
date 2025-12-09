import streamlit as st
import pandas as pd
import sqlite3

if not st.session_state.get('logged_in', False):
    st.warning('Please login from the main page first.')
    st.stop()

DB_PATH = 'fleet_data.db'
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def df_from_db():
    conn = get_conn()
    try:
        df = pd.read_sql_query('SELECT * FROM fleet', conn)
    except Exception:
        df = pd.DataFrame(columns=['id','server','parentFleet','fleetNumber','registration','repairStatus','comments','dateCreated','priority'])
    conn.close()
    return df

df = df_from_db()

# Clean columns
col_map = {}
for col in df.columns:
    if col.strip().lower() == 'status':
        col_map[col] = 'repairStatus'
    if col.strip().lower() == 'fleet number':
        col_map[col] = 'fleetNumber'
    if col.strip().lower() == 'date created':
        col_map[col] = 'dateCreated'
if col_map:
    df = df.rename(columns=col_map)

st.header('Data Table')
# Filters
status_options = ['All'] + sorted(df['repairStatus'].dropna().unique().tolist()) if not df.empty else ['All']
status = st.selectbox('Repair Status', options=status_options)
priority = st.selectbox('Priority', options=['All','1','2','3'])
search = st.text_input('Search')

# Apply filters
d = df.copy()
if status != 'All':
    d = d[d['repairStatus']==status]
if priority != 'All':
    d = d[d['priority'].astype(str)==str(priority)]
if search:
    d = d[d.apply(lambda r: search.lower() in ' '.join(map(str,[r.get('parentFleet',''), r.get('fleetNumber',''), r.get('registration',''), r.get('comments','')])).lower(), axis=1)]

# Pagination
per_page = st.selectbox('Rows per page', [10,25,50], index=1)
total = len(d)
total_pages = max(1, (total + per_page -1)//per_page)
page_num = st.number_input('Page number', min_value=1, value=1, max_value=total_pages)
start = (page_num-1)*per_page
end = start + per_page
slice_df = d.iloc[start:end]

st.write(f'Showing {total} results — page {page_num} of {total_pages}')

# Show table and actions
for _, row in slice_df.iterrows():
    c1,c2,c3,c4,c5,c6 = st.columns([2,1,1,2,1,1])
    c1.write(row.get('parentFleet',''))
    c2.write(row.get('fleetNumber',''))
    c3.write(row.get('registration',''))
    c4.write(row.get('repairStatus',''))
    c5.write(row.get('priority',''))
    with c6:
        if st.session_state.get('role') == 'admin':
            if st.button(f'Edit_{int(row["id"])}', key=f'e_{int(row["id"])}'):
                with st.form(f'form_{int(row["id"])}'):
                    server = st.text_input('Server', value=row.get('server',''))
                    parent = st.text_input('Parent Fleet', value=row.get('parentFleet',''))
                    fleetnum = st.text_input('Fleet Number', value=row.get('fleetNumber',''))
                    reg = st.text_input('Registration', value=row.get('registration',''))
                    status_val = st.selectbox('Repair Status', options=['New','New - vetted','inspected - monitoring','Awaiting material','Offline- pending vetting'])
                    comments = st.text_area('Comments', value=row.get('comments',''))
                    pr = st.selectbox('Priority', options=[1,2,3], index=(int(row.get('priority',1))-1 if row.get('priority') else 0))
                    submitted = st.form_submit_button('Save')
                    if submitted:
                        conn = get_conn()
                        cur = conn.cursor()
                        cur.execute("""UPDATE fleet SET server=?, parentFleet=?, fleetNumber=?, registration=?, repairStatus=?, comments=?, dateCreated=?, priority=? WHERE id=?""", (server,parent,fleetnum,reg,status_val,comments,row.get('dateCreated',''), int(pr), int(row['id'])))
                        conn.commit()
                        conn.close()
                        st.success('Saved')
                        st.experimental_rerun()
            if st.button(f'Delete_{int(row["id"])}', key=f'd_{int(row["id"])}'):
                conn = get_conn()
                cur = conn.cursor()
                cur.execute('DELETE FROM fleet WHERE id=?', (int(row['id']),))
                conn.commit()
                conn.close()
                st.success('Deleted')
                st.experimental_rerun()
        else:
            st.write('View only')

# Export
if st.button('Export current view to Excel'):
    to_export = d.copy()
    to_export.to_excel('export.xlsx', index=False)
    with open('export.xlsx','rb') as f:
        st.download_button('Download Excel', data=f, file_name='fleet_export.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
