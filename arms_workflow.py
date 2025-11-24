import streamlit as st
import pandas as pd
from datetime import datetime, date
import random

from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime

# ======================================
# PAGE CONFIG
# ======================================

st.set_page_config(
    page_title="ARMS Workflow Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ======================================
# BASIC STYLING (TOP BAR + CARDS)
# ======================================

st.markdown(
    """
<style>
    .block-container {
        padding-top: 0.4rem;
    }
    /* Top navigation bar */
    .top-nav {
        background-color: #215a88;
        padding: 0.5rem 1rem;
        color: #ffffff;
    }
    .top-nav-title {
        font-size: 1.2rem;
        font-weight: 600;
        padding-left: 0.5rem;
    }
    .page-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #215a88;
        margin-top: 0.8rem;
        margin-bottom: 0.6rem;
    }
    .stat-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        border: 1px solid #d0d7e5;
        box-shadow: 0 1px 3px rgba(15,23,42,0.08);
    }
    .stat-label {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .stat-value {
        font-size: 1.3rem;
        font-weight: 600;
        color: #0f172a;
        margin-top: 0.15rem;
        margin-bottom: 0.4rem;
    }
    hr.section-divider {
        margin-top: 1rem;
        margin-bottom: 0.7rem;
        border-color: #e2e8f0;
    }
    .task-summary-box {
        background-color: #f8fafc;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        padding: 0.8rem 1rem;
        margin-bottom: 0.8rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ======================================
# SESSION STATE INIT
# ======================================

USERS = [
    "Nisarg Thakker",
    "Jen Shears",
    "Komal Khamar",
    "Janet Yanatos",
    "Rondrea Carroll",
    "Devanshi Joshi",
    "Divyesh Fofandi",
    "Parth Chelani",
    "Prerna Kesrani",
]

PRIORITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = ["New", "In Progress", "Completed"]

if "active_page" not in st.session_state:
    st.session_state.active_page = "task"   # "task" or "report"

if "current_user" not in st.session_state:
    st.session_state.current_user = "Nisarg Thakker"

if "is_admin" not in st.session_state:
    st.session_state.is_admin = True

if "tasks" not in st.session_state:
    st.session_state.tasks = []  # list of dicts; each has "Created At"

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1001

if "task_view" not in st.session_state:
    st.session_state.task_view = "my"  # "my" or "all"

if "show_create_form" not in st.session_state:
    st.session_state.show_create_form = False

if "last_assigned_task" not in st.session_state:
    st.session_state.last_assigned_task = None

# for preventing duplicate imports
if "imported_task_files" not in st.session_state:
    st.session_state.imported_task_files = set()

# analytics workbook
if "analytics_sheets" not in st.session_state:
    st.session_state.analytics_sheets = {}   # name -> df

if "analytics_selected_sheet" not in st.session_state:
    st.session_state.analytics_selected_sheet = None

if "report_start_date" not in st.session_state:
    st.session_state.report_start_date = None
if "report_end_date" not in st.session_state:
    st.session_state.report_end_date = None


# ======================================
# HELPERS
# ======================================

def create_task(title, company, priority, assigned_to,
                status="New", source="Manual") -> dict:
    """Create a task and append it to session_state.tasks."""
    task_id = st.session_state.next_task_id
    st.session_state.next_task_id += 1
    task = {
        "Task ID": task_id,
        "Title": title,
        "Company": company,
        "Priority": priority,
        "Status": status,
        "Created At": datetime.now(),
        "Assigned To": assigned_to,
        "Source": source,
    }
    st.session_state.tasks.append(task)
    return task


def get_tasks_df() -> pd.DataFrame:
    """Return tasks as DataFrame, sorted by Created At if present."""
    if not st.session_state.tasks:
        cols = [
            "Task ID",
            "Title",
            "Company",
            "Priority",
            "Status",
            "Created At",
            "Assigned To",
            "Source",
        ]
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(st.session_state.tasks)
    if "Created At" in df.columns:
        return df.sort_values("Created At", ascending=False)
    return df


def import_tasks_from_excel(file):
    """Create tasks from Excel/CSV upload. One row = one task."""
    name = file.name
    if name in st.session_state.imported_task_files:
        return 0

    if name.lower().endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    df.columns = [c.strip() for c in df.columns]
    count = 0
    for _, row in df.iterrows():
        # Try to guess fields
        title = (
            row.get("Title")
            or row.get("Task Title")
            or row.get("task_name")
            or f"Imported Task {st.session_state.next_task_id}"
        )
        company = row.get("Company") or row.get("Company Name") or "N/A"
        priority = row.get("Priority") or "Medium"
        if priority not in PRIORITIES:
            priority = "Medium"

        assigned = row.get("Assigned To") or row.get("Analyst") or "Unassigned"
        if assigned not in USERS:
            assigned = "Unassigned"

        status = row.get("Status") or "New"
        if status not in STATUSES:
            status = "New"

        t = create_task(
            title=str(title),
            company=str(company),
            priority=priority,
            assigned_to=assigned,
            status=status,
            source=f"Excel:{name}",
        )

        # if there is a date column, use it as Created At
        for col in df.columns:
            if "date" in col.lower():
                try:
                    dt = pd.to_datetime(row[col], errors="coerce")
                    if pd.notna(dt):
                        t["Created At"] = dt.to_pydatetime()
                except Exception:
                    pass
                break

        count += 1

    st.session_state.imported_task_files.add(name)
    return count


def import_tasks_from_eml(files):
    """Create tasks from .eml files."""
    created = 0
    for file in files:
        name = file.name
        if name in st.session_state.imported_task_files:
            continue

        try:
            raw = file.read()
            msg = BytesParser(policy=policy.default).parsebytes(raw)
            subject = msg["subject"] or "No subject"
            requestor = msg["from"] or "Unknown"

            try:
                received = (
                    parsedate_to_datetime(msg["date"])
                    if msg["date"]
                    else datetime.now()
                )
            except Exception:
                received = datetime.now()

            # create as New task, unassigned
            t = create_task(
                title=f"Email: {subject}",
                company=str(requestor),
                priority="Medium",
                assigned_to="Unassigned",
                status="New",
                source=f"Email:{name}",
            )
            t["Created At"] = received
            created += 1
            st.session_state.imported_task_files.add(name)
        except Exception:
            continue

    return created


def load_analytics_workbook(file):
    """Load workbook into analytics_sheets dict."""
    xls = pd.ExcelFile(file)
    sheets = {}
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        df.columns = [c.strip() for c in df.columns]
        # try to parse date columns
        for col in df.columns:
            if "date" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                except Exception:
                    pass
        sheets[sheet_name] = df
    st.session_state.analytics_sheets = sheets
    if sheets and st.session_state.analytics_selected_sheet not in sheets:
        st.session_state.analytics_selected_sheet = list(sheets.keys())[0]


# ======================================
# TOP NAV BAR (NO SIDEBAR)
# ======================================

with st.container():
    st.markdown('<div class="top-nav">', unsafe_allow_html=True)
    nav1, nav2, nav3, nav4 = st.columns([0.08, 0.30, 0.25, 0.37])

    with nav1:
        st.markdown("### 📊", unsafe_allow_html=True)

    with nav2:
        st.markdown(
            '<div class="top-nav-title">ARMS Workflow Management System</div>',
            unsafe_allow_html=True,
        )

    with nav3:
        col_task, col_report = st.columns(2)
        with col_task:
            if st.button("TASK", key="nav_task"):
                st.session_state.active_page = "task"
        with col_report:
            if st.button("REPORT", key="nav_report"):
                st.session_state.active_page = "report"

    with nav4:
        user = st.selectbox(
            "Analyst",
            USERS,
            index=USERS.index(st.session_state.current_user)
            if st.session_state.current_user in USERS
            else 0,
        )
        st.session_state.current_user = user
        st.session_state.is_admin = user in [
            "Nisarg Thakker",
            "Jen Shears",
            "Komal Khamar",
            "Janet Yanatos",
        ]
    st.markdown("</div>", unsafe_allow_html=True)


# ======================================
# TASK PAGE
# ======================================

def render_task_page():
    st.markdown('<div class="page-header">Task Workspace</div>', unsafe_allow_html=True)

    # ----------------- IMPORT ZONE -----------------
    st.markdown("#### Data & Task Import")

    imp1, imp2, imp3 = st.columns(3)

    with imp1:
        task_file = st.file_uploader(
            "Upload Task Excel/CSV",
            type=["xlsx", "xls", "csv"],
            key="task_excel_upload",
        )
        if task_file is not None:
            num = import_tasks_from_excel(task_file)
            if num > 0:
                st.success(f"Imported {num} task(s) from {task_file.name}")

    with imp2:
        eml_files = st.file_uploader(
            "Upload Email (.eml) for Tasks",
            type=["eml"],
            accept_multiple_files=True,
            key="eml_upload",
        )
        if eml_files:
            num = import_tasks_from_eml(eml_files)
            if num > 0:
                st.success(f"Created {num} task(s) from email files")

    with imp3:
        analytics_file = st.file_uploader(
            "Upload Achieved/ARMS Excel (for reports)",
            type=["xlsx", "xls"],
            key="analytics_upload",
        )
        if analytics_file is not None:
            load_analytics_workbook(analytics_file)
            st.success(f"Loaded workbook '{analytics_file.name}' for analytics")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ----------------- CARDS ROW -----------------
    df_all = get_tasks_df()
    my_df = df_all[df_all["Assigned To"] == st.session_state.current_user]

    col1, col2, col3, col4 = st.columns([0.9, 0.9, 0.9, 0.7])

    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Get New Task</div>', unsafe_allow_html=True)
        new_count = len(df_all[df_all["Status"] == "New"])
        st.markdown(
            f'<div class="stat-value">{new_count}</div>', unsafe_allow_html=True
        )
        btn_get_new = st.button("Get New Task", key="btn_get_new")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">My Tasks</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="stat-value">{len(my_df)}</div>', unsafe_allow_html=True
        )
        if st.button("View My Tasks", key="btn_my_tasks"):
            st.session_state.task_view = "my"
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Total Tasks</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="stat-value">{len(df_all)}</div>', unsafe_allow_html=True
        )
        if st.button("View All Tasks", key="btn_all_tasks"):
            st.session_state.task_view = "all"
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Create</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-value">+</div>', unsafe_allow_html=True)
        create_clicked = st.button("Create Task", key="btn_create_task")
        st.markdown("</div>", unsafe_allow_html=True)

    # --------- Get New Task action + Task Summary ---------
    if btn_get_new:
        # find first New & Unassigned task, else New for anyone, else create dummy
        candidate_df = df_all[df_all["Status"] == "New"]
        cand_unassigned = candidate_df[candidate_df["Assigned To"] == "Unassigned"]
        chosen_row = None
        if not cand_unassigned.empty:
            chosen_row = cand_unassigned.iloc[0]
        elif not candidate_df.empty:
            chosen_row = candidate_df.iloc[0]

        if chosen_row is not None:
            # update task in original list
            tid = chosen_row["Task ID"]
            for t in st.session_state.tasks:
                if t["Task ID"] == tid:
                    t["Assigned To"] = st.session_state.current_user
                    t["Status"] = "In Progress"
                    st.session_state.last_assigned_task = t
                    break
            st.success(
                f"Task {tid} assigned to you: {chosen_row['Title']} "
                f"(Priority: {chosen_row['Priority']})"
            )
        else:
            # no existing "New" tasks → create a placeholder and assign
            dummy_title = f"Auto Task {st.session_state.next_task_id}"
            dummy_company = random.choice(
                ["US Foods Holding Corp.", "Medline Inc.", "Sodexo", "Ace Hardware"]
            )
            dummy_priority = random.choice(PRIORITIES)
            new_task = create_task(
                title=dummy_title,
                company=dummy_company,
                priority=dummy_priority,
                assigned_to=st.session_state.current_user,
                status="In Progress",
                source="Get New Task",
            )
            st.session_state.last_assigned_task = new_task
            st.success(
                f"New auto task created and assigned: {new_task['Title']} "
                f"(ID: {new_task['Task ID']}, Priority: {new_task['Priority']})"
            )

    # Show last assigned task summary if available
    if st.session_state.last_assigned_task:
        t = st.session_state.last_assigned_task
        st.markdown("#### Latest Assigned Task Summary")
        with st.container():
            st.markdown('<div class="task-summary-box">', unsafe_allow_html=True)
            st.write(f"**Task ID:** {t['Task ID']}")
            st.write(f"**Title:** {t['Title']}")
            st.write(f"**Company:** {t['Company']}")
            st.write(f"**Priority:** {t['Priority']}")
            st.write(f"**Status:** {t['Status']}")
            st.write(f"**Assigned To:** {t['Assigned To']}")
            st.write(
                f"**Created At:** {t['Created At'].strftime('%Y-%m-%d %H:%M:%S')}"
                if isinstance(t["Created At"], datetime)
                else f"**Created At:** {t['Created At']}"
            )
            st.write(f"**Source:** {t['Source']}")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # --------- Create Task form ---------
    if create_clicked:
        st.session_state.show_create_form = True

    if st.session_state.show_create_form:
        with st.form("create_task_form"):
            st.subheader("Create Task")

            cA, cB = st.columns(2)
            with cA:
                title = st.text_input("Task Title")
                company = st.text_input("Company Name")
                priority = st.selectbox("Priority", PRIORITIES, index=2)
            with cB:
                assigned = st.selectbox(
                    "Assign To",
                    USERS + ["Unassigned"],
                    index=USERS.index(st.session_state.current_user)
                    if st.session_state.current_user in USERS
                    else len(USERS),
                )
                status = st.selectbox("Status", STATUSES, index=0)

            notes = st.text_area("Short Summary / Notes (optional)", height=80)
            f1, f2 = st.columns(2)
            with f1:
                submitted = st.form_submit_button("Save Task")
            with f2:
                cancelled = st.form_submit_button("Cancel")

            if submitted and title.strip():
                new_task = create_task(
                    title=title.strip(),
                    company=company.strip() or "N/A",
                    priority=priority,
                    assigned_to=assigned,
                    status=status,
                    source="Manual",
                )
                st.success(
                    f"Task {new_task['Task ID']} - {new_task['Title']} created and "
                    f"assigned to {assigned}."
                )
                st.session_state.show_create_form = False
            elif submitted and not title.strip():
                st.error("Task Title is required.")
            elif cancelled:
                st.session_state.show_create_form = False

    # --------- Task tables (My / All) ---------
    df_all = get_tasks_df()
    my_df = df_all[df_all["Assigned To"] == st.session_state.current_user]

    if st.session_state.task_view == "my":
        st.subheader(f"My Tasks – {st.session_state.current_user}")
        if my_df.empty:
            st.info("You have no tasks yet.")
        else:
            st.dataframe(my_df, use_container_width=True)
    else:
        st.subheader("Total Tasks (All Analysts)")
        if df_all.empty:
            st.info("No tasks available. Use Create Task or imports above.")
        else:
            st.dataframe(df_all, use_container_width=True)


# ======================================
# REPORT PAGE (Analytics)
# ======================================

def render_report_page():
    st.markdown('<div class="page-header">Reports & Analytics</div>', unsafe_allow_html=True)

    df_all = get_tasks_df()
    if df_all.empty:
        st.info("No tasks yet. Create or import tasks from the Task page.")
    else:
        # ---- Date filter for tasks ----
        if "Created At" in df_all.columns:
            df_all["Created At"] = pd.to_datetime(df_all["Created At"], errors="coerce")
            min_d = df_all["Created At"].min()
            max_d = df_all["Created At"].max()
            if pd.notna(min_d) and pd.notna(max_d):
                if st.session_state.report_start_date is None:
                    st.session_state.report_start_date = min_d.date()
                if st.session_state.report_end_date is None:
                    st.session_state.report_end_date = max_d.date()

                start_date, end_date = st.date_input(
                    "Task Created Date Range",
                    [
                        st.session_state.report_start_date,
                        st.session_state.report_end_date,
                    ],
                )
                if isinstance(start_date, date) and isinstance(end_date, date):
                    st.session_state.report_start_date = start_date
                    st.session_state.report_end_date = end_date
                    mask = (df_all["Created At"].dt.date >= start_date) & (
                        df_all["Created At"].dt.date <= end_date
                    )
                    df_all = df_all[mask]

        # ---- High level metrics ----
        total_tasks = len(df_all)
        completed = len(df_all[df_all["Status"] == "Completed"])
        in_progress = len(df_all[df_all["Status"] == "In Progress"])
        new_tasks = len(df_all[df_all["Status"] == "New"])

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Tasks", total_tasks)
        with m2:
            st.metric("In Progress", in_progress)
        with m3:
            st.metric("Completed", completed)
        with m4:
            st.metric("New", new_tasks)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # ---- Tasks by analyst ----
        st.subheader("Tasks by Analyst")
        by_user = (
            df_all.groupby("Assigned To")[["Task ID"]]
            .count()
            .rename(columns={"Task ID": "Task Count"})
            .sort_values("Task Count", ascending=False)
        )
        st.bar_chart(by_user)

        # ---- Tasks by priority ----
        st.subheader("Tasks by Priority")
        by_priority = (
            df_all.groupby("Priority")[["Task ID"]]
            .count()
            .rename(columns={"Task ID": "Task Count"})
            .sort_values("Task Count", ascending=False)
        )
        st.bar_chart(by_priority)

        # ---- Raw table for export ----
        st.subheader("Task Detail (filtered)")
        st.dataframe(df_all, use_container_width=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # --------- Achieved / ARMS Excel visual ---------
    st.subheader("Achieved Data – Excel Visualization")

    sheets = st.session_state.analytics_sheets
    if not sheets:
        st.info("Upload your achieved ARMS Excel on the Task page to visualize it here.")
        return

    sheet_names = list(sheets.keys())
    sheet_choice = st.selectbox(
        "Select sheet from uploaded workbook", sheet_names,
        index=sheet_names.index(st.session_state.analytics_selected_sheet)
        if st.session_state.analytics_selected_sheet in sheet_names
        else 0,
    )
    st.session_state.analytics_selected_sheet = sheet_choice
    sdf = sheets[sheet_choice].copy()

    st.write(f"**Preview – {sheet_choice}**")
    st.dataframe(sdf.head(50), use_container_width=True)

    # Try to detect date column
    date_cols = [c for c in sdf.columns if "date" in c.lower()]
    metric_cols = [
        c
        for c in sdf.columns
        if pd.to_numeric(sdf[c], errors="coerce").notna().any()
    ]

    if date_cols and metric_cols:
        dcol = st.selectbox("Date column", date_cols)
        mcol = st.selectbox("Metric column", metric_cols)

        sdf[dcol] = pd.to_datetime(sdf[dcol], errors="coerce")
        sdf_filtered = sdf[~sdf[dcol].isna()].copy()

        # date range
        dmin = sdf_filtered[dcol].min()
        dmax = sdf_filtered[dcol].max()
        sd, ed = st.date_input(
            "Achieved data date range",
            [dmin.date(), dmax.date()],
            key="achieved_date_range",
        )
        if isinstance(sd, date) and isinstance(ed, date):
            mask = (sdf_filtered[dcol].dt.date >= sd) & (
                sdf_filtered[dcol].dt.date <= ed
            )
            sdf_filtered = sdf_filtered[mask]

        group_by = st.selectbox(
            "Group by (optional)",
            ["(none)"] + [c for c in sdf.columns if c not in [dcol, mcol]],
        )

        if group_by == "(none)":
            val = pd.to_numeric(sdf_filtered[mcol], errors="coerce").sum()
            st.metric(f"Sum of {mcol}", f"{val:,.2f}")
        else:
            agg = (
                sdf_filtered.groupby(group_by)[mcol]
                .sum(numeric_only=True)
                .reset_index()
            )
            st.write(f"Sum of **{mcol}** by **{group_by}**")
            st.dataframe(agg, use_container_width=True)

    else:
        st.info(
            "Couldn’t automatically find both a date column and a numeric column "
            "in this sheet. You can still inspect it in the table above."
        )


# ======================================
# ROUTING
# ======================================

if st.session_state.active_page == "task":
    render_task_page()
else:
    render_report_page()
