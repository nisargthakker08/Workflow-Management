import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from email import policy
from email.parser import BytesParser

# ======================================
# PAGE CONFIG
# ======================================

st.set_page_config(
    page_title="ARMS Workflow Management",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================================
# STYLING
# ======================================

st.markdown(
    """
<style>
    .main-header {
        font-size: 2.3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.6rem 2rem;
        border-radius: 15px;
        text-align: left;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 0.3rem;
    }
    .section-card {
        background: #ffffff;
        padding: 1.4rem;
        border-radius: 12px;
        box-shadow: 0 5px 18px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        margin-top: 0.7rem;
        margin-bottom: 0.7rem;
    }
    .status-badge {
        padding: 0.2rem 0.7rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-New {
        background: #e0f2fe;
        color: #0369a1;
    }
    .status-In\\ Progress {
        background: #fef3c7;
        color: #92400e;
    }
    .status-Paused {
        background: #e5e7eb;
        color: #374151;
    }
    .status-Completed {
        background: #dcfce7;
        color: #166534;
    }
    .priority-Critical,
    .priority-High {
        background: #fee2e2;
        color: #b91c1c;
    }
    .priority-Medium {
        background: #fffbeb;
        color: #92400e;
    }
    .priority-Low {
        background: #ecfeff;
        color: #155e75;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ======================================
# SESSION STATE
# ======================================

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
]

STATUSES = ["New", "In Progress", "Paused", "Completed"]
PRIORITIES = ["Critical", "High", "Medium", "Low"]

if "tasks" not in st.session_state:
    st.session_state.tasks = []  # list of dict

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1001

if "current_user" not in st.session_state:
    st.session_state.current_user = "Nisarg Thakker"

if "last_assigned_task" not in st.session_state:
    st.session_state.last_assigned_task = None

if "achieved_df" not in st.session_state:
    st.session_state.achieved_df = None

if "achieved_sheet_name" not in st.session_state:
    st.session_state.achieved_sheet_name = None


def reset_all_tasks():
    """Hard reset for old / demo tasks in session."""
    st.session_state.tasks = []
    st.session_state.next_task_id = 1001
    st.session_state.last_assigned_task = None


# ======================================
# TASK HELPERS
# ======================================

def create_task(
    title: str,
    company: str,
    priority: str,
    assigned_to: str = "Unassigned",
    status: str = "New",
    description: str = "",
    department: str = "Operations",
    due_date: date | None = None,
    source: str = "Manual",
):
    task_id = st.session_state.next_task_id
    st.session_state.next_task_id += 1

    if due_date is None:
        due_date = date.today() + timedelta(days=7)

    task = {
        "Task ID": task_id,
        "Title": title,
        "Company": company,
        "Priority": priority if priority in PRIORITIES else "Medium",
        "Status": status if status in STATUSES else "New",
        "Assigned To": assigned_to,
        "Created At": datetime.now(),
        "Due Date": due_date,
        "Completed At": None,
        "Description": description,
        "Department": department,
        "Source": source,
    }
    st.session_state.tasks.append(task)
    return task


def tasks_df() -> pd.DataFrame:
    if not st.session_state.tasks:
        cols = [
            "Task ID",
            "Title",
            "Company",
            "Priority",
            "Status",
            "Assigned To",
            "Created At",
            "Due Date",
            "Completed At",
            "Description",
            "Department",
            "Source",
        ]
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(st.session_state.tasks)
    if "Created At" in df.columns:
        df["Created At"] = pd.to_datetime(df["Created At"], errors="coerce")
        df = df.sort_values("Created At", ascending=False)
    return df


def available_new_tasks():
    return [
        t
        for t in st.session_state.tasks
        if t.get("Status") == "New" and t.get("Assigned To") == "Unassigned"
    ]


def user_tasks(user: str):
    return [t for t in st.session_state.tasks if t.get("Assigned To") == user]


# ======================================
# IMPORT HELPERS
# ======================================

def import_tasks_from_excel(uploaded_file) -> int:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return 0

    created = 0
    for _, row in df.iterrows():
        title = (
            row.get("Title")
            or row.get("Task Title")
            or row.get("Subject")
            or f"Imported Task {st.session_state.next_task_id}"
        )
        company = row.get("Company") or row.get("Company Name") or "N/A"
        priority = row.get("Priority") or "Medium"
        desc = row.get("Description") or ""
        dept = row.get("Department") or "Operations"

        # due date if column exists
        due = None
        for col in df.columns:
            if "due" in col.lower():
                try:
                    d = pd.to_datetime(row[col], errors="coerce")
                    if pd.notna(d):
                        due = d.date()
                except Exception:
                    pass
                break

        create_task(
            title=str(title),
            company=str(company),
            priority=str(priority),
            assigned_to="Unassigned",
            status="New",
            description=str(desc),
            department=str(dept),
            due_date=due,
            source=f"Excel:{uploaded_file.name}",
        )
        created += 1
    return created


def import_task_from_eml(eml_file) -> bool:
    try:
        raw_bytes = eml_file.read()
        msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)

        subject = msg["subject"] or "No subject"
        sender = msg["from"] or "Unknown sender"
        received = msg["date"]

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = str(part.get("Content-Disposition", ""))
                if "attachment" in disp:
                    continue
                if ctype == "text/plain":
                    try:
                        body = part.get_content()
                    except Exception:
                        pass
        else:
            body = msg.get_content()

        content_lower = (subject + " " + body).lower()
        priority = "Medium"
        if "urgent" in content_lower or "asap" in content_lower:
            priority = "Critical"
        elif "important" in content_lower:
            priority = "High"

        description = f"Email task from {sender}\nReceived: {received}\n\n{body[:1000]}"

        create_task(
            title=f"Email: {subject}",
            company=f"Email from {sender}",
            priority=priority,
            assigned_to="Unassigned",
            status="New",
            description=description,
            department="Operations",
            source="Email",
        )
        return True
    except Exception as e:
        st.error(f"Error processing email: {e}")
        return False


# ======================================
# ACHIEVED DATA HELPERS
# ======================================

def load_achieved_workbook(uploaded_file):
    try:
        xls = pd.ExcelFile(uploaded_file)
        sheet = st.selectbox("Select sheet", xls.sheet_names, key="achieved_sheet_select")
        df = pd.read_excel(xls, sheet_name=sheet)
        st.session_state.achieved_df = df
        st.session_state.achieved_sheet_name = sheet
        st.success(f"Loaded sheet '{sheet}' with {len(df)} rows.")
    except Exception as e:
        st.error(f"Error loading workbook: {e}")


# ======================================
# UI: HEADER + USER
# ======================================

st.markdown(
    '<div class="main-header">🚀 ARMS Workflow Management System</div>',
    unsafe_allow_html=True,
)

col_user_1, col_user_2 = st.columns([0.7, 0.3])

with col_user_1:
    if st.button("🧹 Reset all tasks (clear old data)"):
        reset_all_tasks()
        st.success("All tasks cleared. Start fresh by importing Excel / emails or creating tasks.")
        st.experimental_rerun()

with col_user_2:
    # Fixed current user as Nisarg for now.
    # If you later want a dropdown, replace this block with a selectbox over ANALYSTS.
    st.write("Analyst: **Nisarg Thakker**")
    st.session_state.current_user = "Nisarg Thakker"

# ======================================
# TABS
# ======================================

tab_tasks, tab_analytics, tab_import, tab_team, tab_achieved = st.tabs(
    ["📋 Task Management", "📊 Analytics", "📁 Data Import", "👥 Team Metrics", "📈 Achieved Data / ARMS Excel"]
)

# ======================================
# TAB: TASK MANAGEMENT
# ======================================

with tab_tasks:
    df_all = tasks_df()
    my_tasks = user_tasks(st.session_state.current_user)
    new_avail = available_new_tasks()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Get New Task</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(new_avail)}</div>', unsafe_allow_html=True)
        get_new_clicked = st.button("🚀 Get New Task", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">My Tasks</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(my_tasks)}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Tasks</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(df_all)}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Create Task</div>', unsafe_allow_html=True)
        create_clicked = st.button("➕ New Task", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Get New Task logic
    if get_new_clicked:
        if new_avail:
            t = new_avail[0]
            t["Assigned To"] = st.session_state.current_user
            t["Status"] = "In Progress"
            st.session_state.last_assigned_task = t
            st.success(f"Assigned Task #{t.get('Task ID')} to you.")
        else:
            st.info("No new unassigned tasks available.")

    if st.session_state.last_assigned_task:
        t = st.session_state.last_assigned_task
        st.markdown("### Last Assigned Task Summary")
        with st.expander(f"Task #{t.get('Task ID')} – {t.get('Title', '')}", expanded=True):
            st.write(f"**Company:** {t.get('Company', 'N/A')}")
            st.write(f"**Priority:** {t.get('Priority', 'N/A')}")
            st.write(f"**Status:** {t.get('Status', 'N/A')}")
            st.write(f"**Assigned To:** {t.get('Assigned To', 'N/A')}")
            st.write(f"**Created At:** {t.get('Created At', 'N/A')}")
            st.write(f"**Due Date:** {t.get('Due Date', 'N/A')}")
            st.write(f"**Source:** {t.get('Source', 'N/A')}")
            st.write("**Description:**")
            st.write(t.get("Description", ""))

    # Create Task form
    if create_clicked:
        st.markdown("### Create Task")
        with st.form("create_task_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                title = st.text_input("Title")
                company = st.text_input("Company Name")
                priority = st.selectbox("Priority", PRIORITIES, index=1)
                department = st.selectbox("Department", ["Finance", "Legal", "Compliance", "Operations", "Risk"])
            with col_b:
                assigned_to = st.selectbox("Assign To", ["Unassigned"] + ANALYSTS)
                due = st.date_input("Due Date", value=date.today() + timedelta(days=7))
                status = "New" if assigned_to == "Unassigned" else "In Progress"
            description = st.text_area("Description", height=120)
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                submit_new = st.form_submit_button("Save Task", type="primary")
            with col_b2:
                cancel_new = st.form_submit_button("Cancel")

            if submit_new:
                if not title:
                    st.error("Title is required.")
                else:
                    t = create_task(
                        title=title,
                        company=company or "N/A",
                        priority=priority,
                        assigned_to=assigned_to,
                        status=status,
                        description=description,
                        department=department,
                        due_date=due,
                        source="Manual",
                    )
                    st.success(f"Created Task #{t.get('Task ID')}.")
                    st.session_state.last_assigned_task = t
            if cancel_new:
                st.experimental_rerun()

    st.markdown("---")

    # View selection
    view_mode = st.radio(
        "View",
        ["My Tasks", "Available (New & Unassigned)", "All Tasks"],
        horizontal=True,
    )

    if view_mode == "My Tasks":
        show_tasks = my_tasks
    elif view_mode == "Available (New & Unassigned)":
        show_tasks = new_avail
    else:
        show_tasks = st.session_state.tasks

    if not show_tasks:
        st.info("No tasks to show.")
    else:
        st.markdown("### Tasks")
        # sort by due date then priority, safely
        show_tasks_sorted = sorted(
            show_tasks,
            key=lambda t: (
                t.get("Due Date", date.today()),
                PRIORITIES.index(t.get("Priority")) if t.get("Priority") in PRIORITIES else 99,
            ),
        )

        for t in show_tasks_sorted[:50]:
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 2, 1.3, 1.3])

                created_at = t.get("Created At")
                if isinstance(created_at, (datetime, pd.Timestamp)):
                    created_str = created_at.strftime("%Y-%m-%d")
                else:
                    created_str = str(created_at)

                due_val = t.get("Due Date")
                if isinstance(due_val, pd.Timestamp):
                    due_val = due_val.date()
                if isinstance(due_val, (datetime, date)):
                    due_str = due_val.isoformat()
                else:
                    due_str = str(due_val)

                with c1:
                    st.write(f"**#{t.get('Task ID')} – {t.get('Title', '')}**")
                    st.caption(
                        f"{t.get('Company', 'N/A')} | {t.get('Department', 'N/A')} | Source: {t.get('Source', 'N/A')}"
                    )
                with c2:
                    st.write(f"Assigned: {t.get('Assigned To', 'N/A')}")
                    st.write(f"Created: {created_str}")
                    st.write(f"Due: {due_str}")
                with c3:
                    status_val = t.get("Status", "New")
                    st.markdown(
                        f"<span class='status-badge status-{status_val.replace(' ', '\\ ')}'>{status_val}</span>",
                        unsafe_allow_html=True,
                    )
                    priority_val = t.get("Priority", "Medium")
                    st.markdown(
                        f"<span class='status-badge priority-{priority_val}'>{priority_val}</span>",
                        unsafe_allow_html=True,
                    )
                with c4:
                    # Accept / Pause / Resume / Complete buttons
                    if t.get("Status") == "New" and t.get("Assigned To") == "Unassigned":
                        if st.button("Accept", key=f"accept_{t.get('Task ID')}"):
                            t["Assigned To"] = st.session_state.current_user
                            t["Status"] = "In Progress"
                            st.session_state.last_assigned_task = t
                            st.experimental_rerun()
                    elif t.get("Assigned To") == st.session_state.current_user:
                        if t.get("Status") == "In Progress":
                            if st.button("Pause", key=f"pause_{t.get('Task ID')}"):
                                t["Status"] = "Paused"
                                st.experimental_rerun()
                        elif t.get("Status") == "Paused":
                            if st.button("Resume", key=f"resume_{t.get('Task ID')}"):
                                t["Status"] = "In Progress"
                                st.experimental_rerun()
                        if t.get("Status") != "Completed":
                            if st.button("Complete", key=f"complete_{t.get('Task ID')}"):
                                t["Status"] = "Completed"
                                t["Completed At"] = datetime.now()
                                st.experimental_rerun()

                with st.expander(f"Details for Task #{t.get('Task ID')}"):
                    st.write(f"**Title:** {t.get('Title', '')}")
                    st.write(f"**Company:** {t.get('Company', 'N/A')}")
                    st.write(f"**Priority:** {t.get('Priority', 'N/A')}")
                    st.write(f"**Status:** {t.get('Status', 'N/A')}")
                    st.write(f"**Assigned To:** {t.get('Assigned To', 'N/A')}")
                    st.write(f"**Created At:** {t.get('Created At', 'N/A')}")
                    st.write(f"**Due Date:** {t.get('Due Date', 'N/A')}")
                    st.write(f"**Completed At:** {t.get('Completed At', 'N/A')}")
                    st.write(f"**Department:** {t.get('Department', 'N/A')}")
                    st.write(f"**Source:** {t.get('Source', 'N/A')}")
                    st.write("**Description:**")
                    st.write(t.get("Description", ""))
                st.markdown("---")

# ======================================
# TAB: DATA IMPORT
# ======================================

with tab_import:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Email (.eml) Import")
    eml_files = st.file_uploader(
        "Upload .eml files", type=["eml"], accept_multiple_files=True, key="eml_uploader"
    )
    if eml_files:
        if st.button("Process Emails", type="primary"):
            ok = 0
            for f in eml_files:
                if import_task_from_eml(f):
                    ok += 1
            st.success(f"Created {ok} tasks from {len(eml_files)} emails.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Excel Task Import")
    excel_file = st.file_uploader(
        "Upload Excel file for tasks", type=["xlsx", "xls"], key="excel_uploader"
    )
    if excel_file:
        try:
            preview_df = pd.read_excel(excel_file)
            st.write("Preview of uploaded file:")
            st.dataframe(preview_df.head(), use_container_width=True)
        except Exception as e:
            st.error(f"Could not preview file: {e}")

        if st.button("Create Tasks from Excel", type="primary"):
            n = import_tasks_from_excel(excel_file)
            st.success(f"Created {n} tasks from Excel.")
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================
# TAB: ANALYTICS (TASKS)
# ======================================

with tab_analytics:
    df = tasks_df()
    if df.empty:
        st.info("No tasks yet. Import or create tasks first.")
    else:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Key Metrics")

        col1, col2, col3, col4, col5 = st.columns(5)
        total = len(df)
        completed = len(df[df["Status"] == "Completed"])
        in_prog = len(df[df["Status"] == "In Progress"])
        high = len(df[df["Priority"].isin(["Critical", "High"])])

        # robust overdue calc
        if "Due Date" in df.columns:
            due_series = pd.to_datetime(df["Due Date"], errors="coerce")
            overdue = len(
                df[(df["Status"] != "Completed") & (due_series.dt.date < date.today())]
            )
        else:
            overdue = 0

        with col1:
            st.metric("Total Tasks", total)
        with col2:
            st.metric("Completed", completed)
        with col3:
            st.metric("In Progress", in_prog)
        with col4:
            st.metric("High / Critical", high)
        with col5:
            st.metric("Overdue", overdue)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Distributions")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Status Distribution")
            st.bar_chart(df["Status"].value_counts())
        with col2:
            st.write("Priority Distribution")
            st.bar_chart(df["Priority"].value_counts())
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Tasks by Analyst")
        by_user = df.groupby("Assigned To")["Task ID"].count().sort_values(ascending=False)
        st.bar_chart(by_user)
        st.markdown("</div>", unsafe_allow_html=True)

# ======================================
# TAB: TEAM METRICS
# ======================================

with tab_team:
    df = tasks_df()
    if df.empty:
        st.info("No tasks yet.")
    else:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Per-Analyst Summary")

        rows = []
        for a in ANALYSTS:
            adf = df[df["Assigned To"] == a]
            if adf.empty:
                continue
            total = len(adf)
            completed = len(adf[adf["Status"] == "Completed"])
            in_prog = len(adf[adf["Status"] == "In Progress"])
            high = len(adf[adf["Priority"].isin(["Critical", "High"])]
                       )
            rows.append(
                {
                    "Analyst": a,
                    "Total Tasks": total,
                    "Completed": completed,
                    "In Progress": in_prog,
                    "High/Critical": high,
                    "Completion %": round(completed / total * 100, 1) if total else 0.0,
                }
            )
        team_df = pd.DataFrame(rows)
        st.dataframe(team_df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ======================================
# TAB: ACHIEVED / ARMS EXCEL
# ======================================

with tab_achieved:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Upload ARMS / Achieved Excel")

    achieved_file = st.file_uploader(
        "Upload ARMS Data workbook", type=["xlsx", "xls"], key="achieved_uploader"
    )
    if achieved_file:
        load_achieved_workbook(achieved_file)
    st.markdown("</div>", unsafe_allow_html=True)

    df = st.session_state.achieved_df
    if df is None:
        st.info("Upload your ARMS Excel to explore achieved / workflow data.")
    else:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader(f"Sheet: {st.session_state.achieved_sheet_name}")
        st.dataframe(df.head(50), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # detect columns
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        datetime_cols = df.select_dtypes(include="datetime").columns.tolist()
        # also treat columns with date/month in name as date-like
        for c in df.columns:
            cl = c.lower()
            if ("date" in cl or "month" in cl) and c not in datetime_cols:
                try:
                    df[c] = pd.to_datetime(df[c], errors="coerce")
                    datetime_cols.append(c)
                except Exception:
                    pass

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Quick KPI & Trend")

        if not numeric_cols:
            st.info("No numeric columns detected – cannot build KPIs.")
        else:
            metric_col = st.selectbox("Metric column", numeric_cols, key="metric_col")
            if datetime_cols:
                date_col = st.selectbox(
                    "Date column (optional)", ["(none)"] + datetime_cols, key="date_col"
                )
            else:
                date_col = "(none)"

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total", f"{df[metric_col].sum():,.1f}")
            with col2:
                st.metric("Average", f"{df[metric_col].mean():,.1f}")

            if date_col != "(none)":
                ddf = df.dropna(subset=[date_col])
                ddf = ddf.sort_values(date_col)
                ts = ddf.groupby(ddf[date_col].dt.date)[metric_col].sum()
                st.line_chart(ts)
        st.markdown("</div>", unsafe_allow_html=True)

        # category distribution
        cat_cols = [c for c in df.columns if df[c].dtype == "object"]
        if cat_cols and numeric_cols:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Category Breakdown")
            cat_col = st.selectbox("Group by", cat_cols, key="cat_col")
            metric_col2 = st.selectbox("Value", numeric_cols, key="metric_col2")
            agg = df.groupby(cat_col)[metric_col2].sum().sort_values(ascending=False)
            st.bar_chart(agg)
            st.markdown("</div>", unsafe_allow_html=True)

        # explorer + export
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Data Explorer & Export")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False)
        st.download_button(
            "Download full sheet as CSV",
            data=csv,
            file_name="arms_achieved_export.csv",
            mime="text/csv",
        )
        st.markdown("</div>", unsafe_allow_html=True)
