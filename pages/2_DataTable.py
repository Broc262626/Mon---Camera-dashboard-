
import streamlit as st
import sqlite3
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from io import BytesIO

st.title("📘 Data Table — Excel-style editor")

conn = sqlite3.connect("fleet_data.db")
df = pd.read_sql_query("SELECT * FROM fleet", conn)
conn.close()

if df is None or df.empty:
    st.info("No data — upload via Settings.")
else:
    if 'id' not in df.columns:
        df = df.reset_index().rename(columns={'index':'id'})

    st.subheader("Import / Export / Save")
    c1, c2, c3 = st.columns([2,2,2])
    with c1:
        uploaded = st.file_uploader("Import Excel/CSV", type=['xlsx','xls','csv'], key='import')
        if uploaded:
            try:
                if uploaded.name.lower().endswith('.csv'):
                    new_df = pd.read_csv(uploaded)
                else:
                    new_df = pd.read_excel(uploaded)
                conn = sqlite3.connect('fleet_data.db')
                new_df.to_sql('fleet', conn, if_exists='replace', index=False)
                conn.close()
                st.success("Imported to DB. Reload page to view changes.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Import error: {e}")
    with c2:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇ Download CSV", csv, file_name='fleet_export.csv', mime='text/csv')
    with c3:
        towrite = BytesIO()
        with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='fleet')
            writer.save()
        towrite.seek(0)
        st.download_button("⬇ Download Excel", towrite.getvalue(), file_name='fleet_export.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    priority_js = JsCode("""
    function(params) {
        if (params.value == 1) return {'backgroundColor':'#ff4d4f','color':'black','fontWeight':'700','textAlign':'center'};
        if (params.value == 2) return {'backgroundColor':'#ffd24d','color':'black','fontWeight':'700','textAlign':'center'};
        if (params.value == 3) return {'backgroundColor':'#34d399','color':'black','fontWeight':'700','textAlign':'center'};
        return null;
    }
    """)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, filter=True, sortable=True, resizable=True)
    pcol = None
    if 'priority' in df.columns:
        pcol = 'priority'
    elif 'Priority' in df.columns:
        pcol = 'Priority'
    if pcol:
        gb.configure_column(pcol, cellEditor='agSelectCellEditor', cellEditorParams={'values':[1,2,3]}, cellStyle=priority_js)
    gb.configure_selection('single')
    go = gb.build()
    grid_response = AgGrid(df, gridOptions=go, update_mode=GridUpdateMode.VALUE_CHANGED, allow_unsafe_jscode=True, fit_columns_on_grid_load=True, theme='streamlit')
    updated = pd.DataFrame(grid_response['data'])

    st.markdown('---')
    colA, colB = st.columns(2)
    with colA:
        if st.button("💾 Save changes to DB"):
            try:
                conn = sqlite3.connect('fleet_data.db')
                updated.to_sql('fleet', conn, if_exists='replace', index=False)
                conn.close()
                st.success("Saved to DB. Reload to refresh.")
            except Exception as e:
                st.error(f"Save error: {e}")
    with colB:
        selected = grid_response.get('selected_rows', [])
        if st.button("🗑 Delete selected row"):
            if not selected:
                st.warning("Select a row first.")
            else:
                sel = selected[0]
                try:
                    conn = sqlite3.connect('fleet_data.db')
                    cur = conn.cursor()
                    if 'id' in sel:
                        cur.execute("DELETE FROM fleet WHERE id=?", (int(sel['id']),))
                        conn.commit()
                    else:
                        tmp = pd.DataFrame(grid_response['data'])
                        for col in tmp.columns:
                            tmp[col] = tmp[col].astype(str)
                        sel_str = {k:str(v) for k,v in sel.items()}
                        mask = ~(tmp.apply(lambda r: all(r[c]==sel_str.get(c,str(r[c])) for c in sel_str), axis=1))
                        newdf = tmp[mask]
                        newdf.to_sql('fleet', conn, if_exists='replace', index=False)
                    conn.close()
                    st.success("Deleted. Reloading...")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Delete error: {e}")
