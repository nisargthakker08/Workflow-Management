import streamlit as st
import pandas as pd
import numpy as np
import io
import time
from datetime import datetime, date

from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime

# =========================
# PAGE CONFIG & CONSTANTS
# =========================

st.set_page_config(
    page_title="ARMS Workflow Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

TEAM_MEMBERS = [
    "Jen Shears",
    "Rondrea Carroll",
    "Devanshi Joshi",
    "Komal Khamar",
    "Divyesh Fofandi",
    "Parth Chelani",
    "Prerna Kesrani",
    "Nisarg Thakker",
    "Janet Yanatos",
]

ADMIN_USERS = [
    "Nisarg Thakker",
    "Jen Shears",
    "Komal Khamar",
    "Janet Yanatos",
]

# Display name -> internal workflow key
WORKFLOW_KEYS = {
    "Pending Trades": "Pending Trade Workflow",
    "Placements": "Placements Processing",
    "UCC Filings": "UCC Filings",
    "Judgments": "Judgments Processing",
    "Chapter 11": "Chapter 11 Bankruptcy",
    "Chapter 7": "Chapter 7 Bankruptcy",
    "Credit Files": "Credit Files Analysis",
    "Data Import": "Data Import Monitoring",
    "Subscriber Management": "Subscriber Management",
    "Quality Assurance": "Quality Assurance",
    "Trades Tape Imports": "Trades Tape Imports",
    "Trade References": "Trade References",
    "Credit File Audits": "Credit File Audits",
}

# Internal workflow key -> display name
WORKFLOW_LABELS = {v: k for k, v in WORKFLOW_KEYS.items()}

SHEET_NAMES = {
    "trade_pending": "Trade Pending's",
    "ucc": "UCC",
    "judgments": "Judgements",
    "chapter11": "Chapte11",
    "chapter7": "Chapter7",
    "trade_tapes": "Trade Tapes",
    "analyst": "Analyst Data",
    "data_lake": "Data Lake",
    "workflows": "Workflows",
}

# =========================
# CUSTOM CSS
# =========================

st.markdown(
    """
<style>
    body {
        background-color: #f5f7fb;
    }
    .main-header {
        font-size: 2.6rem;
        color: #005a9e;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    .section-header {
        color: #005a9e;
        border-bottom: 2px solid #d0d7e5;
        padding-bottom: 0.4rem;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        font-weight: 600;
    }
    .workflow-card {
        background-color: #ffffff;
        border: 1px solid #d0d7e5;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .task-active {
        border-left: 4px solid #2e8540;
    }
    .task-paused {
        border-left: 4px solid #f0ad4e;
    }
    .task-completed {
        border-left: 4px solid #6c757d;
    }
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# SESSION STATE INIT
# =========================

def init_df(key):
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame()

for key in [
    "trade_pending_df",
    "ucc_df",
    "judgments_df",
    "chapter11_df",
    "chapter7_df",
    "trade_tapes_df",
    "analyst_df",
    "data_lake_df",
    "workflows_df",
]:
    init_df(key)

if "active_tasks" not in st.session_state:
    st.session_state.active_tasks = {}
if "task_history" not in st.session_state:
    st.session_state.task_history = []
if "show_new_task" not in st.session_state:
    st.session_state.show_new_task = False

if "filter_team" not in st.session_state:
    st.session_state.filter_team = []
if "filter_workflow" not in st.session_state:
    st.session_state.filter_workflow = []
if "filter_start" not in st.session_state:
    st.session_state.filter_start = None
if "filter_end" not in st.session_state:
    st.session_state.filter_end = None

if "current_user" not in st.session_state:
    st.session_state.current_user = "Viewer"
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =========================
# HEADER
# =========================

st.markdown(
    '<div class="main-header">ARMS Workflow Management System</div>',
    unsafe_allow_html=True,
)

# =========================
# HELPERS
# =========================

def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except Exception:
                pass
    return df


def load_workbook(file) -> None:
    try:
        xls = pd.ExcelFile(file)

        def read_if_exists(name_key, target_key):
            expected = SHEET_NAMES[name_key]
            actual = None
            for s in xls.sheet_names:
                sl = s.lower().replace(" ", "")
                if sl == expected.lower().replace(" ", ""):
                    actual = s
                    break
            if actual is None:
                return
            df = pd.read_excel(xls, sheet_name=actual)
            df.columns = [c.strip() for c in df.columns]
            df = parse_dates(df)
            st.session_state[target_key] = df

        read_if_exists("trade_pending", "trade_pending_df")
        read_if_exists("ucc", "ucc_df")
        read_if_exists("judgments", "judgments_df")
        read_if_exists("chapter11", "chapter11_df")
        read_if_exists("chapter7", "chapter7_df")
        read_if_exists("trade_tapes", "trade_tapes_df")
        read_if_exists("analyst", "analyst_df")
        read_if_exists("data_lake", "data_lake_df")
        read_if_exists("workflows", "workflows_df")

    except Exception as e:
        st.sidebar.error(f"Error reading workbook: {e}")


def filtered_analyst_df() -> pd.DataFrame:
    df = st.session_state.analyst_df
    if df.empty:
        return df

    df = df.copy()
    date_col = None
    for c in df.columns:
        if c.lower() == "date" or "date" in c.lower():
            date_col = c
            break

    teams = st.session_state.filter_team
    if teams and "Team Member" in df.columns:
        df = df[df["Team Member"].astype(str).isin(teams)]

    wfs = st.session_state.filter_workflow
    if wfs and "Workflow" in df.columns:
        df = df[df["Workflow"].astype(str).isin(wfs)]

    if date_col and st.session_state.filter_start and st.session_state.filter_end:
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            mask = (df[date_col] >= st.session_state.filter_start) & (
                df[date_col] <= st.session_state.filter_end
            )
            df = df[mask]
        except Exception:
            pass

    return df


def sum_pending_column(df: pd.DataFrame) -> int:
    """Try to find a 'pending' column and sum it."""
    if df.empty:
        return 0
    cols = [c for c in df.columns if "pending" in c.lower()]
    if not cols:
        return int(len(df))
    # pick first pending-like column, coerce numeric
    col = cols[0]
    vals = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return int(vals.sum())


def get_workflow_pending_count(workflow_key: str) -> int:
    """Map each workflow to appropriate sheet/column and return pending count."""
    if workflow_key == "Pending Trade Workflow":
        return sum_pending_column(st.session_state.trade_pending_df)

    if workflow_key == "UCC Filings":
        return int(len(st.session_state.ucc_df)) if not st.session_state.ucc_df.empty else 0

    if workflow_key == "Judgments Processing":
        return int(len(st.session_state.judgments_df)) if not st.session_state.judgments_df.empty else 0

    if workflow_key == "Chapter 11 Bankruptcy":
        return int(len(st.session_state.chapter11_df)) if not st.session_state.chapter11_df.empty else 0

    if workflow_key == "Chapter 7 Bankruptcy":
        return int(len(st.session_state.chapter7_df)) if not st.session_state.chapter7_df.empty else 0

    dl = st.session_state.data_lake_df
    if dl.empty:
        return 0

    col_map = {
        "Placements Processing": "placements_actions",
        "Credit Files Analysis": "credit_files_actions",
        "Data Import Monitoring": "trades_tape_actions",
        "Subscriber Management": "pending_actions",
        "Quality Assurance": "tnt_actions",
        "Trades Tape Imports": "trades_tape_actions",
        "Trade References": "trade_references_actions",
        "Credit File Audits": "tnt_actions",
    }

    col = col_map.get(workflow_key)
    if col and col in dl.columns:
        vals = pd.to_numeric(dl[col], errors="coerce").fillna(0)
        return int(vals.sum())
    return 0


def get_active_analysts_for_workflow(workflow_key: str) -> int:
    df = st.session_state.analyst_df
    if df.empty:
        return 0
    if "Workflow" not in df.columns or "Team Member" not in df.columns:
        return 0
    label = WORKFLOW_LABELS.get(workflow_key, workflow_key)
    mask = df["Workflow"].astype(str).str.contains(label, case=False, na=False)
    return int(df.loc[mask, "Team Member"].nunique())


# =========================
# SIDEBAR (LOGIN + NAV)
# =========================

with st.sidebar:
    st.header("User & Access")

    user_choice = st.selectbox(
        "I am:",
        ["Viewer"] + ADMIN_USERS,
        index=0,
    )
    st.session_state.current_user = user_choice
    st.session_state.is_admin = user_choice in ADMIN_USERS

    if st.session_state.is_admin:
        st.success(f"Admin access: {user_choice}")
    elif user_choice == "Viewer":
        st.info("Viewer mode: dashboards & analytics only.")
    else:
        st.info(f"Limited access for {user_choice}")

    st.markdown("---")
    st.header("ARMS Navigation")

    # ----- Data Import -----
    st.subheader("📁 Data Import (full workbook)")
    wb_file = st.file_uploader(
        "Upload Excel workbook (.xlsx / .xls) with all ARMS sheets:",
        type=["xlsx", "xls"],
        help="Workbook should contain: Trade Pending's, UCC, Judgements, Chapte11, Chapter7, Trade Tapes, Analyst Data, Data Lake, Workflows",
    )

    if wb_file is not None:
        load_workbook(wb_file)
        st.success("Workbook loaded and cleaned. Sheets attached.")

    # ----- Workflow selection -----
    st.markdown("---")
    st.subheader("Workflow Management")
    selected_workflow = st.selectbox(
        "Select Workflow:",
        list(WORKFLOW_LABELS.keys()),
        format_func=lambda x: WORKFLOW_LABELS.get(x, x),
    )

    # ----- Task controls -----
    st.markdown("---")
    st.subheader("Task Controls")
    if st.session_state.is_admin:
        if st.button("🎯 Start New Task", use_container_width=True):
            st.session_state.show_new_task = True
            st.experimental_rerun()
    else:
        st.caption("Only admins can create tasks.")

    # ----- Global filters (Analyst Data) -----
    st.markdown("---")
    st.subheader("Global Filters (Analyst Data)")

    adf = st.session_state.analyst_df
    if not adf.empty and "Team Member" in adf.columns and "Workflow" in adf.columns:
        date_col = None
        for c in adf.columns:
            if c.lower() == "date" or "date" in c.lower():
                date_col = c
                break

        teams = sorted(adf["Team Member"].dropna().astype(str).unique().tolist())
        workflows = sorted(adf["Workflow"].dropna().astype(str).unique().tolist())

        st.session_state.filter_team = st.multiselect(
            "Team Member",
            teams,
            default=teams,
        )
        st.session_state.filter_workflow = st.multiselect(
            "Workflow",
            workflows,
            default=workflows,
        )

        if date_col:
            adf2 = adf.copy()
            adf2[date_col] = pd.to_datetime(adf2[date_col], errors="coerce")
            min_d = adf2[date_col].min()
            max_d = adf2[date_col].max()
            if pd.notna(min_d) and pd.notna(max_d):
                start_default = min_d.date()
                end_default = max_d.date()
                start_date, end_date = st.date_input(
                    "Date range",
                    [start_default, end_default],
                )
                if isinstance(start_date, date) and isinstance(end_date, date):
                    st.session_state.filter_start = datetime.combine(
                        start_date, datetime.min.time()
                    )
                    st.session_state.filter_end = datetime.combine(
                        end_date, datetime.max.time()
                    )
    else:
        st.caption("Upload workbook with 'Analyst Data' to enable filters.")

# =========================
# TABS
# =========================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📊 Dashboard",
        "📋 Pending Workflow",
        "📧 Email Import",
        "⏱️ Task Management",
        "📈 Analytics",
        "⚙️ Workflow Setup",
    ]
)

# =========================
# TAB 1 – DASHBOARD
# =========================

with tab1:
    st.markdown(
        '<div class="section-header">ARMS Workflow Dashboard</div>',
        unsafe_allow_html=True,
    )

    pending_count = get_workflow_pending_count(selected_workflow)
    active_analysts = get_active_analysts_for_workflow(selected_workflow)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Pending Items", f"{pending_count:,}")
    with c2:
        st.metric("Active Analysts", active_analysts)
    with c3:
        st.metric("Avg Processing Time", "N/A")
    with c4:
        st.metric("SLA Compliance", "N/A")

    st.subheader("Workflow Distribution (Pending Items)")

    rows = []
    for display, wf_key in WORKFLOW_KEYS.items():
        rows.append({"Workflow": display, "Pending": get_workflow_pending_count(wf_key)})
    dist_df = pd.DataFrame(rows).set_index("Workflow")
    st.bar_chart(dist_df["Pending"])

# =========================
# TAB 2 – PENDING WORKFLOW
# =========================

with tab2:
    st.markdown(
        f'<div class="section-header">📋 {WORKFLOW_LABELS.get(selected_workflow, selected_workflow)} – Detail</div>',
        unsafe_allow_html=True,
    )

    label = WORKFLOW_LABELS.get(selected_workflow, selected_workflow)

    if label == "Pending Trades":
        df = st.session_state.trade_pending_df
        if df.empty:
            st.info("Upload workbook with 'Trade Pending's' sheet to see pending trades.")
        else:
            st.metric("Total Pending (sum of pending columns)", sum_pending_column(df))
            st.dataframe(df, use_container_width=True)

    elif label == "UCC Filings":
        df = st.session_state.ucc_df
        if df.empty:
            st.info("Upload workbook with 'UCC' sheet.")
        else:
            st.metric("Total UCC rows", len(df))
            st.dataframe(df, use_container_width=True)

    elif label == "Judgments":
        df = st.session_state.judgments_df
        if df.empty:
            st.info("Upload workbook with 'Judgements' sheet.")
        else:
            st.metric("Total Judgment rows", len(df))
            st.dataframe(df, use_container_width=True)

    elif label == "Chapter 11":
        df = st.session_state.chapter11_df
        if df.empty:
            st.info("Upload workbook with 'Chapte11' sheet.")
        else:
            st.metric("Total Chapter 11 cases", len(df))
            st.dataframe(df, use_container_width=True)

    elif label == "Chapter 7":
        df = st.session_state.chapter7_df
        if df.empty:
            st.info("Upload workbook with 'Chapter7' sheet.")
        else:
            st.metric("Total Chapter 7 cases", len(df))
            st.dataframe(df, use_container_width=True)

    else:
        st.info(
            "This workflow does not have a dedicated pending sheet. Its metrics are derived from the Data Lake."
        )
        dl = st.session_state.data_lake_df
        if not dl.empty:
            st.dataframe(dl, use_container_width=True)

# =========================
# TAB 3 – EMAIL IMPORT
# =========================

with tab3:
    st.markdown(
        '<div class="section-header">📧 Email Work Import & Task Creation</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.is_admin:
        st.info("Only admin users can import emails and create tasks.")
    else:
        st.write(
            "Upload `.eml` files or Excel/CSV sheets containing work requests, "
            "then convert them into tasks managed in the Task Management tab."
        )

        email_files = st.file_uploader(
            "Upload .eml / .xlsx / .xls / .csv:",
            type=["eml", "xlsx", "xls", "csv"],
            accept_multiple_files=True,
            key="email_upload",
        )

        email_data = []

        if email_files:
            for email_file in email_files:
                name = email_file.name.lower()
                try:
                    # .eml
                    if name.endswith(".eml"):
                        raw_bytes = email_file.read()
                        msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)

                        subject = msg["subject"] or "No subject"
                        requestor = msg["from"] or "Unknown"

                        try:
                            received_dt = (
                                parsedate_to_datetime(msg["date"])
                                if msg["date"]
                                else datetime.now()
                            )
                        except Exception:
                            received_dt = datetime.now()

                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                ctype = part.get_content_type()
                                disp = str(part.get("Content-Disposition"))
                                if ctype == "text/plain" and "attachment" not in disp:
                                    try:
                                        body += part.get_content()
                                    except Exception:
                                        pass
                        else:
                            try:
                                body = msg.get_content()
                            except Exception:
                                body = ""

                        attachments = []
                        for att in msg.iter_attachments():
                            fn = att.get_filename()
                            if fn:
                                attachments.append(fn)

                        email_data.append(
                            {
                                "email_file": email_file.name,
                                "work_item_id": f"EMAIL_{len(email_data)+1:04d}",
                                "subject": subject,
                                "requestor": requestor,
                                "received_date": received_dt,
                                "priority": "Medium",
                                "estimated_effort_minutes": 30,
                                "body_preview": body[:500],
                                "attachments": ", ".join(attachments),
                                "assigned_to": "Unassigned",
                                "status": "New",
                            }
                        )

                    # CSV / Excel
                    elif name.endswith(".csv"):
                        df_sheet = pd.read_csv(email_file)
                        df_sheet.columns = [c.strip() for c in df_sheet.columns]
                        for _, row in df_sheet.iterrows():
                            email_data.append(
                                {
                                    "email_file": email_file.name,
                                    "work_item_id": f"EMAIL_{len(email_data)+1:04d}",
                                    "subject": row.get("subject", "N/A"),
                                    "requestor": row.get("from", "Unknown"),
                                    "received_date": row.get("date", datetime.now()),
                                    "priority": row.get("priority", "Medium"),
                                    "estimated_effort_minutes": row.get(
                                        "estimated_effort", 30
                                    ),
                                    "body_preview": str(row.get("body", ""))[:500],
                                    "attachments": str(row.get("attachments", "")),
                                    "assigned_to": "Unassigned",
                                    "status": "New",
                                }
                            )
                    else:
                        df_sheet = pd.read_excel(email_file)
                        df_sheet.columns = [c.strip() for c in df_sheet.columns]
                        for _, row in df_sheet.iterrows():
                            email_data.append(
                                {
                                    "email_file": email_file.name,
                                    "work_item_id": f"EMAIL_{len(email_data)+1:04d}",
                                    "subject": row.get("subject", "N/A"),
                                    "requestor": row.get("from", "Unknown"),
                                    "received_date": row.get("date", datetime.now()),
                                    "priority": row.get("priority", "Medium"),
                                    "estimated_effort_minutes": row.get(
                                        "estimated_effort", 30
                                    ),
                                    "body_preview": str(row.get("body", ""))[:500],
                                    "attachments": str(row.get("attachments", "")),
                                    "assigned_to": "Unassigned",
                                    "status": "New",
                                }
                            )

                except Exception as e:
                    st.error(f"Error processing {email_file.name}: {e}")

        if email_files and not email_data:
            st.warning("Files were uploaded but no work items could be extracted.")

        if email_data:
            email_df = pd.DataFrame(email_data)
            st.subheader("Extracted Work Items")
            st.dataframe(email_df, use_container_width=True)

            st.subheader("Create Tasks from Work Items")

            c1, c2 = st.columns(2)
            with c1:
                selected_items = st.multiselect(
                    "Select work items:",
                    options=email_df["work_item_id"].tolist(),
                )
            with c2:
                assigned_analyst = st.selectbox("Assign to Analyst:", TEAM_MEMBERS)
                wf_choice = st.selectbox(
                    "Workflow:",
                    list(WORKFLOW_LABELS.keys()),
                    format_func=lambda x: WORKFLOW_LABELS.get(x, x),
                )

                if st.button("Create Tasks", type="primary"):
                    created = 0
                    for item_id in selected_items:
                        row = email_df[email_df["work_item_id"] == item_id].iloc[0]
                        task_id = f"TASK_{len(st.session_state.active_tasks) + 1:04d}"

                        st.session_state.active_tasks[task_id] = {
                            "task_name": f"Email: {row['subject']}",
                            "workflow": wf_choice,
                            "assigned_analyst": assigned_analyst,
                            "description": f"From: {row['requestor']} - {row['subject']}\n\n{row.get('body_preview', '')}",
                            "estimated_duration": row["estimated_effort_minutes"],
                            "priority": row["priority"],
                            "start_time": datetime.now(),
                            "status": "Active",
                            "paused_time": None,
                            "total_paused_duration": 0,
                            "source": "Email Import",
                        }
                        created += 1

                    st.success(
                        f"✅ {created} task(s) created and assigned to {assigned_analyst}"
                    )
                    st.experimental_rerun()
        else:
            if not email_files:
                st.info("Upload .eml or Excel/CSV to extract work items.")

# =========================
# TAB 4 – TASK MANAGEMENT
# =========================

with tab4:
    st.markdown(
        '<div class="section-header">⏱️ Task Time Tracking & Management</div>',
        unsafe_allow_html=True,
    )

    st.write("All tasks from manual creation and email imports are consolidated here.")

    if not st.session_state.is_admin:
        st.info("Viewer mode: you can see tasks but cannot create or modify them.")

    # New task form (admins only)
    if st.session_state.show_new_task and st.session_state.is_admin:
        with st.form("new_task_form"):
            st.subheader("Create New Task")

            c1, c2 = st.columns(2)
            with c1:
                task_name = st.text_input("Task Name:", placeholder="Enter task name")
                task_workflow = st.selectbox(
                    "Workflow:",
                    list(WORKFLOW_LABELS.keys()),
                    format_func=lambda x: WORKFLOW_LABELS.get(x, x),
                )
                assigned_analyst = st.selectbox("Assign to Analyst:", TEAM_MEMBERS)
            with c2:
                task_description = st.text_area(
                    "Task Description:", placeholder="Describe the task..."
                )
                estimated_duration = st.number_input(
                    "Estimated Duration (minutes):", min_value=5, value=30
                )
                priority = st.selectbox(
                    "Priority:", ["Low", "Medium", "High", "Critical"]
                )

            cc1, cc2 = st.columns(2)
            with cc1:
                submitted = st.form_submit_button("🎯 Start Task")
            with cc2:
                cancel = st.form_submit_button("❌ Cancel")

            if submitted and task_name:
                task_id = f"TASK_{len(st.session_state.active_tasks) + 1:04d}"
                st.session_state.active_tasks[task_id] = {
                    "task_name": task_name,
                    "workflow": task_workflow,
                    "assigned_analyst": assigned_analyst,
                    "description": task_description,
                    "estimated_duration": estimated_duration,
                    "priority": priority,
                    "start_time": datetime.now(),
                    "status": "Active",
                    "paused_time": None,
                    "total_paused_duration": 0,
                    "source": "Manual Creation",
                }
                st.session_state.show_new_task = False
                st.success(f"✅ Task '{task_name}' started.")
                st.experimental_rerun()
            elif cancel:
                st.session_state.show_new_task = False
                st.experimental_rerun()

    if st.session_state.active_tasks:
        st.subheader("Active Tasks")

        for task_id, task in list(st.session_state.active_tasks.items()):
            css_class = "task-active" if task["status"] == "Active" else "task-paused"
            with st.container():
                st.markdown(
                    f'<div class="workflow-card {css_class}">', unsafe_allow_html=True
                )
                c1, c2, c3 = st.columns([3, 2, 1])

                with c1:
                    st.markdown(f"**{task['task_name']}**")
                    st.write(
                        f"Workflow: {WORKFLOW_LABELS.get(task['workflow'], task['workflow'])} | Analyst: {task['assigned_analyst']}"
                    )
                    st.write(
                        f"Priority: {task['priority']} | Started: {task['start_time'].strftime('%Y-%m-%d %H:%M')}"
                    )
                    if task.get("source"):
                        st.write(f"Source: {task['source']}")

                with c2:
                    current_duration = (
                        datetime.now() - task["start_time"]
                    ).total_seconds() / 60
                    st.write(f"Duration: {current_duration:.1f} min")
                    st.write(f"Status: {task['status']}")

                with c3:
                    if st.session_state.is_admin:
                        if task["status"] == "Active":
                            if st.button("⏸️ Pause", key=f"pause_{task_id}"):
                                st.session_state.active_tasks[task_id]["status"] = "Paused"
                                st.session_state.active_tasks[task_id][
                                    "paused_time"
                                ] = datetime.now()
                                st.experimental_rerun()
                            if st.button("✅ Complete", key=f"complete_{task_id}"):
                                t = st.session_state.active_tasks[task_id].copy()
                                t["end_time"] = datetime.now()
                                t["total_duration"] = (
                                    t["end_time"] - t["start_time"]
                                ).total_seconds() / 60
                                st.session_state.task_history.append(t)
                                del st.session_state.active_tasks[task_id]
                                st.experimental_rerun()
                        elif task["status"] == "Paused":
                            if st.button("▶️ Resume", key=f"resume_{task_id}"):
                                paused = (
                                    datetime.now()
                                    - st.session_state.active_tasks[task_id]["paused_time"]
                                ).total_seconds() / 60
                                st.session_state.active_tasks[task_id][
                                    "total_paused_duration"
                                ] += paused
                                st.session_state.active_tasks[task_id]["status"] = "Active"
                                st.session_state.active_tasks[task_id]["paused_time"] = None
                                st.experimental_rerun()
                    else:
                        st.caption("View only")

                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No active tasks yet.")

    if st.session_state.task_history:
        st.subheader("Task History")
        hist_df = pd.DataFrame(st.session_state.task_history)
        st.dataframe(hist_df, use_container_width=True)

# =========================
# TAB 5 – ANALYTICS
# =========================

with tab5:
    st.markdown(
        '<div class="section-header">📈 Department & Analyst Analytics</div>',
        unsafe_allow_html=True,
    )

    # ---- Analyst performance from Analyst Data ----
    adf_f = filtered_analyst_df()
    if not adf_f.empty:
        st.subheader("Analyst Performance (from Analyst Data)")

        numeric_cols = []
        for col in ["Target Qty", "Achieved Qty"]:
            if col in adf_f.columns:
                adf_f[col] = pd.to_numeric(adf_f[col], errors="coerce")
                numeric_cols.append(col)

        if "Team Member" in adf_f.columns and numeric_cols:
            analyst_perf = (
                adf_f.groupby("Team Member")[numeric_cols]
                .sum(numeric_only=True)
                .reset_index()
            )
            if "Target Qty" in analyst_perf.columns and "Achieved Qty" in analyst_perf.columns:
                analyst_perf["Achievement %"] = (
                    analyst_perf["Achieved Qty"] * 100.0 / analyst_perf["Target Qty"]
                ).round(1)
            st.dataframe(analyst_perf, use_container_width=True)

        if "Workflow" in adf_f.columns and "Achieved Qty" in adf_f.columns:
            wf_perf = (
                adf_f.groupby("Workflow")[["Achieved Qty"]]
                .sum(numeric_only=True)
                .reset_index()
                .sort_values("Achieved Qty", ascending=False)
            )
            st.subheader("Work Units by Workflow")
            st.dataframe(wf_perf, use_container_width=True)
    else:
        st.info("Upload workbook with 'Analyst Data' sheet to see analyst analytics.")

    # ---- Department metrics from Data Lake ----
    st.markdown("### Department Metrics (from Data Lake)")
    dl = st.session_state.data_lake_df
    if not dl.empty:
        st.dataframe(dl, use_container_width=True)
    else:
        st.info("Upload workbook with 'Data Lake' sheet to view department metrics.")

    # ---- Custom measure lab (Power BI-style) ----
    st.markdown("### Custom Measure Lab (simple Power BI-style)")

    available_sheets = {
        "Trade Pending's": st.session_state.trade_pending_df,
        "UCC": st.session_state.ucc_df,
        "Judgements": st.session_state.judgments_df,
        "Chapte11": st.session_state.chapter11_df,
        "Chapter7": st.session_state.chapter7_df,
        "Trade Tapes": st.session_state.trade_tapes_df,
        "Analyst Data": st.session_state.analyst_df,
        "Data Lake": st.session_state.data_lake_df,
        "Workflows": st.session_state.workflows_df,
    }

    sheet_name = st.selectbox(
        "Choose sheet for custom measure:", list(available_sheets.keys())
    )
    sheet_df = available_sheets[sheet_name]

    if sheet_df.empty:
        st.info(f"No data loaded for sheet '{sheet_name}'.")
    else:
        num_cols = [
            c for c in sheet_df.columns if pd.to_numeric(sheet_df[c], errors="coerce").notna().any()
        ]
        if not num_cols:
            st.info("No numeric columns detected to aggregate.")
        else:
            col_name = st.selectbox("Numeric column", num_cols)
            agg_func = st.selectbox(
                "Aggregation",
                ["Sum", "Average", "Count", "Distinct Count", "Min", "Max"],
            )

            col_series = pd.to_numeric(sheet_df[col_name], errors="coerce")

            if agg_func == "Sum":
                value = float(col_series.sum())
            elif agg_func == "Average":
                value = float(col_series.mean())
            elif agg_func == "Count":
                value = int(col_series.count())
            elif agg_func == "Distinct Count":
                value = int(col_series.nunique())
            elif agg_func == "Min":
                value = float(col_series.min())
            else:  # Max
                value = float(col_series.max())

            st.metric(f"{agg_func} of {col_name}", f"{value:,.2f}")

# =========================
# TAB 6 – WORKFLOW SETUP
# =========================

with tab6:
    st.markdown(
        '<div class="section-header">⚙️ Workflow Setup & Configuration</div>',
        unsafe_allow_html=True,
    )

    wf_df = st.session_state.workflows_df
    if not wf_df.empty:
        st.subheader("Workflows from Workbook")
        st.dataframe(wf_df, use_container_width=True)

        st.markdown(
            "Use this table to confirm SLA hours, priority, and quality requirements "
            "for each workflow like Trades Tape Imports, Pending, Placements, Judgments, UCC, "
            "Credit Files, Ch 11, Ch 7, Trade References, and Credit File Audits."
        )
    else:
        st.info("Upload workbook with 'Workflows' sheet to see configured workflows.")

# =========================
# FOOTER
# =========================

st.markdown("---")
st.markdown(
    "ARMS Workflow Management System v5.1 | Data-driven from ARMS Workbook | For internal use only"
)
