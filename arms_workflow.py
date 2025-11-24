import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="ARMS Workflow Manager",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

ANALYSTS = [
    "Nisarg Thakker",
    "Jen Shears",
    "Komal Khamar",
    "Janet Yanatos",
    "Rondrea Carroll",
    "Devanshi Joshi",
    "Divyesh Fofandi",
    "Parth Chelani",
    "Prerna Kesrani",
    "Ayushi Chandel",
    "Ankit Rawat",
]

# =========================
# STYLING
# =========================

st.markdown("""
<style>
    .main { background-color: #0e1a2b; }
    .top-header {
        background: linear-gradient(135deg,#0f2d4e,#1a4b8c);
        padding: 1.2rem 2rem;
        color: white;
        border-bottom: 3px solid #00d4ff;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: #1e2a3b;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border: 1px solid #2a3a50;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .metric-card h3 {
        font-size: 0.8rem;
        text-transform: uppercase;
        color: #b3d9ff;
        margin-bottom: 0.3rem;
    }
    .metric-card p {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-header">
  <h1 style="margin:0; font-size:2.0rem;">🚀 ARMS Workflow Manager</h1>
  <p style="margin:0.2rem 0 0;">Task Management • Analyst Performance • Enterprise Analytics</p>
</div>
""", unsafe_allow_html=True)

# =========================
# SESSION INIT
# =========================

if "data" not in st.session_state:
    st.session_state.data = {}

if "task_assignments" not in st.session_state:
    # {task_key: {"analyst": ..., "status": "In Progress"/"Paused"/"Completed"}}
    st.session_state.task_assignments = {}

if "active_task" not in st.session_state:
    st.session_state.active_task = None  # (sheet_name, index)


# =========================
# SIDEBAR – USER & DATA LOAD
# =========================

with st.sidebar:
    st.subheader("👤 Logged-in User")

    current_analyst = st.selectbox(
        "Select Analyst",
        options=["(Stakeholder View)"] + ANALYSTS,
        index=0
    )

    st.markdown("---")
    st.subheader("📂 Data Source")

    master_file = st.file_uploader(
        "Upload ARMS Master Excel",
        type=["xlsx", "xls"],
        help="File containing Pending, UCC, Judgments, Chapter11, Chapter7, Trade Tapes, Analyst Data, Data Lake, Workflows sheets."
    )

    if master_file:
        try:
            xls = pd.ExcelFile(master_file)
            # Map sheet names to our logical names (adjust to exact names in your file)
            sheet_map = {
                "Pending": "pending",
                "UCC": "ucc",
                "Judgements": "judgments",
                "Chapter11": "ch11",
                "Chapte11": "ch11",
                "Chapter7": "ch7",
                "Trade Tapes": "trade_tapes",
                "Analyst Data": "analyst_data",
                "Data Lake": "data_lake",
                "Workflows": "workflows",
            }

            loaded_sheets = []
            for sheet_name, key in sheet_map.items():
                if sheet_name in xls.sheet_names:
                    df = pd.read_excel(master_file, sheet_name=sheet_name)
                    st.session_state.data[key] = df
                    loaded_sheets.append(sheet_name)

            st.success(f"Loaded sheets: {', '.join(loaded_sheets)}")

        except Exception as e:
            st.error(f"Error reading Excel: {e}")

    else:
        st.info("Upload the master Excel file to start.")

# Helper to get DF safely
def get_df(key):
    return st.session_state.data.get(key, pd.DataFrame())

# =========================
# UTILITY: NEXT TASK SELECTION
# =========================

def get_next_pending_task(pending_df, analyst_name):
    """
    Simple 'Get Next Task' logic:
    - Sort by Import Date then File Date (if present)
    - Choose first row that is not already assigned
    """
    if pending_df.empty:
        return None

    df = pending_df.copy()
    # Try to parse dates if columns exist
    for col in ["Import Date", "File Date", "Date IND Format"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    sort_cols = [c for c in ["Import Date", "File Date", "Date IND Format"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols)

    for idx, row in df.iterrows():
        task_key = f"Pending::{idx}"
        assign_info = st.session_state.task_assignments.get(task_key)
        if assign_info is None or assign_info.get("status") != "Completed":
            # assign to this analyst
            st.session_state.task_assignments[task_key] = {
                "analyst": analyst_name,
                "status": "In Progress",
                "assigned_at": dt.datetime.now(),
            }
            st.session_state.active_task = ("pending", idx)
            return task_key, row

    return None

# =========================
# TAB 1 – TASK MANAGEMENT
# =========================

def tab_task_management():
    st.subheader("⏱️ Task Management")

    pending_df = get_df("pending")
    if pending_df.empty:
        st.warning("Pending sheet not loaded.")
        return

    # KPI row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_items = pending_df["Total Pending"].sum() if "Total Pending" in pending_df.columns else len(pending_df)
        st.markdown('<div class="metric-card"><h3>Total Pending Items</h3>'
                    f'<p>{int(total_items):,}</p></div>', unsafe_allow_html=True)

    with col2:
        reviewed = pending_df["Reviewed"].sum() if "Reviewed" in pending_df.columns else 0
        st.markdown('<div class="metric-card"><h3>Reviewed</h3>'
                    f'<p>{int(reviewed):,}</p></div>', unsafe_allow_html=True)

    with col3:
        assigned_count = sum(1 for k, v in st.session_state.task_assignments.items() if v["status"] != "Completed")
        st.markdown('<div class="metric-card"><h3>In-Progress Tasks</h3>'
                    f'<p>{assigned_count:,}</p></div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card"><h3>Active Analysts</h3>'
                    f'<p>{len(set(v["analyst"] for v in st.session_state.task_assignments.values()))}</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Get Next Task – only for analysts, not stakeholder view
    if current_analyst != "(Stakeholder View)":
        if st.button("🎯 Get Next Task", type="primary"):
            res = get_next_pending_task(pending_df, current_analyst)
            if res is None:
                st.success("No more unassigned tasks in Pending.")
            else:
                st.success("Task assigned. Scroll to 'Active Task' section below.")

    # Active Task panel
    st.markdown("### 📌 Active Task")

    if st.session_state.active_task is None:
        st.info("No active task selected. Click **Get Next Task** to start.")
    else:
        sheet_key, row_idx = st.session_state.active_task
        df = get_df(sheet_key)
        if row_idx not in df.index:
            st.warning("Active task no longer exists in data.")
        else:
            row = df.loc[row_idx]
            task_key = f"{sheet_key}::{row_idx}"
            assign_info = st.session_state.task_assignments.get(task_key, {})

            st.write(f"**Workflow:** Pending | **Row ID:** {row_idx}")
            if "Subscriber" in df.columns:
                st.write(f"**Subscriber:** {row['Subscriber']}")
            if "Import Date" in df.columns:
                st.write(f"**Import Date:** {row['Import Date']}")

            # Show all columns in an expander
            with st.expander("View full task details"):
                st.dataframe(row.to_frame().T, use_container_width=True)

            # Actions row
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("⏸️ Pause Task"):
                    if assign_info:
                        assign_info["status"] = "Paused"
                    st.success("Task paused.")

            with c2:
                if st.button("✅ Complete Task"):
                    if assign_info:
                        assign_info["status"] = "Completed"
                        assign_info["completed_at"] = dt.datetime.now()
                    st.session_state.active_task = None
                    st.success("Task marked as completed.")

            with c3:
                uploaded_files = st.file_uploader(
                    "Attach emails / documents",
                    type=None,                  # ✅ allows .eml and anything else
                    accept_multiple_files=True,
                    key=f"upload_{task_key}"
                )
                if uploaded_files:
                    st.info(f"{len(uploaded_files)} file(s) attached to this task (not persisted yet).")

    st.markdown("---")

    # Who is working on what?
    st.markdown("### 👀 Current Assignments")

    if st.session_state.task_assignments:
        rows = []
        for tkey, info in st.session_state.task_assignments.items():
            sheet_name, idx = tkey.split("::")
            rows.append({
                "Workflow": sheet_name,
                "Row ID": idx,
                "Analyst": info["analyst"],
                "Status": info["status"],
                "Assigned At": info.get("assigned_at"),
                "Completed At": info.get("completed_at"),
            })
        assign_df = pd.DataFrame(rows)
        if current_analyst != "(Stakeholder View)":
            assign_df = assign_df[assign_df["Analyst"] == current_analyst]
        st.dataframe(assign_df, use_container_width=True)
    else:
        st.info("No tasks assigned yet.")

# =========================
# TAB 2 – ANALYST PERFORMANCE
# =========================

def tab_analyst_performance():
    st.subheader("👥 Analyst Performance")

    analyst_df = get_df("analyst_data")
    data_lake_df = get_df("data_lake")

    if analyst_df.empty and data_lake_df.empty:
        st.warning("Analyst Data / Data Lake sheets not loaded.")
        return

    # Basic clean-up
    if "Date" in analyst_df.columns:
        analyst_df["Date"] = pd.to_datetime(analyst_df["Date"], errors="coerce")

    # Filter by analyst
    if current_analyst != "(Stakeholder View)":
        analyst_filtered = analyst_df[analyst_df["Team Member"] == current_analyst] \
            if "Team Member" in analyst_df.columns else analyst_df
        dl_filtered = data_lake_df[data_lake_df["team_member"] == current_analyst] \
            if "team_member" in data_lake_df.columns else data_lake_df
    else:
        analyst_filtered = analyst_df
        dl_filtered = data_lake_df

    col1, col2, col3 = st.columns(3)
    with col1:
        if "Achieved Qty" in analyst_filtered.columns:
            achieved = analyst_filtered["Achieved Qty"].sum()
            st.markdown('<div class="metric-card"><h3>Total Units Achieved</h3>'
                        f'<p>{int(achieved):,}</p></div>', unsafe_allow_html=True)
    with col2:
        if "Target Qty" in analyst_filtered.columns:
            target = analyst_filtered["Target Qty"].sum()
            st.markdown('<div class="metric-card"><h3>Total Target</h3>'
                        f'<p>{int(target):,}</p></div>', unsafe_allow_html=True)
    with col3:
        if not analyst_filtered.empty and {"Achieved Qty", "Target Qty"}.issubset(analyst_filtered.columns):
            pct = (analyst_filtered["Achieved Qty"].sum() /
                   max(1, analyst_filtered["Target Qty"].sum())) * 100
            st.markdown('<div class="metric-card"><h3>Target Achievement %</h3>'
                        f'<p>{pct:,.1f}%</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    if not analyst_filtered.empty:
        st.markdown("#### Daily Performance (Analyst Data)")
        st.dataframe(analyst_filtered, use_container_width=True)

    if not dl_filtered.empty:
        st.markdown("#### Monthly Work Units (Data Lake)")
        pivot = dl_filtered[["month_year", "total_work_units", "pending_actions"]].copy()
        st.dataframe(pivot, use_container_width=True)

# =========================
# TAB 3 – ADVANCED ANALYTICS (STAKEHOLDERS)
# =========================

def tab_advanced_analytics():
    st.subheader("📈 Advanced Analytics – Stakeholder View")

    pending_df = get_df("pending")
    workflows_df = get_df("workflows")
    data_lake_df = get_df("data_lake")

    if pending_df.empty and workflows_df.empty and data_lake_df.empty:
        st.warning("Load Pending / Workflows / Data Lake sheets for this tab.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        if not pending_df.empty:
            total_pending = pending_df["Total Pending"].sum() if "Total Pending" in pending_df.columns else len(pending_df)
            st.markdown('<div class="metric-card"><h3>Pending Items</h3>'
                        f'<p>{int(total_pending):,}</p></div>', unsafe_allow_html=True)
    with col2:
        if not data_lake_df.empty and "total_work_units" in data_lake_df.columns:
            twu = data_lake_df["total_work_units"].sum()
            st.markdown('<div class="metric-card"><h3>Total Work Units</h3>'
                        f'<p>{int(twu):,}</p></div>', unsafe_allow_html=True)
    with col3:
        if not workflows_df.empty and "Workflow Name" in workflows_df.columns:
            workflows_count = workflows_df["Workflow Name"].nunique()
            st.markdown('<div class="metric-card"><h3>Active Workflows</h3>'
                        f'<p>{workflows_count}</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    if not workflows_df.empty:
        st.markdown("#### Workflow SLA Overview")
        st.dataframe(
            workflows_df[[
                "Workflow Name", "Workflow Type", "Target Metric",
                "Measurement Unit", "Monthly Target", "Priority", "SLA Hours",
                "Quality Required?"
            ]],
            use_container_width=True
        )

    if not data_lake_df.empty:
        st.markdown("#### Volume by Analyst (from Data Lake)")
        if {"team_member", "total_work_units"}.issubset(data_lake_df.columns):
            agg = data_lake_df.groupby("team_member")["total_work_units"].sum().reset_index()
            st.dataframe(agg.sort_values("total_work_units", ascending=False), use_container_width=True)

# =========================
# TAB 4 – WORKFLOW & SLA SETUP
# =========================

def tab_workflow_config():
    st.subheader("⚙️ Workflow & SLA Setup")

    workflows_df = get_df("workflows").copy()

    if workflows_df.empty:
        st.info("No Workflows sheet loaded. You can start creating one here and then export it.")
        workflows_df = pd.DataFrame(columns=[
            "No", "Workflow Name", "Workflow Type", "Target Metric",
            "Measurement Unit", "Monthly Target", "Priority", "SLA Hours",
            "Quality Required?"
        ])

    st.markdown("### Existing Workflows")
    st.dataframe(workflows_df, use_container_width=True)

    st.markdown("---")
    st.markdown("### ➕ Create / Edit Workflow")

    with st.form("new_workflow_form"):
        wf_name = st.text_input("Workflow Name")
        wf_type = st.selectbox("Workflow Type", ["Volume", "Target", "Quality"])
        target_metric = st.text_input("Target Metric", value="Completion %")
        measurement_unit = st.text_input("Measurement Unit", value="Items")
        monthly_target = st.number_input("Monthly Target", min_value=0, value=100)
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], index=2)
        sla_hours = st.number_input("SLA Hours", min_value=1, value=72)
        quality_required = st.checkbox("Quality Required?", value=True)

        submitted = st.form_submit_button("Save Workflow")
        if submitted and wf_name:
            new_row = {
                "No": len(workflows_df) + 1,
                "Workflow Name": wf_name,
                "Workflow Type": wf_type,
                "Target Metric": target_metric,
                "Measurement Unit": measurement_unit,
                "Monthly Target": monthly_target,
                "Priority": priority,
                "SLA Hours": sla_hours,
                "Quality Required?": "Yes" if quality_required else "No",
            }
            workflows_df = workflows_df._append(new_row, ignore_index=True)
            st.session_state.data["workflows"] = workflows_df
            st.success("Workflow saved in session. You can export it as Excel from below.")

    st.markdown("### 💾 Export Workflows")
    if not workflows_df.empty:
        csv = workflows_df.to_csv(index=False)
        st.download_button(
            "Download Workflows as CSV",
            data=csv,
            file_name="ARMS_Workflows_Config.csv",
            mime="text/csv"
        )

# =========================
# MAIN
# =========================

tab1, tab2, tab3, tab4 = st.tabs([
    "⏱️ Task Management",
    "👥 Analyst Performance",
    "📈 Advanced Analytics",
    "⚙️ Workflow & SLA Setup",
])

with tab1:
    tab_task_management()
with tab2:
    tab_analyst_performance()
with tab3:
    tab_advanced_analytics()
with tab4:
    tab_workflow_config()
