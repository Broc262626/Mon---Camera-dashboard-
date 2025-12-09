import streamlit as st
import pandas as pd
import sqlite3

st.header("Data Table")

# Ensure user is logged in
if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.stop()

DB_PATH = "fleet_data.db"
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# SAME NORMALIZER TO MATCH OVERVIEW + SETTINGS
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

# LOAD DATA
conn = get_conn()
df = pd.read_sql_query("SELECT * FROM fleet", conn)
conn.close()

if df.empty:
    st.info("No data available. Upload Excel in Settings.")
    st.stop()

# Normalize status
if "repairStatus" in df.columns:
    df["repairStatus"] = df["repairStatus"].apply(normalize_status)
elif "Repair status" in df.columns:
    df["Repair status"] = df["Repair status"].apply(normalize_status)
    df = df.rename(columns={"Repair status":"repairStatus"})

# FILTER BAR -------------------------------------------------
st.subheader("Filters")

col1, col2, col3 = st.columns(3)

with col1:
    status_filter = st.selectbox(
        "Repair Status",
        ["All", "New", "New - vetted", "inspected - monitoring", "Awaiting material", "Offline- pending vetting"],
    )

with col2:
    priority_filter = st.selectbox("Priority", ["All", 1, 2, 3])

with col3:
    search = st.text_input("Search (fleet, registration, comments)")

# APPLY FILTERS ----------------------------------------------
filtered = df.copy()

if status_filter != "All":
    filtered = filtered[filtered["repairStatus"] == status_filter]

if priority_filter != "All":
    filtered = filtered[filtered["priority"] == int(priority_filter)]

if search:
    q = search.lower()
    filtered = filtered[filtered.apply(lambda row: q in str(row).lower(), axis=1)]

# STYLE TABLE -------------------------------------------------
priority_colors = {
    1: "#ef4444",   # Red
    2: "#facc15",   # Yellow
    3: "#22c55e",   # Green
}

# Create a styled version
styled = filtered[["parentFleet", "fleetNumber", "registration", "repairStatus", "comments", "priority", "dateCreated"]].copy()

# Highlight priority colors
styled["Priority Color"] = styled["priority"].map(priority_colors)

# SHOW TABLE --------------------------------------------------

# Fullscreen toggle
fullscreen = st.checkbox("Fullscreen Table View")

def render_table(height):
    st.dataframe(
        styled.style.apply(
            lambda row: [
                f"background-color: {row['Priority Color']}" if col == "priority" else ""
                for col in row.index
            ],
            axis=1,
        ),
        use_container_width=True,
        height=height,
    )

if fullscreen:
    st.markdown("## 📺 Fullscreen Table")
    render_table(900)
else:
    render_table(400)

# Floating action menu (3-dot) per row using selectbox-style popup
st.markdown("### Actions")
for idx, row in styled.reset_index().iterrows():
    cols = st.columns([2,1,1,1,1,1,0.5])
    cols[0].write(row.get("parentFleet",""))
    cols[1].write(row.get("fleetNumber",""))
    cols[2].write(row.get("registration",""))
    cols[3].write(row.get("repairStatus",""))
    cols[4].write(row.get("priority",""))
    with cols[6]:
        choice = st.selectbox("", ["⋮","Edit","Delete","View Details"], key=f"menu_{idx}")
        if choice == "Edit":
            # simple edit form popped inline
            with st.form(f"edit_form_{idx}"):
                server = st.text_input("Server", value=row.get("server",""))
                parent = st.text_input("Parent Fleet", value=row.get("parentFleet",""))
                fleetnum = st.text_input("Fleet Number", value=row.get("fleetNumber",""))
                reg = st.text_input("Registration", value=row.get("registration",""))
                status_val = st.selectbox("Repair Status", options=["New","New - vetted","inspected - monitoring","Awaiting material","Offline- pending vetting"])
                comments = st.text_area("Comments", value=row.get("comments",""))
                pr = st.selectbox("Priority", options=[1,2,3], index=(int(row.get("priority",1))-1 if row.get("priority") else 0))
                submitted = st.form_submit_button("Save")
                if submitted:
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute("""UPDATE fleet SET server=?, parentFleet=?, fleetNumber=?, registration=?, repairStatus=?, comments=?, dateCreated=?, priority=? WHERE id=?""", (server,parent,fleetnum,reg,status_val,comments,row.get("dateCreated",""), int(pr), int(row.get("id",0))))
                    conn.commit()
                    conn.close()
                    st.success("Saved")
                    st.experimental_rerun()
        elif choice == "Delete":
            if st.button(f"confirm_delete_{idx}", key=f"del_{idx}"):
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("DELETE FROM fleet WHERE id=?", (int(row.get("id",0)),))
                conn.commit()
                conn.close()
                st.success("Deleted")
                st.experimental_rerun()
        elif choice == "View Details":
            st.write(row.to_dict())
