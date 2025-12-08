import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sqlite3

DB = Path(__file__).parent.parent / "data" / "devices.db"
conn = sqlite3.connect(DB)
df = pd.read_sql_query("SELECT * FROM devices", conn)
conn.close()

st.markdown("<h1>Camera Repair Dashboard</h1>", unsafe_allow_html=True)
st.write(f"Signed in as **{st.session_state.user}** ({st.session_state.role})")

PALETTE = {
    "New":"#2563eb",
    "In Progress":"#d97706",
    "Awaiting Parts":"#b45309",
    "Repaired":"#0f766e"
}

counts = df['status'].value_counts().to_dict()
display = ["New","In Progress","Awaiting Parts","Repaired"]
cols = st.columns(4, gap="large")
for i, s in enumerate(display):
    with cols[i]:
        cnt = counts.get(s,0)
        color = PALETTE.get(s, "#374151")
        st.markdown(f'<div class="kpi-card" style="background:{color}"><div class="kpi-label">{s}</div><div class="kpi-value">{cnt}</div></div>', unsafe_allow_html=True)

st.markdown("---")
left, right = st.columns([2,1])
with left:
    st.subheader("Status distribution")
    pie_df = pd.DataFrame({"status":list(counts.keys()), "count":[counts[k] for k in counts.keys()]})
    if not pie_df.empty:
        fig = px.pie(pie_df, names="status", values="count", color="status", color_discrete_map=PALETTE, hole=0.35)
        fig.update_traces(textinfo="percent+label", textfont_size=14)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data to show")
with right:
    st.subheader("Quick stats")
    st.metric("Total devices", df.shape[0])
    st.metric("Priority 1 devices", int((df['priority']=="1").sum()))

st.markdown("---")
st.subheader("Parent Fleet summary")
if not df.empty:
    fleet_summary = df.groupby("parent_fleet").agg(Total_Issues=("serial_number","count"), Open=("status", lambda x: (x!="Repaired").sum()), Completed=("status", lambda x: (x=="Repaired").sum()), Priority1=("priority", lambda x: (x=="1").sum())).reset_index()
    st.markdown('<div class="table-card">' + fleet_summary.to_html(index=False, classes="dataframe") + "</div>", unsafe_allow_html=True)
else:
    st.info("No fleet data")

p1_count = int((df['priority']=="1").sum())
if p1_count>0:
    st.markdown(f'<div class="alert-box">⚠️ <strong>{p1_count} devices with Priority 1</strong></div>', unsafe_allow_html=True)
