import streamlit as st
import sqlite3
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

st.title("📄 Data Table — Excel Style (Editable + Delete)")

conn = sqlite3.connect("fleet_data.db")
df = pd.read_sql_query("SELECT * FROM fleet", conn)

if df.empty:
    st.warning("No data found. Please import data in Settings.")
    st.stop()

if "row_id" not in df.columns:
    df["row_id"] = df.index

priority_color_js = JsCode("""function(params) {
    if (params.value == 1) return {'color': 'white','backgroundColor': 'red'};
    if (params.value == 2) return {'color': 'black','backgroundColor': 'yellow'};
    if (params.value == 3) return {'color': 'black','backgroundColor': 'lightgreen'};
    return null;
} """)

action_menu_js = JsCode("""function(params){
    return `<div style='cursor:pointer;font-size:18px;text-align:center;'>⋮</div>`;
}""")

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, filter=True, resizable=True, sortable=True)
gb.configure_column("Priority", cellEditor="agSelectCellEditor",
                    cellEditorParams={"values":[1,2,3]}, cellStyle=priority_color_js)
gb.configure_column("Actions", headerName="⋮", editable=False, filter=False,
                    width=80, cellRenderer=action_menu_js)

gb.configure_selection("single")
go = gb.build()

grid = AgGrid(df, gridOptions=go, enable_enterprise_modules=False,
              update_mode=GridUpdateMode.MODEL_CHANGED,
              allow_unsafe_jscode=True, fit_columns_on_grid_load=True)

updated_df = grid["data"]

if st.button("💾 Save All Changes"):
    updated_df.drop(columns=["Actions"], errors="ignore", inplace=True)
    updated_df.to_sql("fleet", conn, if_exists="replace", index=False)
    st.success("Changes saved successfully!")

if st.button("🗑 Delete Selected Row"):
    selected = grid.get("selected_rows", [])
    if len(selected)==0:
        st.warning("Select a row to delete.")
    else:
        row_id = selected[0]["row_id"]
        new_df = updated_df[updated_df["row_id"] != row_id]
        new_df.to_sql("fleet", conn, if_exists="replace", index=False)
        st.success("Row deleted!")
        st.experimental_rerun()
