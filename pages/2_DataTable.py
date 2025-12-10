import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.title("Data Table")

df = st.session_state.get("uploaded_data")

if df is None:
    st.warning("Upload an Excel file in Settings.")
else:
    builder = GridOptionsBuilder.from_dataframe(df)
    builder.configure_default_column(editable=True)
    builder.configure_pagination(enabled=True)
    grid = AgGrid(df, gridOptions=builder.build(), update_mode=GridUpdateMode.MODEL_CHANGED)

    if st.button("Save Changes"):
        st.session_state["uploaded_data"] = pd.DataFrame(grid["data"])
        st.success("Changes saved.")
