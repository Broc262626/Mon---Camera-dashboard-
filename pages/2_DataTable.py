
import streamlit as st
import sqlite3
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.title("📄 Data Table (Excel Style)")

conn = sqlite3.connect("fleet_data.db")
df = pd.read_sql_query("SELECT * FROM fleet", conn)

if df.empty:
    st.warning("No data found. Please upload data in Settings.")
    st.stop()

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True)
gb.configure_column("Priority", cellEditor="agSelectCellEditor", cellEditorParams={"values":[1,2,3]})
gb.configure_selection("single")
go = gb.build()

grid = AgGrid(
    df,
    gridOptions=go,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    fit_columns_on_grid_load=True
)

updated_df = grid["data"]

if st.button("Save Changes"):
    updated_df.to_sql("fleet", conn, if_exists="replace", index=False)
    st.success("Table updated successfully!")
