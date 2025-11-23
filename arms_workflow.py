import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime, timedelta, date
import time

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
]

WORKFLOW_LABELS = {
    "Pending Trade Workflow": "Pending Trades",
    "Placements Processing": "Placements",
    "UCC Filings": "UCC Filings",
    "Judgments Processing": "Judgments",
    "Chapter 11 Bankruptcy": "Chapter 11",
    "Chapter 7 Bankruptcy": "Chapter 7",
    "Credit Files Analysis": "Credit Files",
    "Data Import Monitoring": "Data Import",
    "Subscriber Management": "Subscriber Management",
    "Quality Assurance": "Quality Assurance",
}

# default demo metrics (used if we cannot calculate from data)
DEFAULT_WORKFLOW_METRICS = {
    "Pending Trade Workflow": {
        "pending": 71368,
        "analysts": 24,
        "time": "2.3 days",
        "sla": "92%",
    },
    "Placements Processing": {
        "pending": 2345,
        "analysts": 8,
        "time": "1.2 days",
        "sla": "95%",
    },
    "UCC Filings": {
        "pending": 1567,
        "analysts": 6,
        "time": "0.8 days",
        "sla": "98%",
    },
    "Judgments Processing": {
        "pending": 2890,
        "analysts": 7,
        "time": "1.5 days",
        "sla": "94%",
    },
    "Chapter 11 Bankruptcy": {
        "pending": 456,
        "analysts": 3,
        "time": "3.2 days",
        "sla": "89%",
    },
    "Chapter 7 Bankruptcy": {
        "pending": 321,
        "analysts": 2,
        "time": "2.8 days",
        "sla": "91%",
    },
    "Credit Files Analysis": {
        "pending": 1789,
        "analysts": 5,
        "time": "1.1 days",
        "sla": "96%",
    },
    "Data Import Monitoring": {
        "pending": 567,
        "analysts": 4,
        "time": "0.5 days",
        "sla": "99%",
    },
    "Subscriber Management": {
        "pending": 234,
        "analysts": 3,
        "time": "0.3 days",
        "sla": "97%",
    },
    "Quality Assurance": {
        "pending": 123,
        "analysts": 2,
        "time": "1.0 days",
        "sla": "93%",
    },
}

# =========================
# CUSTOM CSS
# =========================

st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .workflow-card {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .task-active {
        border-left: 4px solid #28a745;
    }
    .task-paused {
        border-left: 4px solid #ffc107;
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

if "active_tasks" not in st.session_state:
    st.session_state.active_tasks = {}
if "task_history" not in st.session_state:
    st.session_state.task_history = []
if "workflow_data" not in st.session_state:
    st.session_state.workflow_data = {}
if "historical_data" not in st.session_state:
    st.session_state.historical_data = pd.DataFrame()
if "workflow_definitions" not in st.session_state:
    st.session_state.workflow_definitions = {}
if "show_new_task" not in st.session_state:
    st.session_state.show_new_task = False
if "active_filter" not in st.session_state:
    st.session_state.active_filter = None
if "date_filter" not in st.session_state:
    st.session_state.date_filter = None

# =========================
# HEADER
# =========================

st.markdown(
    '<div class="main-header">ARMS Workflow Management System</div>',
    unsafe_allow_html=True,
)

# =========================
# SIDEBAR
# =========================

with st.sidebar:
    st.header("ARMS Navigation")

    # ----- Data Import -----
    st.subheader("📁 Data Import")
    uploaded_files = st.file_uploader(
        "Upload Excel/CSV Files:",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
        help="Upload historical data, current workflows, or performance metrics",
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_up = pd.read_csv(uploaded_file)
                else:
                    df_up = pd.read_excel(uploaded_file)

                # simple cleanup: strip col names
                df_up.columns = [c.strip() for c in df_up.columns]

                if st.session_state.historical_data.empty:
                    st.session_state.historical_data = df_up
                else:
                    st.session_state.historical_data = pd.concat(
                        [st.session_state.historical_data, df_up], ignore_index=True
                    )

                st.success(f"✅ {uploaded_file.name} loaded successfully!")
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")

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
    if st.button("🎯 Start New Task", use_container_width=True):
        st.session_state.show_new_task = True
        st.rerun()

    # ----- Global filters (slicer + date) -----
    st.markdown("---")
    st.subheader("Global Filters")

    combined_df = st.session_state.historical_data.copy()
    if st.session_state.task_history:
        task_history_df = pd.DataFrame(st.session_state.task_history)
        if combined_df.empty:
            combined_df = task_history_df
        else:
            combined_df = pd.concat([combined_df, task_history_df], ignore_index=True)

    if not combined_df.empty:
        # generic column filter
        filter_col = st.selectbox(
            "Filter column",
            options=combined_df.columns.tolist(),
        )

        unique_vals = (
            combined_df[filter_col].dropna().astype(str).unique().tolist()
        )

        selected_vals = st.multiselect(
            "Filter values",
            options=unique_vals,
            default=unique_vals,
        )

        st.session_state.active_filter = {
            "column": filter_col,
            "values": selected_vals,
        }

        # date filter
        st.markdown("**Date filter**")

        df_for_dates = combined_df.copy()
        # detect date-typed columns
        date_columns = df_for_dates.select_dtypes(
            include=["datetime64[ns]", "datetime64[ns, UTC]"]
        ).columns.tolist()

        # also try columns with "date" in name
        if not date_columns:
            candidate_cols = [c for c in df_for_dates.columns if "date" in c.lower()]
            for c in candidate_cols:
                try:
                    df_for_dates[c] = pd.to_datetime(df_for_dates[c])
                    date_columns.append(c)
                except Exception:
                    pass

        if date_columns:
            date_col = st.selectbox("Date column", date_columns, key="date_col_select")

            min_d = df_for_dates[date_col].min()
            max_d = df_for_dates[date_col].max()

            if pd.isna(min_d) or pd.isna(max_d):
                st.caption("No valid dates found to build a range.")
                st.session_state.date_filter = None
            else:
                start_default = min_d.date()
                end_default = max_d.date()
                start_date, end_date = st.date_input(
                    "Date range",
                    [start_default, end_default],
                )
                if isinstance(start_date, date) and isinstance(end_date, date):
                    st.session_state.date_filter = {
                        "column": date_col,
                        "start": datetime.combine(start_date, datetime.min.time()),
                        "end": datetime.combine(end_date, datetime.max.time()),
                    }
        else:
            st.caption("No date-like columns detected for date filter.")
            st.session_state.date_filter = None
    else:
        st.caption("Upload data or complete tasks to enable global filters.")
        st.session_state.active_filter = None
        st.session_state.date_filter = None

# =========================
# HELPER: APPLY FILTERS
# =========================

def apply_global_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Apply active_filter and date_filter from session_state to a dataframe."""
    if df is None or df.empty:
        return df

    result = df.copy()

    # generic filter
    af = st.session_state.get("active_filter")
    if af and af.get("column") in result.columns:
        try:
            result = result[result[af["column"]].astype(str).isin(af["values"])]
        except Exception:
            pass

    # date filter
    df_filter = st.session_state.get("date_filter")
    if df_filter and df_filter.get("column") in result.columns:
        try:
            col = df_filter["column"]
            result[col] = pd.to_datetime(result[col], errors="coerce")
            mask = (result[col] >= df_filter["start"]) & (
                result[col] <= df_filter["end"]
            )
            result = result[mask]
        except Exception:
            pass

    return result


def get_workflow_metrics(selected_key: str) -> dict:
    """
    Try to compute dynamic 'pending' counts from historical_data using a workflow-like column.
    Fallback to DEFAULT_WORKFLOW_METRICS.
    """
    base = DEFAULT_WORKFLOW_METRICS.get(selected_key, DEFAULT_WORKFLOW_METRICS["Pending Trade Workflow"]).copy()

    df = st.session_state.historical_data
    if df is None or df.empty:
        return base

    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    # guess workflow column
    workflow_col = None
    for c in df.columns:
        low = c.lower()
        if "workflow" in low or "process" in low or "chapter" in low or "work_type" in low:
            workflow_col = c
            break

    if not workflow_col:
        return base

    try:
        df[workflow_col] = df[workflow_col].astype(str)
    except Exception:
        return base

    # try to match selected workflow using label keywords
    label = WORKFLOW_LABELS.get(selected_key, selected_key)
    keywords = [
        "Pending Trades",
        "Placements",
        "UCC",
        "Judgments",
        "Chapter 11",
        "Chapter 7",
        "Credit Files",
        "Data Import",
        "Subscriber",
        "Quality Assurance",
    ]

    target = label
    # very simple: count rows where workflow column contains label bits
    mask = df[workflow_col].str.contains(label, case=False, na=False)
    if not mask.any():
        # for Chapter 11 etc, just search by chapter
        if "Chapter 11" in label:
            mask = df[workflow_col].str.contains("11", case=False, na=False)
        elif "Chapter 7" in label:
            mask = df[workflow_col].str.contains("7", case=False, na=False)

    count = int(mask.sum())
    if count > 0:
        base["pending"] = count

    return base


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

    current_metrics = get_workflow_metrics(selected_workflow)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Pending Items", f"{current_metrics['pending']:,}")
    with c2:
        st.metric("Active Analysts", current_metrics["analysts"])
    with c3:
        st.metric("Avg Processing Time", current_metrics["time"])
    with c4:
        st.metric("SLA Compliance", current_metrics["sla"])

    st.subheader(
        f"{WORKFLOW_LABELS.get(selected_workflow, selected_workflow)} - Distribution"
    )

    workflow_data = {
        "Workflow": [
            "Pending Trades",
            "Placements",
            "UCC Filings",
            "Judgments",
            "Chapter 11",
            "Chapter 7",
            "Credit Files",
            "Data Import",
            "Subscriber Management",
            "Quality Assurance",
        ],
        "Pending_Items": [71368, 2345, 1567, 2890, 456, 321, 1789, 567, 234, 123],
    }
    workflow_df = pd.DataFrame(workflow_data)
    st.bar_chart(workflow_df.set_index("Workflow")["Pending_Items"])

# =========================
# TAB 2 – PENDING WORKFLOW
# =========================

with tab2:
    st.markdown(
        f'<div class="section-header">📋 {WORKFLOW_LABELS.get(selected_workflow, selected_workflow)} Analysis</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Database Table Integration")

    tables_info = {
        "Table 1": "Trades Tape Import - File Dates",
        "Table 2": "Trades Tape Import - Analyst & Performance",
        "Table 3": "Pending Data - Import Timeline",
        "Table 4": "Pending Data - Analyst Assignment",
        "Table 5": "Placements - Basic Metrics",
        "Table 6": "Placements - Credit Files Analysis",
        "Table 7": "UCC Filings - Basic Metrics",
        "Table 8": "UCC Filings - Credit Files Analysis",
        "Table 9": "Judgments - Basic Metrics",
        "Table 10": "Judgments - Credit Files Analysis",
        "Table 11": "Chapter 11 - Import Timeline",
        "Table 12": "Chapter 11 - Analyst Assignment",
        "Table 13": "Chapter 7 - Import Timeline",
        "Table 14": "Chapter 7 - Analyst Assignment",
    }

    st.multiselect(
        "Select tables to analyze:",
        list(tables_info.keys()),
        default=["Table 1", "Table 2", "Table 3", "Table 4"],
        format_func=lambda x: f"{x}: {tables_info[x]}",
    )

    if not st.session_state.historical_data.empty:
        df = apply_global_filters(st.session_state.historical_data)

        st.subheader("Historical Data Overview (Filtered)")
        st.dataframe(df, use_container_width=True)

        st.subheader("Data Summary")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Records", len(df))
        with c2:
            st.metric("Columns", len(df.columns))
        with c3:
            date_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"])
            if not date_cols.empty:
                st.metric("Earliest Date", str(date_cols.min().min().date()))
            else:
                st.metric("Earliest Date", "N/A")

# =========================
# TAB 3 – EMAIL IMPORT
# =========================

with tab3:
    st.markdown(
        '<div class="section-header">📧 Email Work Import & Management</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Upload Email Work Files")

    email_files = st.file_uploader(
        "Upload email files or work request spreadsheets:",
        type=["xlsx", "xls", "csv", "eml"],
        accept_multiple_files=True,
        help="Upload .eml or Excel/CSV containing work requests",
        key="email_uploader",
    )

    email_data = []

    if email_files:
        st.success(f"✅ {len(email_files)} file(s) uploaded successfully!")

        for email_file in email_files:
            try:
                name = email_file.name.lower()

                # --- Raw .eml email files ---
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

                    # Extract plain text body
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
                        fname = att.get_filename()
                        if fname:
                            attachments.append(fname)

                    email_data.append(
                        {
                            "email_file": email_file.name,
                            "work_item_id": f"EMAIL_{len(email_data)+1:04d}",
                            "subject": subject,
                            "requestor": requestor,
                            "received_date": received_dt,
                            "priority": "Medium",
                            "estimated_effort_minutes": 30,
                            "assigned_to": "Unassigned",
                            "status": "New",
                            "body_preview": body[:500],
                            "attachments": ", ".join(attachments),
                        }
                    )

                # --- Excel / CSV work request sheets ---
                elif name.endswith(".csv"):
                    df_sheet = pd.read_csv(email_file)
                else:
                    df_sheet = pd.read_excel(email_file)

                if not name.endswith(".eml"):
                    df_sheet.columns = [c.strip() for c in df_sheet.columns]
                    for _, row in df_sheet.iterrows():
                        email_data.append(
                            {
                                "email_file": email_file.name,
                                "work_item_id": f"EMAIL_{len(email_data)+1:04d}",
                                "subject": row.get("subject", "N/A"),
                                "requestor": row.get("from", "Unknown"),
                                "received_date": row.get(
                                    "date", datetime.now().strftime("%Y-%m-%d")
                                ),
                                "priority": row.get("priority", "Medium"),
                                "estimated_effort_minutes": row.get(
                                    "estimated_effort", 30
                                ),
                                "assigned_to": "Unassigned",
                                "status": "New",
                                "body_preview": str(row.get("body", ""))[:500],
                                "attachments": str(row.get("attachments", "")),
                            }
                        )

            except Exception as e:
                st.error(f"Error processing {email_file.name}: {str(e)}")

    if email_data:
        email_df = pd.DataFrame(email_data)
        st.subheader("Extracted Work Items")
        st.dataframe(email_df, use_container_width=True)

        st.subheader("Assign Work Items & Create Tasks")

        c1, c2 = st.columns(2)
        with c1:
            selected_items = st.multiselect(
                "Select work items to assign:",
                options=email_df["work_item_id"].tolist(),
            )
        with c2:
            assigned_analyst = st.selectbox(
                "Assign to Analyst:",
                options=TEAM_MEMBERS,
            )
            workflow_type = st.selectbox(
                "Workflow Type:",
                list(WORKFLOW_LABELS.keys()),
                format_func=lambda x: WORKFLOW_LABELS.get(x, x),
            )

            if st.button("Create Tasks from Selected Items", type="primary"):
                for item_id in selected_items:
                    row = email_df[email_df["work_item_id"] == item_id].iloc[0]
                    task_id = f"TASK_{len(st.session_state.active_tasks) + 1:04d}"

                    st.session_state.active_tasks[task_id] = {
                        "task_name": f"Email: {row['subject']}",
                        "workflow": workflow_type,
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

                st.success(
                    f"✅ {len(selected_items)} tasks created and assigned to {assigned_analyst}"
                )
                st.rerun()

# =========================
# TAB 4 – TASK MANAGEMENT
# =========================

with tab4:
    st.markdown(
        '<div class="section-header">⏱️ Task Time Tracking & Management</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Active Task Management")

    # New task form
    if st.session_state.show_new_task:
        with st.form("new_task_form"):
            st.subheader("Create New Task")

            c1, c2 = st.columns(2)
            with c1:
                task_name = st.text_input(
                    "Task Name:",
                    placeholder="Enter task name",
                )
                task_workflow = st.selectbox(
                    "Workflow Type:",
                    list(WORKFLOW_LABELS.keys()),
                    format_func=lambda x: WORKFLOW_LABELS.get(x, x),
                )
                assigned_analyst = st.selectbox(
                    "Assign to Analyst:",
                    TEAM_MEMBERS,
                )
            with c2:
                task_description = st.text_area(
                    "Task Description:",
                    placeholder="Describe the task...",
                )
                estimated_duration = st.number_input(
                    "Estimated Duration (minutes):",
                    min_value=5,
                    value=30,
                )
                priority = st.selectbox(
                    "Priority:",
                    ["Low", "Medium", "High", "Critical"],
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
                st.success(f"✅ Task '{task_name}' started successfully!")
                st.rerun()
            elif cancel:
                st.session_state.show_new_task = False
                st.rerun()

    if st.session_state.active_tasks:
        st.subheader("Currently Active Tasks")

        for task_id, task in list(st.session_state.active_tasks.items()):
            task_class = "task-active" if task["status"] == "Active" else "task-paused"

            with st.container():
                st.markdown(
                    f'<div class="workflow-card {task_class}">', unsafe_allow_html=True
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
                    if task["status"] == "Active":
                        if st.button("⏸️ Pause", key=f"pause_{task_id}"):
                            st.session_state.active_tasks[task_id]["status"] = "Paused"
                            st.session_state.active_tasks[task_id][
                                "paused_time"
                            ] = datetime.now()
                            st.rerun()
                        if st.button("✅ Complete", key=f"complete_{task_id}"):
                            task_data = st.session_state.active_tasks[task_id].copy()
                            task_data["end_time"] = datetime.now()
                            task_data["total_duration"] = (
                                task_data["end_time"] - task_data["start_time"]
                            ).total_seconds() / 60
                            st.session_state.task_history.append(task_data)
                            del st.session_state.active_tasks[task_id]
                            st.rerun()
                    elif task["status"] == "Paused":
                        if st.button("▶️ Resume", key=f"resume_{task_id}"):
                            paused_duration = (
                                datetime.now()
                                - st.session_state.active_tasks[task_id]["paused_time"]
                            ).total_seconds() / 60
                            st.session_state.active_tasks[task_id][
                                "total_paused_duration"
                            ] += paused_duration
                            st.session_state.active_tasks[task_id]["status"] = "Active"
                            st.session_state.active_tasks[task_id]["paused_time"] = None
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info(
            "No active tasks. Use 'Start New Task' (sidebar) or create from Email Import."
        )

    if st.session_state.task_history:
        st.subheader("Task History")
        history_df = pd.DataFrame(st.session_state.task_history)
        st.dataframe(history_df, use_container_width=True)

# =========================
# TAB 5 – ANALYTICS
# =========================

with tab5:
    st.markdown(
        '<div class="section-header">📈 Comprehensive Analytics</div>',
        unsafe_allow_html=True,
    )

    all_data = st.session_state.historical_data.copy()
    if st.session_state.task_history:
        task_history_df = pd.DataFrame(st.session_state.task_history)
        if not all_data.empty:
            all_data = pd.concat([all_data, task_history_df], ignore_index=True)
        else:
            all_data = task_history_df

    if not all_data.empty:
        all_data = apply_global_filters(all_data)

        st.subheader("Combined Historical & Current Data (Filtered)")
        st.dataframe(all_data, use_container_width=True)

        st.subheader("Performance Analytics")
        c1, c2, c3 = st.columns(3)

        with c1:
            if "total_duration" in all_data.columns:
                avg_duration = all_data["total_duration"].mean()
                st.metric("Average Task Duration", f"{avg_duration:.1f} min")

        with c2:
            if "priority" in all_data.columns:
                high_priority = len(all_data[all_data["priority"] == "High"])
                st.metric("High Priority Tasks", high_priority)

        with c3:
            if "workflow" in all_data.columns:
                unique_workflows = all_data["workflow"].nunique()
                st.metric("Active Workflows", unique_workflows)

    st.subheader("Department Performance Metrics")

    dept_metrics_data = {
        "Metric": [
            "Total Items Processed",
            "Average Processing Time",
            "SLA Compliance Rate",
            "Quality Score",
            "Cost per Item",
            "Analyst Utilization",
            "Backlog Size",
            "Customer Satisfaction",
        ],
        "Current": [
            15432,
            "2.3 days",
            "92%",
            "94.5%",
            "$4.67",
            "78%",
            71368,
            "4.2/5.0",
        ],
        "Target": [
            16000,
            "2.0 days",
            "95%",
            "96%",
            "$4.50",
            "85%",
            50000,
            "4.5/5.0",
        ],
        "Variance": [
            "-3.5%",
            "+15%",
            "-3%",
            "-1.5%",
            "+3.8%",
            "-7%",
            "+42.7%",
            "-0.3",
        ],
    }
    dept_metrics_df = pd.DataFrame(dept_metrics_data)
    st.dataframe(dept_metrics_df, use_container_width=True)

# =========================
# TAB 6 – WORKFLOW SETUP
# =========================

with tab6:
    st.markdown(
        '<div class="section-header">⚙️ Workflow Setup & Configuration</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Define New Workflow")

    with st.form("workflow_definition"):
        c1, c2 = st.columns(2)
        with c1:
            workflow_name = st.text_input("Workflow Name:")
            sla_target = st.number_input(
                "SLA Target (%):", min_value=0, max_value=100, value=95
            )
            max_processing_time = st.number_input(
                "Max Processing Time (hours):", min_value=1, value=24
            )
        with c2:
            assigned_team = st.text_input("Assigned Team:")
            required_approvals = st.number_input(
                "Required Approvals:", min_value=0, value=1
            )
            priority_level = st.selectbox(
                "Default Priority:",
                ["Low", "Medium", "High", "Critical"],
            )

        data_points = st.text_area(
            "Required Data Points (comma-separated):",
            placeholder="subscriber_id, trade_date, amount, status...",
        )

        submitted = st.form_submit_button("Create Workflow Definition")

        if submitted and workflow_name:
            workflow_id = f"WF_{len(st.session_state.workflow_definitions) + 1:03d}"
            st.session_state.workflow_definitions[workflow_id] = {
                "workflow_name": workflow_name,
                "sla_target": sla_target,
                "max_processing_time": max_processing_time,
                "assigned_team": assigned_team,
                "required_approvals": required_approvals,
                "priority_level": priority_level,
                "data_points": [
                    dp.strip() for dp in data_points.split(",")
                ]
                if data_points
                else [],
                "created_date": datetime.now().strftime("%Y-%m-%d"),
            }
            st.success(f"✅ Workflow '{workflow_name}' defined successfully!")

    if st.session_state.workflow_definitions:
        st.subheader("Defined Workflows")
        workflows_df = pd.DataFrame.from_dict(
            st.session_state.workflow_definitions, orient="index"
        )
        st.dataframe(workflows_df, use_container_width=True)

# =========================
# EXPORT SECTION
# =========================

st.markdown("---")
st.subheader("📤 Export Data & Reports")

ec1, ec2, ec3 = st.columns(3)
with ec1:
    export_format = st.radio("Export Format:", ["Excel", "CSV"])
with ec2:
    include_sections = st.multiselect(
        "Include Sections:",
        [
            "Task History",
            "Active Tasks",
            "Workflow Definitions",
            "Historical Data",
        ],
        default=["Task History", "Active Tasks"],
    )
with ec3:
    st.write("")
    if st.button("Generate Comprehensive Report", type="primary"):
        with st.spinner("Generating export file..."):
            time.sleep(2)
            output = io.BytesIO()

            if export_format == "Excel":
                from pandas import ExcelWriter

                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    if "Task History" in include_sections and st.session_state.task_history:
                        pd.DataFrame(st.session_state.task_history).to_excel(
                            writer, sheet_name="Task_History", index=False
                        )
                    if "Active Tasks" in include_sections and st.session_state.active_tasks:
                        pd.DataFrame.from_dict(
                            st.session_state.active_tasks, orient="index"
                        ).to_excel(
                            writer, sheet_name="Active_Tasks", index=False
                        )
                    if (
                        "Workflow Definitions" in include_sections
                        and st.session_state.workflow_definitions
                    ):
                        pd.DataFrame.from_dict(
                            st.session_state.workflow_definitions, orient="index"
                        ).to_excel(
                            writer, sheet_name="Workflow_Definitions", index=False
                        )
                    if (
                        "Historical Data" in include_sections
                        and not st.session_state.historical_data.empty
                    ):
                        st.session_state.historical_data.to_excel(
                            writer, sheet_name="Historical_Data", index=False
                        )
                mime_type = "application/vnd.ms-excel"
                file_name = f"ARMS_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            else:
                csv_df_list = []
                if "Task History" in include_sections and st.session_state.task_history:
                    csv_df_list.append(
                        pd.DataFrame(st.session_state.task_history)
                    )
                if "Active Tasks" in include_sections and st.session_state.active_tasks:
                    csv_df_list.append(
                        pd.DataFrame.from_dict(
                            st.session_state.active_tasks, orient="index"
                        )
                    )
                if (
                    "Workflow Definitions" in include_sections
                    and st.session_state.workflow_definitions
                ):
                    csv_df_list.append(
                        pd.DataFrame.from_dict(
                            st.session_state.workflow_definitions, orient="index"
                        )
                    )
                if (
                    "Historical Data" in include_sections
                    and not st.session_state.historical_data.empty
                ):
                    csv_df_list.append(st.session_state.historical_data)

                if csv_df_list:
                    export_df = pd.concat(csv_df_list, ignore_index=True)
                else:
                    export_df = pd.DataFrame()

                export_df.to_csv(output, index=False)
                mime_type = "text/csv"
                file_name = f"ARMS_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

            st.success("Export generated successfully!")
            st.download_button(
                label="Download Export File",
                data=output.getvalue(),
                file_name=file_name,
                mime=mime_type,
            )

# =========================
# FOOTER
# =========================

st.markdown("---")
st.markdown(
    "ARMS Workflow Management System v4.3 | GitHub & Streamlit Ready | For internal use only"
)

with st.expander("🚀 Deployment Notes"):
    st.markdown(
        """
Deployment checklist:

1. Save this file as `arms_workflow.py` in your GitHub repo.
2. Create `requirements.txt` with at least:
   streamlit
   pandas
   numpy
   openpyxl
   xlsxwriter
   """
    )
