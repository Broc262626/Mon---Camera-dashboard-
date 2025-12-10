
import streamlit as st
import sqlite3
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from io import BytesIO

st.title("📘 Data Table — Excel Mode")

# DB load
conn = sqlite3.connect("fleet_data.db")
df = pd.read_sql_query("SELECT * FROM fleet", conn)
conn.close()

if df.empty:
    st.info("No data available. Upload Excel in Settings.")
    # allow import here too
else:
    # ensure id exists
    if 'id' not in df.columns:
        df.reset_index(inplace=True)
        df.rename(columns={'index':'id'}, inplace=True)

    # IMPORT / EXPORT UI
    st.subheader("Import / Export")
    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        uploaded = st.file_uploader("Import Excel/CSV", type=['xlsx','xls','csv'], key='import')
        if uploaded:
            try:
                if uploaded.name.lower().endswith('.csv'):
                    new_df = pd.read_csv(uploaded)
                else:
                    new_df = pd.read_excel(uploaded)
                # map columns if they match expected names
                # write to DB
                conn = sqlite3.connect("fleet_data.db")
                new_df.to_sql('fleet', conn, if_exists='replace', index=False)
                conn.close()
                st.success("Imported and saved to DB. Reload page to see changes.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Import error: {e}")

    with col2:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇ Download CSV", csv, file_name='fleet_export.csv', mime='text/csv')
    with col3:
        towrite = BytesIO()
        with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='fleet')
            writer.save()
        towrite.seek(0)
        st.download_button("⬇ Download Excel", towrite.getvalue(), file_name='fleet_export.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    st.markdown('---')

    # AG Grid setup
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, filter=True, sortable=True, resizable=True)
    # priority dropdown
    if 'priority' in df.columns or 'Priority' in df.columns:
        pcol = 'priority' if 'priority' in df.columns else 'Priority'
        gb.configure_column(pcol, cellEditor='agSelectCellEditor', cellEditorParams={'values':[1,2,3]})
        # color via JS
        js = JsCode("""function(params) {
            if (params.value == 1) return {'backgroundColor':'#ff4d4f','color':'black','fontWeight':'700'};
            if (params.value == 2) return {'backgroundColor':'#ffd24d','color':'black','fontWeight':'700'};
            if (params.value == 3) return {'backgroundColor':'#34d399','color':'black','fontWeight':'700'};
            return null;
        }""")
        gb.configure_column(pcol, cellStyle=js)

    gb.configure_grid_options(domLayout='normal')
    go = gb.build()

    grid_response = AgGrid(df, gridOptions=go, enable_enterprise_modules=False,
                          update_mode=GridUpdateMode.VALUE_CHANGED, allow_unsafe_jscode=True,
                          fit_columns_on_grid_load=True,theme='streamlit')

    updated = pd.DataFrame(grid_response['data'])

    st.write('---')
    colA, colB = st.columns(2)
    with colA:
        if st.button('💾 Save changes to DB'):
            try:
                conn = sqlite3.connect('fleet_data.db')
                updated.to_sql('fleet', conn, if_exists='replace', index=False)
                conn.close()
                st.success('Saved to DB. Reload page to view.')
            except Exception as e:
                st.error(f'Error saving: {e}')
    with colB:
        selected = grid_response.get('selected_rows', [])
        if st.button('🗑 Delete selected row'):
            if not selected:
                st.warning('Select a row first (single select).')
            else:
                sel = selected[0]
                # attempt to remove by id if present, else by matching row
                try:
                    conn = sqlite3.connect('fleet_data.db')
                    cur = conn.cursor()
                    if 'id' in sel:
                        cur.execute('DELETE FROM fleet WHERE id=?', (int(sel['id']),))
                        conn.commit()
                    else:
                        # fallback: build dataframe without selected row
                        updated_df = updated.copy()
                        for k,v in sel.items():
                            updated_df = updated_df[~(updated_df[k].astype(str)==str(v))]
                        updated_df.to_sql('fleet', conn, if_exists='replace', index=False)
                    conn.close()
                    st.success('Deleted. Reloading...')
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f'Delete error: {e}')
