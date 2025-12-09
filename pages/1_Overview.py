import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ---------------------------------------
# DB Connection
# ---------------------------------------
DB_PATH = "fleet_data.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# ---------------------------------------
# NORMALIZE STATUS FUNCTION
# ---------------------------------------
def normalize_status(value):
    if not value:
        return "Unknown"
    v = str(value).strip().lower()

    if v in ["new", "new ", "fresh", "0"]:
        return "New"

    if "vetted" in v or "po-approved" in v or "po approved" in v:
        return "New - vetted"

    if "inspect" in v or "monitor" in v:
        return "inspected - monitoring"

    if "await" in v or "material" in v or "awaitingpo" in v or "awaiting po" in v:
        return "Awaiting material"

    if "offline" in v or "pending" in v or "vet" in v:
        return "Offline- pending vetting"

    return "Other"

# ---------------------------------------
# PAGE START
# ---------------------------------------
st.header("Overview")

conn = get_conn()
df = pd.read_sql_query("SELECT * FROM fleet", conn)
conn.close()

if df.empty:
    st.info("No data available. Upload Excel in Settings.")
    st.stop()

# Apply normalization
# Support either column name 'repairStatus' or variations stored in DB
if "repairStatus" in df.columns:
    df["repairStatus"] = df["repairStatus"].apply(normalize_status)
elif "Repair status" in df.columns:
    df["Repair status"] = df["Repair status"].apply(normalize_status)
    df = df.rename(columns={"Repair status":"repairStatus"})

# ---------------------------------------
# COUNT BY STATUS
# ---------------------------------------
status_order = [
    "New",
    "New - vetted",
    "inspected - monitoring",
    "Awaiting material",
    "Offline- pending vetting",
]

counts = df["repairStatus"].value_counts().reindex(status_order, fill_value=0)

# ---------------------------------------
# KPI CARDS
# ---------------------------------------
colors = {
    "New": "#ef4444",
    "New - vetted": "#f59e0b",
    "inspected - monitoring": "#facc15",
    "Awaiting material": "#60a5fa",
    "Offline- pending vetting": "#34d399",
}

cols = st.columns(5)
for i, status in enumerate(status_order):
    with cols[i]:
        st.markdown(
            f"""
            <div style='background:{colors[status]}; padding:20px; border-radius:10px; text-align:center; color:#081224;'>
                <h4 style='margin:0'>{status}</h4>
                <h2 style='margin:0'>{counts[status]}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------
# BAR CHART
# ---------------------------------------
chart_df = pd.DataFrame({"Status": status_order, "Count": counts.values})
fig = px.bar(
    chart_df,
    x="Status",
    y="Count",
    title="Camera Health Chart",
    color="Status",
    color_discrete_map=colors,
)
fig.update_layout(plot_bgcolor='#071123',paper_bgcolor='#071123',font_color='white',xaxis_title='',yaxis_title='')
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------
# QUICK TABLE (OVERVIEW STYLE)
# ---------------------------------------
st.subheader("Quick table (Overview style)")

# Build quick table columns flexibly, handling variant column names
cols_needed = []
for c in ["parentFleet","Parent fleet","parent fleet"]:
    if c in df.columns:
        cols_needed.append(c)
        break
for c in ["fleetNumber","Fleet number","fleet number"]:
    if c in df.columns:
        cols_needed.append(c)
        break
for c in ["repairStatus","Repair status"]:
    if c in df.columns:
        cols_needed.append(c)
        break
for c in ["comments","Comments"]:
    if c in df.columns:
        cols_needed.append(c)
        break
for c in ["priority","Priority"]:
    if c in df.columns:
        cols_needed.append(c)
        break

if len(cols_needed) < 5:
    # fallback: show available columns
    quick = df.head(10)
else:
    quick = df[cols_needed].head(10)
    quick.columns = ['Parent Fleet','Fleet number','Repair status','Comments','Priority']

st.dataframe(quick, use_container_width=True)