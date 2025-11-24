import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import io
import base64

# ======================================
# ENTERPRISE CONFIGURATION
# ======================================

st.set_page_config(
    page_title="ARMS Workflow Management",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .task-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #3498db;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-pending { background: #fff3cd; color: #856404; }
    .status-in-progress { background: #d1ecf1; color: #0c5460; }
    .status-completed { background: #d4edda; color: #155724; }
    .status-under-review { background: #f8d7da; color: #721c24; }
    .priority-high { background: #f8d7da; color: #721c24; }
    .priority-medium { background: #fff3cd; color: #856404; }
    .priority-low { background: #d1ecf1; color: #0c5460; }
</style>
""", unsafe_allow_html=True)

# ======================================
# DATA MANAGEMENT
# ======================================

ANALYSTS = [
    "Nisarg Thakker", "Jen Shears", "Komal Khamar", "Janet Yanatos", 
    "Rondrea Carroll", "Devanshi Joshi", "Divyesh Fofandi", "Parth Chelani", 
    "Prerna Kesrani", "Ayushi Chandel", "Ankit Rawat"
]

WORKFLOWS_CONFIG = {
    "Pending": {
        "columns": ["Subscriber", "Import Date", "File Date", "Imported By", "Total Pending", "Reviewed", "Notes"]
    },
    "UCC": {
        "columns": ["filing_1_filing_type", "collateral_desc", "credit_file_status", "notesPublic", "filing_jurisdiction", "Date IND Format", "dateEntered", "secured_1_orig_name"]
    },
    "Judgements": {
        "columns": ["Filing_Number", "Filing_Date", "Date IND Format", "Release_Date", "Filing_Agency", "Amount", "Filing_Category", "Creditor_Name", "Debtor_Name_1", "Debtor_Name_2", "Filling_County"]
    },
    "Chapter11": {
        "columns": ["Company Name", "Chapter", "City", "State", "petitionlink", "Case Number", "Date IND Format", "Date Filed", "Industries"]
    },
    "Chapter7": {
        "columns": ["Company Name", "Chapter", "City", "State", "petitionlink", "Case Number", "Date IND Format", "Date Filed", "Industries"]
    },
    "Trade Tapes": {
        "columns": ["Client", "Balances", "Sent Via", "File ETA", "Oct 2025 Submission", "Sep 2025 Submission", "Aug 2025 Submission", "Last Submission Date", "Oct 2025", "Sep 2025", "Aug 2025", "Jul 2025", "Jun 2025", "May 2025", "Apr 2025", "Mar 2025", "Feb 2025", "Jan 2025", "Dec 2024", "Nov 2024"]
    },
    "Analyst Data": {
        "columns": ["source_file", "Team Member", "merge_timestamp", "Date", "Ad Hoc", "Target Qty", "Achieved Qty", "Remarks", "Rating", "Delivered on Time?", "Workflow", "Status"]
    },
    "Data Lake": {
        "columns": ["team_member", "month_year", "total_work_units", "bankruptcy_days", "ucc_actions", "credit_files_actions", "trade_references_actions", "trades_tape_actions", "pending_actions", "placements_actions", "judgments_actions", "tnt_actions", "search_pending", "search_credit_files", "search_other", "working_days"]
    }
}

WORKFLOW_TARGETS = [
    {"Workflow Name": "Trades Tape Imports", "Workflow Type": "Volume", "Target Metric": "Completion %", "Measurement Unit": "Batches", "Monthly Target": "100%", "Priority": "High", "SLA Hours": 24, "Quality Required?": "Yes"},
    {"Workflow Name": "Pending", "Workflow Type": "Volume", "Target Metric": "Completion %", "Measurement Unit": "Items", "Monthly Target": "100%", "Priority": "High", "SLA Hours": 72, "Quality Required?": "Yes"},
    {"Workflow Name": "Placements", "Workflow Type": "Target", "Target Metric": "Placements", "Measurement Unit": "Cases", "Monthly Target": 50, "Priority": "Medium", "SLA Hours": 72, "Quality Required?": "Yes"},
    {"Workflow Name": "Judgments", "Workflow Type": "Target", "Target Metric": "Accuracy %", "Measurement Unit": "Judgments", "Monthly Target": "98%", "Priority": "Medium", "SLA Hours": 72, "Quality Required?": "Yes"},
    {"Workflow Name": "UCC", "Workflow Type": "Target", "Target Metric": "UCC Filings", "Measurement Unit": "Filings", "Monthly Target": 30, "Priority": "Medium", "SLA Hours": 72, "Quality Required?": "Yes"},
    {"Workflow Name": "Credit Files", "Workflow Type": "Target", "Target Metric": "Files", "Measurement Unit": "Files", "Monthly Target": 150, "Priority": "Low", "SLA Hours": 72, "Quality Required?": "Yes"},
    {"Workflow Name": "Ch 11", "Workflow Type": "Quality", "Target Metric": "Timeliness %", "Measurement Unit": "Cases", "Monthly Target": "95%", "Priority": "Critical", "SLA Hours": 24, "Quality Required?": "Yes"},
    {"Workflow Name": "Ch 7", "Workflow Type": "Quality", "Target Metric": "Timeliness %", "Measurement Unit": "Cases", "Monthly Target": "95%", "Priority": "Critical", "SLA Hours": 24, "Quality Required?": "Yes"},
    {"Workflow Name": "Trade References", "Workflow Type": "Volume", "Target Metric": "Processing %", "Measurement Unit": "References", "Monthly Target": "100%", "Priority": "High", "SLA Hours": 48, "Quality Required?": "Yes"},
    {"Workflow Name": "Credit File Audits", "Workflow Type": "Quality", "Target Metric": "Compliance %", "Measurement Unit": "Audits", "Monthly Target": "100%", "Priority": "Medium", "SLA Hours": 72, "Quality Required?": "Yes"}
]

def initialize_session_state():
    if 'tasks' not in st.session_state:
        st.session_state.tasks = create_sample_tasks()
    if 'current_user' not in st.session_state:
        st.session_state.current_user = "Nisarg Thakker"
    if 'workflows' not in st.session_state:
        st.session_state.workflows = WORKFLOW_TARGETS.copy()
    if 'analytics_data' not in st.session_state:
        st.session_state.analytics_data = {}
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}

def create_sample_tasks():
    """Create realistic sample tasks based on the provided data"""
    tasks = []
    
    sample_data = [
        {"Task ID": 1270, "Task Type": "Tier II", "Company Name": "US Foods Holding Corp.", "Document Type": "10-Q", "Priority": "High", "Status": "Under Review", "Tier1 Completed Date Time": "November 24, 2025 8:44 AM", "Assigned User": "Ayushi Chandel"},
        {"Task ID": 1269, "Task Type": "Tier II", "Company Name": "Medline Inc - PFE 2022", "Document Type": "10-K", "Priority": "High", "Status": "Completed", "Tier1 Completed Date Time": "November 21, 2025 2:28 PM", "Assigned User": "Komal Khamar"},
        {"Task ID": 1268, "Task Type": "Tier II", "Company Name": "Medline Inc - 2Q", "Document Type": "10-Q", "Priority": "High", "Status": "Completed", "Tier1 Completed Date Time": "November 21, 2025 2:20 PM", "Assigned User": "Komal Khamar"},
        {"Task ID": 1267, "Task Type": "Tier II", "Company Name": "Medline Inc - 2Q", "Document Type": "10-Q", "Priority": "High", "Status": "Completed", "Tier1 Completed Date Time": "November 21, 2025 2:06 PM", "Assigned User": "Komal Khamar"},
        {"Task ID": 1266, "Task Type": "Tier II", "Company Name": "Medline Inc - PFE 2023", "Document Type": "10-K", "Priority": "High", "Status": "Completed", "Tier1 Completed Date Time": "November 21, 2025 1:35 PM", "Assigned User": "Komal Khamar"},
        {"Task ID": 1265, "Task Type": "Tier II", "Company Name": "Medline Inc - PFE 2024", "Document Type": "10-K", "Priority": "High", "Status": "Completed", "Tier1 Completed Date Time": "November 21, 2025 1:06 PM", "Assigned User": "Komal Khamar"},
        {"Task ID": 1264, "Task Type": "Tier II", "Company Name": "Soleno", "Document Type": "10-K", "Priority": "High", "Status": "Completed", "Tier1 Completed Date Time": "November 21, 2025 1:16 AM", "Assigned User": "Komal Khamar"},
        {"Task ID": 1263, "Task Type": "Tier II", "Company Name": "Bath & Body Works, Inc.", "Document Type": "10-Q", "Priority": "Low", "Status": "Completed", "Tier1 Completed Date Time": "November 21, 2025 6:04 AM", "Assigned User": "Komal Khamar"},
        {"Task ID": 1262, "Task Type": "Tier II", "Company Name": "Ace Hardware", "Document Type": "10-Q", "Priority": "High", "Status": "Completed", "Tier1 Completed Date Time": "November 21, 2025 6:29 AM", "Assigned User": "Komal Khamar"},
        {"Task ID": 1261, "Task Type": "Tier I", "Company Name": "Medline Inc.", "Document Type": "10-Q", "Priority": "High", "Status": "Completed", "Tier1 Completed Date Time": "November 21, 2025 6:14 AM", "Assigned User": "Ayushi Chandel"},
    ]
    
    # Add some pending tasks
    for i in range(10):
        tasks.append({
            "Task ID": 1250 - i,
            "Task Type": np.random.choice(["Tier I", "Tier II"]),
            "Company Name": np.random.choice(["Apple Inc", "Microsoft Corp", "Google LLC", "Amazon Inc", "Tesla Inc"]),
            "Document Type": np.random.choice(["10-Q", "10-K", "8-K"]),
            "Priority": np.random.choice(["High", "Medium", "Low"]),
            "Status": "Pending",
            "Tier1 Completed Date Time": "",
            "Assigned User": "Unassigned"
        })
    
    tasks.extend(sample_data)
    return tasks

# ======================================
# TASK MANAGEMENT COMPONENTS
# ======================================

def get_next_task():
    """Get the next available task for the current user"""
    available_tasks = [task for task in st.session_state.tasks if task["Status"] == "Pending" and task["Assigned User"] == "Unassigned"]
    if available_tasks:
        return available_tasks[0]
    return None

def assign_task_to_user(task_id, user):
    """Assign a task to a user"""
    for task in st.session_state.tasks:
        if task["Task ID"] == task_id:
            task["Assigned User"] = user
            task["Status"] = "In Progress"
            return True
    return False

def update_task_status(task_id, new_status):
    """Update task status"""
    for task in st.session_state.tasks:
        if task["Task ID"] == task_id:
            task["Status"] = new_status
            if new_status == "Completed":
                task["Tier1 Completed Date Time"] = datetime.now().strftime("%B %d, %Y %I:%M %p")
            return True
    return False

def task_modal(task):
    """Display task details in a modal-like expander"""
    with st.expander(f"Task #{task['Task ID']} - {task['Company Name']} - {task['Document Type']}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Company:** {task['Company Name']}")
            st.write(f"**Document Type:** {task['Document Type']}")
            st.write(f"**Task Type:** {task['Task Type']}")
            st.write(f"**Priority:** {task['Priority']}")
            
        with col2:
            st.write(f"**Status:** {task['Status']}")
            st.write(f"**Assigned To:** {task['Assigned User']}")
            if task['Tier1 Completed Date Time']:
                st.write(f"**Completed:** {task['Tier1 Completed Date Time']}")
        
        # Task actions
        st.markdown("---")
        st.subheader("Task Actions")
        
        if task["Status"] == "In Progress" and task["Assigned User"] == st.session_state.current_user:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("⏸️ Pause", key=f"pause_{task['Task ID']}"):
                    update_task_status(task["Task ID"], "Paused")
                    st.rerun()
            
            with col2:
                if st.button("✅ Complete", key=f"complete_{task['Task ID']}"):
                    update_task_status(task["Task ID"], "Completed")
                    st.rerun()
            
            with col3:
                if st.button("📤 Upload Files", key=f"upload_{task['Task ID']}"):
                    st.info("File upload functionality would be implemented here")
            
            with col4:
                if st.button("🔍 Send for Review", key=f"review_{task['Task ID']}"):
                    update_task_status(task["Task ID"], "Under Review")
                    st.rerun()
        
        elif task["Status"] == "Paused" and task["Assigned User"] == st.session_state.current_user:
            if st.button("▶️ Resume", key=f"resume_{task['Task ID']}"):
                update_task_status(task["Task ID"], "In Progress")
                st.rerun()

# ======================================
# ANALYTICS COMPONENTS
# ======================================

def process_uploaded_excel(uploaded_file):
    """Process uploaded Excel file with multiple sheets"""
    try:
        xl_file = pd.ExcelFile(uploaded_file)
        sheet_data = {}
        
        for sheet_name in xl_file.sheet_names:
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            sheet_data[sheet_name] = df
            
        st.session_state.analytics_data = sheet_data
        st.session_state.uploaded_files[uploaded_file.name] = sheet_data
        return True
        
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return False

def create_workflow_analytics():
    """Create comprehensive analytics dashboard"""
    
    if not st.session_state.analytics_data:
        st.info("Please upload an Excel file with workflow data in the Analytics tab.")
        return
    
    st.markdown("### 📊 Workflow Analytics Dashboard")
    
    # Sheet selection
    sheet_names = list(st.session_state.analytics_data.keys())
    selected_sheet = st.selectbox("Select Sheet for Analysis", sheet_names)
    
    if selected_sheet:
        df = st.session_state.analytics_data[selected_sheet]
        
        # Basic metrics
        st.markdown("#### 📈 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(df))
        
        with col2:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                st.metric("Numeric Columns", len(numeric_cols))
            else:
                st.metric("Data Columns", len(df.columns))
        
        with col3:
            missing_values = df.isnull().sum().sum()
            st.metric("Missing Values", missing_values)
        
        with col4:
            memory_usage = f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
            st.metric("Memory Usage", memory_usage)
        
        # Data preview
        st.markdown("#### 👀 Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Basic charts for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            st.markdown("#### 📊 Basic Visualizations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Correlation heatmap
                st.write("Correlation Matrix")
                corr_matrix = df[numeric_cols].corr()
                fig = px.imshow(corr_matrix, title="Feature Correlations")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Distribution of first numeric column
                if len(numeric_cols) > 0:
                    st.write(f"Distribution of {numeric_cols[0]}")
                    fig = px.histogram(df, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
                    st.plotly_chart(fig, use_container_width=True)

# ======================================
# WORKFLOW MANAGEMENT
# ======================================

def workflow_management():
    """Manage workflow configurations"""
    st.markdown("### 🔧 Workflow Management")
    
    # Display current workflows
    st.markdown("#### Current Workflows")
    workflows_df = pd.DataFrame(st.session_state.workflows)
    st.dataframe(workflows_df, use_container_width=True)
    
    # Add new workflow
    st.markdown("#### Add New Workflow")
    
    with st.form("add_workflow_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            workflow_name = st.text_input("Workflow Name")
            workflow_type = st.selectbox("Workflow Type", ["Volume", "Target", "Quality", "Compliance"])
            target_metric = st.text_input("Target Metric")
            
        with col2:
            measurement_unit = st.text_input("Measurement Unit")
            monthly_target = st.text_input("Monthly Target")
            priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"])
            sla_hours = st.number_input("SLA Hours", min_value=1, max_value=168, value=24)
            quality_required = st.selectbox("Quality Required?", ["Yes", "No"])
        
        if st.form_submit_button("Add Workflow"):
            if workflow_name:
                new_workflow = {
                    "Workflow Name": workflow_name,
                    "Workflow Type": workflow_type,
                    "Target Metric": target_metric,
                    "Measurement Unit": measurement_unit,
                    "Monthly Target": monthly_target,
                    "Priority": priority,
                    "SLA Hours": sla_hours,
                    "Quality Required?": quality_required
                }
                st.session_state.workflows.append(new_workflow)
                st.success(f"Workflow '{workflow_name}' added successfully!")
                st.rerun()
            else:
                st.error("Please enter a workflow name")

# ======================================
# MAIN APPLICATION
# ======================================

def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; color:white;">🚀 ARMS Workflow Management System</h1>
        <p style="margin:0; opacity:0.9;">Enterprise Task Management & Analytics Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**Current User:** {st.session_state.current_user}")
    with col2:
        if st.button("Switch User"):
            st.session_state.current_user = st.selectbox("Select User", ANALYSTS)
            st.rerun()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Task Management", "👥 Analyst Performance", "📈 Advanced Analytics", "🔧 Workflow Management"])
    
    # ======================================
    # TASK MANAGEMENT TAB
    # ======================================
    with tab1:
        st.markdown("### # My Task | All Task")
        st.markdown("#### Search Task Information")
        
        # Task metrics
        col1, col2, col3, col4 = st.columns(4)
        
        my_tasks = [task for task in st.session_state.tasks if task["Assigned User"] == st.session_state.current_user and task["Status"] != "Completed"]
        available_tasks = [task for task in st.session_state.tasks if task["Status"] == "Pending" and task["Assigned User"] == "Unassigned"]
        total_tasks = len(st.session_state.tasks)
        completed_tasks = len([task for task in st.session_state.tasks if task["Status"] == "Completed"])
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 2rem; font-weight: bold;">{len(available_tasks)}</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.9rem;">Get New Task</div>', unsafe_allow_html=True)
            
            next_task = get_next_task()
            if next_task and st.button("Get Next Task", use_container_width=True):
                assign_task_to_user(next_task["Task ID"], st.session_state.current_user)
                st.success(f"Task #{next_task['Task ID']} assigned to you!")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 2rem; font-weight: bold;">{len(my_tasks)}</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.9rem;">My Tasks</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 2rem; font-weight: bold;">{total_tasks}</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.9rem;">Total Tasks</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 2rem; font-weight: bold;">{completed_tasks}</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.9rem;">Completed</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Task view selection
        view_option = st.radio("View:", ["My Tasks", "All Tasks", "Available Tasks"], horizontal=True)
        
        # Filter tasks based on selection
        if view_option == "My Tasks":
            display_tasks = my_tasks
        elif view_option == "Available Tasks":
            display_tasks = available_tasks
        else:
            display_tasks = st.session_state.tasks
        
        # Display tasks
        st.markdown("#### Task List")
        
        if not display_tasks:
            st.info("No tasks found for the selected view.")
        else:
            for task in display_tasks:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**#{task['Task ID']}** - {task['Company Name']}")
                        st.write(f"{task['Document Type']} | {task['Task Type']}")
                    
                    with col2:
                        st.write(f"**Assigned:** {task['Assigned User']}")
                        if task['Tier1 Completed Date Time']:
                            st.write(f"**Completed:** {task['Tier1 Completed Date Time']}")
                    
                    with col3:
                        status_class = task['Status'].lower().replace(' ', '-')
                        st.markdown(f'<span class="status-badge status-{status_class}">{task["Status"]}</span>', unsafe_allow_html=True)
                    
                    with col4:
                        priority_class = task['Priority'].lower()
                        st.markdown(f'<span class="status-badge priority-{priority_class}">{task["Priority"]}</span>', unsafe_allow_html=True)
                    
                    # Task actions
                    if task["Status"] == "Pending" and task["Assigned User"] == "Unassigned":
                        if st.button("Accept", key=f"accept_{task['Task ID']}"):
                            assign_task_to_user(task["Task ID"], st.session_state.current_user)
                            st.rerun()
                    
                    # Task modal for details
                    task_modal(task)
                    st.markdown("---")
    
    # ======================================
    # ANALYST PERFORMANCE TAB
    # ======================================
    with tab2:
        st.markdown("### 👥 Analyst Performance")
        
        # Analyst workload
        st.markdown("#### Analyst Workload")
        
        analyst_workload = []
        for analyst in ANALYSTS:
            tasks_count = len([task for task in st.session_state.tasks if task["Assigned User"] == analyst])
            completed_count = len([task for task in st.session_state.tasks if task["Assigned User"] == analyst and task["Status"] == "Completed"])
            in_progress_count = len([task for task in st.session_state.tasks if task["Assigned User"] == analyst and task["Status"] == "In Progress"])
            
            analyst_workload.append({
                "Analyst": analyst,
                "Total Tasks": tasks_count,
                "Completed": completed_count,
                "In Progress": in_progress_count,
                "Completion Rate": f"{(completed_count/tasks_count*100):.1f}%" if tasks_count > 0 else "0%"
            })
        
        workload_df = pd.DataFrame(analyst_workload)
        st.dataframe(workload_df, use_container_width=True)
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Tasks by Analyst")
            fig = px.bar(workload_df, x='Analyst', y='Total Tasks', title='Total Tasks Assigned')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Completion Rates")
            completion_rates = workload_df.copy()
            completion_rates['Completion Rate Num'] = completion_rates['Completion Rate'].str.rstrip('%').astype('float')
            fig = px.bar(completion_rates, x='Analyst', y='Completion Rate Num', title='Completion Rate by Analyst')
            st.plotly_chart(fig, use_container_width=True)
    
    # ======================================
    # ADVANCED ANALYTICS TAB
    # ======================================
    with tab3:
        st.markdown("### 📈 Advanced Analytics")
        
        # File upload
        st.markdown("#### Upload Data for Analytics")
        uploaded_file = st.file_uploader("Upload Excel file with workflow data", type=["xlsx", "xls"])
        
        if uploaded_file:
            if st.button("Process Excel File"):
                if process_uploaded_excel(uploaded_file):
                    st.success(f"File '{uploaded_file.name}' processed successfully!")
                else:
                    st.error("Failed to process the file")
        
        # Show analytics if data is available
        if st.session_state.analytics_data:
            create_workflow_analytics()
        else:
            st.info("Please upload an Excel file to see analytics.")
    
    # ======================================
    # WORKFLOW MANAGEMENT TAB
    # ======================================
    with tab4:
        workflow_management()

if __name__ == "__main__":
    main()
