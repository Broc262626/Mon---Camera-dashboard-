import streamlit as st

st.set_page_config(page_title='Fleet Dashboard', layout='wide')

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None

def do_login(username, password):
    if username == 'admin' and password == 'adminpass':
        st.session_state.logged_in = True
        st.session_state.role = 'admin'
        st.experimental_rerun()
    if username == 'viewer' and password == 'viewonly':
        st.session_state.logged_in = True
        st.session_state.role = 'viewer'
        st.experimental_rerun()
    st.error('Invalid credentials. Demo users: admin/adminpass, viewer/viewonly')

if not st.session_state.logged_in:
    st.title('Fleet Dashboard — Login')
    with st.form('login'):
        user = st.text_input('Username')
        pwd = st.text_input('Password', type='password')
        submitted = st.form_submit_button('Login')
        if submitted:
            do_login(user, pwd)
    st.stop()

# If logged in, show small header and logout
col1, col2 = st.columns([9,1])
with col1:
    st.markdown('### Fleet Health Dashboard')
with col2:
    if st.button('Logout'):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.experimental_rerun()

st.info('Use the sidebar (left) to navigate: Overview, Data Table, Settings (Settings is admin-only).')