import streamlit as st
import pandas as pd
from datetime import datetime
import random

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="ARMS Workflow Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================
# BASIC STYLING
# =========================
st.markdown(
    """
<style>
    /* Remove default Streamlit padding at the top */
    .block-container {
        padding-top: 0.5rem;
    }

    /* Top nav bar */
    .top-nav {
        background-color: #215a88;
        padding: 0.6rem 1.2rem;
        color: #ffffff;
    }
    .top-nav-title {
        font-size: 1.3rem;
        font-weight: 600;
        padding-left: 0.5rem;
    }
    .top-nav-tab {
        font-size: 0.95rem;
        font-weight: 500;
        padding: 0.4rem 0.8rem;
        border-radius: 4px;
        cursor: pointer;
        text-align: center;
    }
    .top-nav-tab-active {
        background-color: #ffffff;
        color: #215a88;
    }
    .top-nav-tab-inactive {
        color: #f1f5fb;
        border: 1px solid transparent;
    }

    .page-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #215a88;
        margin-top: 0.8rem;
        margin-bottom: 0.7rem;
    }

    /* Cards */
    .stat-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        border: 1px solid #d0d7e5;
        box-shadow: 0 1px 3px rgba(15,23,42,0.08);
    }
    .stat-label {
        font-size: 0.85rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .stat-value {
        font-size: 1.4rem;
        font-weight: 600;
        color: #0f172a;
        margin-top: 0.2rem;
        margin-bottom: 0.4rem;
    }
    .stat-button {
        font-size: 0.85rem;
    }

    /* Section separator */
    hr.section-divider {
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
        border-color: #e2e8f0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# SESSION STATE INIT
# =========================
if "active_page" not in st.session_state:
    st.session_state.active_page = "task"  # "task" or "report"

if "current_user" not in st.session_state:
    st.session_state.current_user = "Nisarg Thakker"

if "is_admin" not in st.session_state:
    st.session_state.is_admin = True

if "tasks" not in st.session_state:
    # seed with a couple of demo tasks
    st.session_state.tasks = [
        {
            "Task ID": 1001,
            "Title": "Medline Inc - 10-K",
            "Company": "Medline Inc.",
            "Priority": "High",
            "Status": "In Progress",
            "Created At": datetime(2025, 11, 21, 14, 15),
            "Assigned To": "Komal Khamar",
            "Source": "Manual",
        },
        {
            "Task ID": 1002,
            "Title": "US Foods FYE 2024 - 10-Q",
            "Company": "US Foods Holding Corp.",
            "Priority": "High",
            "Status": "Completed",
            "Created At": datetime(2025, 11, 21, 13, 5),
            "Assigned To": "Ayushi Chandel",
            "Source": "Manual",
        },
    ]

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1003

if "task_view" not in st.session_state:
    st.session_state.task_view = "my"  # "my" or "all"

# =========================
# HELPERS
# =========================
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

def create_task(
    title: str,
    company: str,
    priority: str,
    assigned_to: str,
    status: str = "New",
    source: str = "Manual",
) -> dict:
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
    if not st.session_state.tasks:
        return pd.DataFrame(
            columns=[
                "Task ID",
                "Title",
                "Company",
                "Priority",
                "Status",
                "Created At",
                "Assigned To",
                "Source",
            ]
        )
    df = pd.DataFrame(st.session_state.tasks)
    return df.sort_values("Created At", ascending=False)


# =========================
# TOP NAV BAR
# =========================
with st.container():
    st.markdown('<div class="top-nav">', unsafe_allow_html=True)
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([0.08, 0.35, 0.30, 0.27])

    with nav_col1:
        st.markdown("### 📊", unsafe_allow_html=True)
    with nav_col2:
        st.markdown(
            '<div class="top-nav-title">ARMS Workflow Management System</div>',
            unsafe_allow_html=True,
        )
    with nav_col3:
        c_task, c_report = st.columns(2)
        with c_task:
            if st.button(
                "TASK",
                key="nav_task",
            ):
                st.session_state.active_page = "task"
        with c_report:
            if st.button(
                "REPORT",
                key="nav_report",
            ):
                st.session_state.active_page = "report"

    with nav_col4:
        user = st.selectbox(
            "User",
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

# =========================
# TASK PAGE
# =========================
def render_task_page():
    st.markdown('<div class="page-header">Task Workspace</div>', unsafe_allow_html=True)

    df_all = get_tasks_df()
    my_df = df_all[df_all["Assigned To"] == st.session_state.current_user]

    # ---- cards row ----
    c1, c2, c3, c4 = st.columns([0.9, 0.9, 0.9, 0.7])

    with c1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Get New Task</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="stat-value">{len(df_all[df_all["Status"]=="New"])}</div>',
            unsafe_allow_html=True,
        )
        get_new_clicked = st.button("Get New Task", key="btn_get_new")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">My Tasks</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="stat-value">{len(my_df)}</div>', unsafe_allow_html=True
        )
        if st.button("View My Tasks", key="btn_my_tasks"):
            st.session_state.task_view = "my"
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">All Tasks</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="stat-value">{len(df_all)}</div>', unsafe_allow_html=True
        )
        if st.button("View All Tasks", key="btn_all_tasks"):
            st.session_state.task_view = "all"
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Create</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-value">+</div>', unsafe_allow_html=True)
        show_create = st.button("Create Task", key="btn_create_task")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Get New Task behaviour ----
    if get_new_clicked:
        # For now: generate a placeholder task. Later we’ll link to mailbox/workbook.
        auto_title = f"Auto Task #{st.session_state.next_task_id}"
        auto_company = random.choice(
            ["US Foods Holding Corp.", "Medline Inc.", "Sodexo", "Ace Hardware"]
        )
        auto_priority = random.choice(PRIORITIES)
        new_task = create_task(
            title=auto_title,
            company=auto_company,
            priority=auto_priority,
            assigned_to=st.session_state.current_user,
            status="In Progress",
            source="Get New Task",
        )

        st.success(
            f"New task assigned to you: **{new_task['Title']}** "
            f"(ID: {new_task['Task ID']}, Priority: {new_task['Priority']})"
        )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ---- Create Task form ----
    if show_create and st.session_state.is_admin:
        with st.form("create_task_form"):
            st.subheader("Create Task")

            col_a, col_b = st.columns(2)
            with col_a:
                title = st.text_input("Task Title")
                company = st.text_input("Company Name")
                priority = st.selectbox("Priority", PRIORITIES, index=2)
            with col_b:
                assigned = st.selectbox(
                    "Assign To",
                    USERS,
                    index=USERS.index(st.session_state.current_user)
                    if st.session_state.current_user in USERS
                    else 0,
                )
                status = st.selectbox("Status", STATUSES, index=0)

            desc = st.text_area("Short Summary / Notes", height=80)
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                submitted = st.form_submit_button("Save Task")
            with col_s2:
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
                    f"Task **{new_task['Task ID']} - {new_task['Title']}** created and assigned to **{assigned}**."
                )
            elif submitted and not title.strip():
                st.error("Task Title is required.")
    elif show_create and not st.session_state.is_admin:
        st.warning("Only admin users can create tasks.")

    # ---- Task Tables ----
    if st.session_state.task_view == "my":
        st.subheader(f"My Tasks – {st.session_state.current_user}")
        if my_df.empty:
            st.info("You have no tasks yet.")
        else:
            st.dataframe(my_df, use_container_width=True)
    else:
        st.subheader("All Tasks")
        if df_all.empty:
            st.info("No tasks available.")
        else:
            st.dataframe(df_all, use_container_width=True)


# =========================
# REPORT PAGE
# =========================
def render_report_page():
    st.markdown(
        '<div class="page-header">Reports & Analytics</div>', unsafe_allow_html=True
    )

    df_all = get_tasks_df()
    if df_all.empty:
        st.info("No tasks yet. Create or get tasks from the Task page.")
        return

    # ---- High level metrics ----
    total_tasks = len(df_all)
    completed = len(df_all[df_all["Status"] == "Completed"])
    in_progress = len(df_all[df_all["Status"] == "In Progress"])
    new_tasks = len(df_all[df_all["Status"] == "New"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Tasks", total_tasks)
    with c2:
        st.metric("In Progress", in_progress)
    with c3:
        st.metric("Completed", completed)
    with c4:
        st.metric("New", new_tasks)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ---- Tasks by user ----
    st.subheader("Tasks by Assigned User")
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

    # ---- Raw table ----
    st.subheader("Task Detail (for export / validation)")
    st.dataframe(df_all, use_container_width=True)


# =========================
# ROUTER
# =========================
if st.session_state.active_page == "task":
    render_task_page()
else:
    render_report_page()
