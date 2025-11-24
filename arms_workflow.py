import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import io
import base64
import time

# ======================================
# ENTERPRISE CONFIGURATION
# ======================================

st.set_page_config(
    page_title="ARMS Workflow Management",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Enterprise Styling
st.markdown("""
<style>
    /* Main Theme */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Enterprise Header */
    .enterprise-header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-bottom: 4px solid #2980b9;
    }
    
    /* Power BI-like Cards */
    .powerbi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e1e8ed;
        margin-bottom: 1rem;
    }
    
    /* Metric Cards */
    .metric-card-enterprise {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: 1px solid #2c3e50;
    }
    
    .metric-value-enterprise {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0.5rem 0;
    }
    
    .metric-label-enterprise {
        font-size: 0.9rem;
        color: #ecf0f1;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Status badges */
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
    .status-paused { background: #e2e3e5; color: #383d41; }
    
    .priority-critical { background: #f8d7da; color: #721c24; }
    .priority-high { background: #f8d7da; color: #721c24; }
    .priority-medium { background: #fff3cd; color: #856404; }
    .priority-low { background: #d1ecf1; color: #0c5460; }
    
    /* Login Styling */
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ======================================
# AUTHENTICATION SYSTEM
# ======================================

USERS = {
    "admin": {"password": "admin123", "role": "manager", "name": "System Administrator"},
    "nisarg": {"password": "nisarg123", "role": "analyst", "name": "Nisarg Thakker"},
    "komal": {"password": "komal123", "role": "analyst", "name": "Komal Khamar"},
    "ayushi": {"password": "ayushi123", "role": "analyst", "name": "Ayushi Chandel"},
    "jen": {"password": "jen123", "role": "analyst", "name": "Jen Shears"},
    "rondrea": {"password": "rondrea123", "role": "analyst", "name": "Rondrea Carroll"},
    "devanshi": {"password": "devanshi123", "role": "analyst", "name": "Devanshi Joshi"},
    "divyesh": {"password": "divyesh123", "role": "analyst", "name": "Divyesh Fofandi"},
    "parth": {"password": "parth123", "role": "analyst", "name": "Parth Chelani"},
    "prerna": {"password": "prerna123", "role": "analyst", "name": "Prerna Kesrani"},
    "ankit": {"password": "ankit123", "role": "analyst", "name": "Ankit Rawat"}
}

ANALYSTS = [
    "Nisarg Thakker", "Jen Shears", "Komal Khamar", "Rondrea Carroll", 
    "Devanshi Joshi", "Divyesh Fofandi", "Parth Chelani", "Prerna Kesrani", 
    "Ayushi Chandel", "Ankit Rawat"
]

def authenticate(username, password):
    if username in USERS and USERS[username]["password"] == password:
        return USERS[username]
    return None

def login_page():
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h1 style='color: #2c3e50; margin-bottom: 0.5rem;'>🚀 ARMS Workflow Management</h1>
        <p style='color: #7f8c8d; margin-bottom: 2rem;'>Enterprise Task Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.subheader("🔐 User Login")
            
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Login", use_container_width=True, type="primary"):
                    user = authenticate(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.current_user = username
                        st.session_state.user_role = user["role"]
                        st.session_state.user_name = user["name"]
                        st.success(f"Welcome {user['name']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            with col2:
                if st.button("Reset", use_container_width=True):
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Demo credentials
            with st.expander("Demo Credentials"):
                st.write("**Manager:** admin / admin123")
                st.write("**Analysts:** nisarg / nisarg123, komal / komal123, etc.")

# ======================================
# DATA MANAGEMENT
# ======================================

def initialize_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
        
    # Task management
    if "tasks" not in st.session_state:
        st.session_state.tasks = create_sample_tasks()
    if "next_task_id" not in st.session_state:
        st.session_state.next_task_id = 1280
        
    # Analytics data
    if "analytics_data" not in st.session_state:
        st.session_state.analytics_data = {}
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = {}

def create_sample_tasks():
    """Create realistic sample tasks with proper structure"""
    tasks = []
    
    # Sample data with proper structure
    sample_data = [
        {"Task_ID": 1270, "Task_Type": "Tier II", "Company_Name": "US Foods Holding Corp.", "Document_Type": "10-Q", "Priority": "High", "Status": "Under Review", "Tier1_Completed_Date_Time": "November 24, 2025 8:44 AM", "Assigned_User": "Ayushi Chandel"},
        {"Task_ID": 1269, "Task_Type": "Tier II", "Company_Name": "Medline Inc - PFE 2022", "Document_Type": "10-K", "Priority": "High", "Status": "Completed", "Tier1_Completed_Date_Time": "November 21, 2025 2:28 PM", "Assigned_User": "Komal Khamar"},
        {"Task_ID": 1268, "Task_Type": "Tier II", "Company_Name": "Medline Inc - 2Q", "Document_Type": "10-Q", "Priority": "High", "Status": "Completed", "Tier1_Completed_Date_Time": "November 21, 2025 2:20 PM", "Assigned_User": "Komal Khamar"},
        {"Task_ID": 1267, "Task_Type": "Tier II", "Company_Name": "Medline Inc - 2Q", "Document_Type": "10-Q", "Priority": "High", "Status": "Completed", "Tier1_Completed_Date_Time": "November 21, 2025 2:06 PM", "Assigned_User": "Komal Khamar"},
        {"Task_ID": 1266, "Task_Type": "Tier II", "Company_Name": "Medline Inc - PFE 2023", "Document_Type": "10-K", "Priority": "High", "Status": "Completed", "Tier1_Completed_Date_Time": "November 21, 2025 1:35 PM", "Assigned_User": "Komal Khamar"},
        {"Task_ID": 1265, "Task_Type": "Tier II", "Company_Name": "Medline Inc - PFE 2024", "Document_Type": "10-K", "Priority": "High", "Status": "Completed", "Tier1_Completed_Date_Time": "November 21, 2025 1:06 PM", "Assigned_User": "Komal Khamar"},
        {"Task_ID": 1264, "Task_Type": "Tier II", "Company_Name": "Soleno", "Document_Type": "10-K", "Priority": "High", "Status": "Completed", "Tier1_Completed_Date_Time": "November 21, 2025 1:16 AM", "Assigned_User": "Komal Khamar"},
        {"Task_ID": 1263, "Task_Type": "Tier II", "Company_Name": "Bath & Body Works, Inc.", "Document_Type": "10-Q", "Priority": "Low", "Status": "Completed", "Tier1_Completed_Date_Time": "November 21, 2025 6:04 AM", "Assigned_User": "Komal Khamar"},
        {"Task_ID": 1262, "Task_Type": "Tier II", "Company_Name": "Ace Hardware", "Document_Type": "10-Q", "Priority": "High", "Status": "Completed", "Tier1_Completed_Date_Time": "November 21, 2025 6:29 AM", "Assigned_User": "Komal Khamar"},
        {"Task_ID": 1261, "Task_Type": "Tier I", "Company_Name": "Medline Inc.", "Document_Type": "10-Q", "Priority": "High", "Status": "Completed", "Tier1_Completed_Date_Time": "November 21, 2025 6:14 AM", "Assigned_User": "Ayushi Chandel"},
    ]
    
    # Add pending tasks
    for i in range(15):
        tasks.append({
            "Task_ID": 1250 - i,
            "Task_Type": np.random.choice(["Tier I", "Tier II"]),
            "Company_Name": np.random.choice(["Apple Inc", "Microsoft Corp", "Google LLC", "Amazon Inc", "Tesla Inc"]),
            "Document_Type": np.random.choice(["10-Q", "10-K", "8-K"]),
            "Priority": np.random.choice(["High", "Medium", "Low"]),
            "Status": "Pending",
            "Tier1_Completed_Date_Time": "",
            "Assigned_User": "Unassigned"
        })
    
    tasks.extend(sample_data)
    return tasks

# ======================================
# TASK MANAGEMENT COMPONENTS
# ======================================

def get_next_task():
    """Get the next available task for the current user"""
    available_tasks = [task for task in st.session_state.tasks if task["Status"] == "Pending" and task["Assigned_User"] == "Unassigned"]
    if available_tasks:
        return available_tasks[0]
    return None

def assign_task_to_user(task_id, user):
    """Assign a task to a user"""
    for task in st.session_state.tasks:
        if task["Task_ID"] == task_id:
            task["Assigned_User"] = user
            task["Status"] = "In Progress"
            return True
    return False

def update_task_status(task_id, new_status):
    """Update task status"""
    for task in st.session_state.tasks:
        if task["Task_ID"] == task_id:
            task["Status"] = new_status
            if new_status == "Completed":
                task["Tier1_Completed_Date_Time"] = datetime.now().strftime("%B %d, %Y %I:%M %p")
            return True
    return False

def create_new_task(task_data):
    """Create a new task"""
    task_id = st.session_state.next_task_id
    st.session_state.next_task_id += 1
    
    task = {
        "Task_ID": task_id,
        **task_data
    }
    st.session_state.tasks.append(task)
    return task

def task_modal(task):
    """Display task details in a modal-like expander"""
    with st.expander(f"📋 Task #{task['Task_ID']} - {task['Company_Name']} - {task['Document_Type']}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Company:** {task['Company_Name']}")
            st.write(f"**Document Type:** {task['Document_Type']}")
            st.write(f"**Task Type:** {task['Task_Type']}")
            st.write(f"**Priority:** {task['Priority']}")
            
        with col2:
            st.write(f"**Status:** {task['Status']}")
            st.write(f"**Assigned To:** {task['Assigned_User']}")
            if task['Tier1_Completed_Date_Time']:
                st.write(f"**Completed:** {task['Tier1_Completed_Date_Time']}")
        
        # Task actions
        st.markdown("---")
        st.subheader("Task Actions")
        
        if task["Status"] == "In Progress" and task["Assigned_User"] == st.session_state.user_name:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("⏸️ Pause", key=f"pause_{task['Task_ID']}", use_container_width=True):
                    update_task_status(task["Task_ID"], "Paused")
                    st.rerun()
            
            with col2:
                if st.button("✅ Complete", key=f"complete_{task['Task_ID']}", use_container_width=True):
                    update_task_status(task["Task_ID"], "Completed")
                    st.rerun()
            
            with col3:
                if st.button("📤 Upload Files", key=f"upload_{task['Task_ID']}", use_container_width=True):
                    uploaded_file = st.file_uploader(f"Upload file for Task #{task['Task_ID']}", 
                                                   type=['pdf', 'doc', 'docx', 'xlsx', 'eml'],
                                                   key=f"file_upload_{task['Task_ID']}")
                    if uploaded_file:
                        st.success(f"File {uploaded_file.name} uploaded successfully!")
            
            with col4:
                if st.button("🔍 Send for Review", key=f"review_{task['Task_ID']}", use_container_width=True):
                    update_task_status(task["Task_ID"], "Under Review")
                    st.rerun()
        
        elif task["Status"] == "Paused" and task["Assigned_User"] == st.session_state.user_name:
            if st.button("▶️ Resume", key=f"resume_{task['Task_ID']}", use_container_width=True):
                update_task_status(task["Task_ID"], "In Progress")
                st.rerun()

# ======================================
# MAIN APPLICATION TABS
# ======================================

def tab_dashboard():
    """Dashboard with metrics and overview"""
    st.markdown("### 📊 Dashboard Overview")
    
    # Key Metrics
    total_tasks = len(st.session_state.tasks)
    pending_tasks = len([t for t in st.session_state.tasks if t["Status"] == "Pending"])
    my_tasks = len([t for t in st.session_state.tasks if t["Assigned_User"] == st.session_state.user_name and t["Status"] != "Completed"])
    completed_tasks = len([t for t in st.session_state.tasks if t["Status"] == "Completed"])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card-enterprise">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value-enterprise">{pending_tasks}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label-enterprise">Available Tasks</div>', unsafe_allow_html=True)
        
        # Get Next Task button
        next_task = get_next_task()
        if next_task and st.session_state.user_role == "analyst":
            if st.button("🚀 Get Next Task", key="get_next_dashboard", use_container_width=True):
                assign_task_to_user(next_task["Task_ID"], st.session_state.user_name)
                st.success(f"Task #{next_task['Task_ID']} assigned to you!")
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card-enterprise">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value-enterprise">{my_tasks}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label-enterprise">My Tasks</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card-enterprise">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value-enterprise">{total_tasks}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label-enterprise">Total Tasks</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card-enterprise">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value-enterprise">{completed_tasks}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label-enterprise">Completed</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent Activity - Fixed the KeyError
    st.markdown("### 📈 Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Task status distribution - Fixed with error handling
        if st.session_state.tasks:
            df = pd.DataFrame(st.session_state.tasks)
            if 'Status' in df.columns:
                status_counts = df["Status"].value_counts()
                fig = px.pie(values=status_counts.values, names=status_counts.index, 
                             title="Task Status Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No status data available for chart")
        else:
            st.info("No tasks available for analysis")
    
    with col2:
        # Priority distribution - Fixed with error handling
        if st.session_state.tasks:
            df = pd.DataFrame(st.session_state.tasks)
            if 'Priority' in df.columns:
                priority_counts = df["Priority"].value_counts()
                fig = px.bar(x=priority_counts.index, y=priority_counts.values,
                             title="Tasks by Priority", color=priority_counts.index)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No priority data available for chart")
        else:
            st.info("No tasks available for analysis")

def tab_task_management():
    """Task management with Get Next Task functionality"""
    st.markdown("### # My Task | All Task")
    st.markdown("#### Search Task Information")
    
    # Get Next Task functionality
    next_task = get_next_task()
    
    if next_task:
        st.markdown("---")
        st.markdown("### 🎯 Get Next Task")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**Task #{next_task['Task_ID']}** - {next_task['Company_Name']}")
            st.write(f"**Document Type:** {next_task['Document_Type']} | **Priority:** {next_task['Priority']}")
            st.write(f"**Task Type:** {next_task['Task_Type']}")
        
        with col2:
            if st.button("🚀 Accept This Task", use_container_width=True, type="primary"):
                assign_task_to_user(next_task["Task_ID"], st.session_state.user_name)
                st.success(f"Task #{next_task['Task_ID']} assigned to you!")
                st.rerun()
        
        st.markdown("---")
    
    # Task filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        view_option = st.selectbox("View", ["All Tasks", "My Tasks", "Pending", "In Progress", "Completed"])
    
    with col2:
        priority_filter = st.multiselect("Priority", ["Critical", "High", "Medium", "Low"], default=["Critical", "High", "Medium", "Low"])
    
    with col3:
        task_type_filter = st.multiselect("Task Type", ["Tier I", "Tier II"], default=["Tier I", "Tier II"])
    
    with col4:
        date_filter = st.date_input("Date Range", [date.today() - timedelta(days=30), date.today()])
    
    # Filter tasks
    filtered_tasks = st.session_state.tasks.copy()
    
    if view_option == "My Tasks":
        filtered_tasks = [t for t in filtered_tasks if t["Assigned_User"] == st.session_state.user_name]
    elif view_option == "Pending":
        filtered_tasks = [t for t in filtered_tasks if t["Status"] == "Pending"]
    elif view_option == "In Progress":
        filtered_tasks = [t for t in filtered_tasks if t["Status"] == "In Progress"]
    elif view_option == "Completed":
        filtered_tasks = [t for t in filtered_tasks if t["Status"] == "Completed"]
    
    filtered_tasks = [t for t in filtered_tasks if t["Priority"] in priority_filter and t["Task_Type"] in task_type_filter]
    
    # Display tasks
    st.markdown(f"#### {view_option} ({len(filtered_tasks)} tasks)")
    
    if not filtered_tasks:
        st.info("No tasks match the current filters.")
    else:
        for task in filtered_tasks:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.write(f"**#{task['Task_ID']}** - {task['Company_Name']}")
                    st.write(f"{task['Document_Type']} | {task['Task_Type']}")
                
                with col2:
                    st.write(f"**Assigned:** {task['Assigned_User']}")
                    if task['Tier1_Completed_Date_Time']:
                        st.write(f"**Completed:** {task['Tier1_Completed_Date_Time']}")
                
                with col3:
                    status_class = task['Status'].lower().replace(' ', '-')
                    st.markdown(f'<span class="status-badge status-{status_class}">{task["Status"]}</span>', unsafe_allow_html=True)
                
                with col4:
                    priority_class = task['Priority'].lower()
                    st.markdown(f'<span class="status-badge priority-{priority_class}">{task["Priority"]}</span>', unsafe_allow_html=True)
                
                # Task actions for unassigned tasks
                if task["Status"] == "Pending" and task["Assigned_User"] == "Unassigned":
                    if st.button("Accept", key=f"accept_{task['Task_ID']}"):
                        assign_task_to_user(task["Task_ID"], st.session_state.user_name)
                        st.rerun()
                
                # Task modal for details
                task_modal(task)
                st.markdown("---")
    
    # Manual Task Creation (for managers)
    if st.session_state.user_role == "manager":
        st.markdown("---")
        st.markdown("### ➕ Manual Task Creation")
        
        with st.form("create_task_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input("Company Name")
                document_type = st.selectbox("Document Type", ["10-Q", "10-K", "8-K", "Annual Report"])
                task_type = st.selectbox("Task Type", ["Tier I", "Tier II"])
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            
            with col2:
                assigned_user = st.selectbox("Assign To", ["Unassigned"] + ANALYSTS)
                description = st.text_area("Description")
            
            if st.form_submit_button("Create Task", type="primary"):
                if company_name:
                    task_data = {
                        "Task_Type": task_type,
                        "Company_Name": company_name,
                        "Document_Type": document_type,
                        "Priority": priority,
                        "Status": "Pending" if assigned_user == "Unassigned" else "In Progress",
                        "Tier1_Completed_Date_Time": "",
                        "Assigned_User": assigned_user
                    }
                    
                    task = create_new_task(task_data)
                    st.success(f"Task #{task['Task_ID']} created successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a company name")

def tab_analyst_performance():
    """Analyst performance tracking"""
    st.markdown("### 👥 Analyst Performance")
    
    # Calculate performance metrics
    performance_data = []
    
    for analyst in ANALYSTS:
        analyst_tasks = [t for t in st.session_state.tasks if t["Assigned_User"] == analyst]
        total_tasks = len(analyst_tasks)
        completed_tasks = len([t for t in analyst_tasks if t["Status"] == "Completed"])
        in_progress_tasks = len([t for t in analyst_tasks if t["Status"] == "In Progress"])
        pending_tasks = len([t for t in analyst_tasks if t["Status"] == "Pending"])
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        performance_data.append({
            "Analyst": analyst,
            "Total Tasks": total_tasks,
            "Completed": completed_tasks,
            "In Progress": in_progress_tasks,
            "Pending": pending_tasks,
            "Completion Rate": f"{completion_rate:.1f}%"
        })
    
    performance_df = pd.DataFrame(performance_data)
    
    # Display performance table
    st.dataframe(performance_df, use_container_width=True)
    
    # Performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Tasks by Analyst")
        fig = px.bar(performance_df, x='Analyst', y='Total Tasks', 
                     title='Total Tasks Assigned per Analyst')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Completion Rates")
        completion_df = performance_df.copy()
        completion_df['Completion Rate Num'] = completion_df['Completion Rate'].str.rstrip('%').astype('float')
        fig = px.bar(completion_df, x='Analyst', y='Completion Rate Num',
                     title='Completion Rate by Analyst')
        st.plotly_chart(fig, use_container_width=True)

def tab_advanced_analytics():
    """Advanced analytics with Excel upload"""
    st.markdown("### 📈 Advanced Analytics")
    
    # File upload section
    st.markdown("#### 📤 Upload Excel Data")
    
    uploaded_file = st.file_uploader("Upload Excel file with multiple sheets", 
                                   type=["xlsx", "xls"],
                                   help="Upload Excel files with multiple sheets for correlation analysis")
    
    if uploaded_file:
        try:
            # Read all sheets
            xl_file = pd.ExcelFile(uploaded_file)
            sheet_names = xl_file.sheet_names
            
            st.success(f"✅ File loaded with {len(sheet_names)} sheets: {', '.join(sheet_names)}")
            
            # Store data in session state
            st.session_state.analytics_data[uploaded_file.name] = {}
            
            # Sheet selection and preview
            selected_sheets = st.multiselect("Select sheets to analyze", sheet_names, default=sheet_names[:2])
            
            if selected_sheets:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Sheet Correlation")
                    
                    # Show basic info about selected sheets
                    for sheet_name in selected_sheets:
                        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                        st.session_state.analytics_data[uploaded_file.name][sheet_name] = df
                        
                        st.write(f"**{sheet_name}**: {len(df)} rows, {len(df.columns)} columns")
                
                with col2:
                    st.markdown("#### Data Preview")
                    preview_sheet = st.selectbox("Preview sheet", selected_sheets)
                    if preview_sheet:
                        df_preview = pd.read_excel(uploaded_file, sheet_name=preview_sheet)
                        st.dataframe(df_preview.head(10), use_container_width=True)
                
                # Basic analytics
                st.markdown("#### Basic Analytics")
                
                if len(selected_sheets) >= 2:
                    # Try to find common columns for correlation
                    common_analytics = {}
                    
                    for sheet_name in selected_sheets:
                        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                        numeric_cols = df.select_dtypes(include=[np.number]).columns
                        
                        if len(numeric_cols) > 0:
                            common_analytics[sheet_name] = {
                                'row_count': len(df),
                                'numeric_columns': len(numeric_cols),
                                'total_columns': len(df.columns),
                                'sample_data': df[numeric_cols].mean().to_dict()
                            }
                    
                    # Display analytics
                    if common_analytics:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Sheets Loaded", len(common_analytics))
                        
                        with col2:
                            total_rows = sum(data['row_count'] for data in common_analytics.values())
                            st.metric("Total Rows", f"{total_rows:,}")
                        
                        with col3:
                            total_columns = sum(data['total_columns'] for data in common_analytics.values())
                            st.metric("Total Columns", total_columns)
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    # .eml file upload
    st.markdown("---")
    st.markdown("#### 📧 Email (.eml) Import")
    
    eml_files = st.file_uploader("Upload .eml files", 
                                type=["eml"],
                                accept_multiple_files=True,
                                help="Upload .eml files to create tasks from emails")
    
    if eml_files:
        st.success(f"✅ {len(eml_files)} .eml file(s) uploaded successfully!")
        
        if st.button("Process Emails and Create Tasks"):
            for eml_file in eml_files:
                # Create task from email
                task_data = {
                    "Task_Type": "Tier II",
                    "Company_Name": f"Email: {eml_file.name}",
                    "Document_Type": "Email Processing",
                    "Priority": "Medium",
                    "Status": "Pending",
                    "Tier1_Completed_Date_Time": "",
                    "Assigned_User": "Unassigned"
                }
                
                task = create_new_task(task_data)
                st.success(f"Created Task #{task['Task_ID']} from {eml_file.name}")

def tab_workflow_setup():
    """Workflow setup and configuration"""
    st.markdown("### ⚙️ Workflow Setup")
    
    # Workflow configuration
    st.markdown("#### Workflow Configuration")
    
    with st.form("workflow_config"):
        col1, col2 = st.columns(2)
        
        with col1:
            workflow_name = st.text_input("Workflow Name")
            workflow_type = st.selectbox("Workflow Type", ["Pending", "UCC", "Judgements", "Chapter11", "Chapter7", "Trade Tapes"])
            target_metric = st.text_input("Target Metric")
            measurement_unit = st.text_input("Measurement Unit")
        
        with col2:
            monthly_target = st.text_input("Monthly Target")
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            sla_hours = st.number_input("SLA Hours", min_value=1, value=24)
            quality_required = st.selectbox("Quality Required?", ["Yes", "No"])
        
        data_points = st.text_area("Data Points (comma separated)", 
                                 placeholder="Enter required data points separated by commas")
        
        if st.form_submit_button("Save Workflow Configuration"):
            if workflow_name:
                st.success(f"Workflow '{workflow_name}' configured successfully!")
            else:
                st.error("Please enter a workflow name")
    
    # Pre-defined workflows based on your requirements
    st.markdown("#### Pre-defined Workflows")
    
    predefined_workflows = [
        {"Workflow Name": "Trades Tape Imports", "Workflow Type": "Volume", "Target Metric": "Completion %", 
         "Measurement Unit": "Batches", "Monthly Target": "100%", "Priority": "High", "SLA Hours": 24, "Quality Required?": "Yes"},
        {"Workflow Name": "Pending", "Workflow Type": "Volume", "Target Metric": "Completion %", 
         "Measurement Unit": "Items", "Monthly Target": "100%", "Priority": "High", "SLA Hours": 72, "Quality Required?": "Yes"},
        {"Workflow Name": "Placements", "Workflow Type": "Target", "Target Metric": "Placements", 
         "Measurement Unit": "Cases", "Monthly Target": "50", "Priority": "Medium", "SLA Hours": 72, "Quality Required?": "Yes"},
        {"Workflow Name": "Judgments", "Workflow Type": "Target", "Target Metric": "Accuracy %", 
         "Measurement Unit": "Judgments", "Monthly Target": "98%", "Priority": "Medium", "SLA Hours": 72, "Quality Required?": "Yes"},
        {"Workflow Name": "UCC", "Workflow Type": "Target", "Target Metric": "UCC Filings", 
         "Measurement Unit": "Filings", "Monthly Target": "30", "Priority": "Medium", "SLA Hours": 72, "Quality Required?": "Yes"},
    ]
    
    workflows_df = pd.DataFrame(predefined_workflows)
    st.dataframe(workflows_df, use_container_width=True)

# ======================================
# MAIN APPLICATION
# ======================================

def main_app():
    """Main application after login"""
    
    # Header
    st.markdown(f"""
    <div class="enterprise-header">
        <h1 style="margin:0; color:white;">🚀 ARMS Workflow Management System</h1>
        <p style="margin:0; opacity:0.9;">Welcome, {st.session_state.user_name} ({st.session_state.user_role.title()})</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    if st.session_state.user_role == "manager":
        tabs = st.tabs(["📊 Dashboard", "📋 Task Management", "👥 Analyst Performance", "📈 Advanced Analytics", "⚙️ Workflow Setup"])
    else:
        tabs = st.tabs(["📊 Dashboard", "📋 Task Management", "👥 Analyst Performance", "📈 Advanced Analytics"])
    
    # Tab content
    with tabs[0]:
        tab_dashboard()
    
    with tabs[1]:
        tab_task_management()
    
    with tabs[2]:
        tab_analyst_performance()
    
    with tabs[3]:
        tab_advanced_analytics()
    
    if st.session_state.user_role == "manager" and len(tabs) > 4:
        with tabs[4]:
            tab_workflow_setup()
    
    # Logout button
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.user_role = None
        st.session_state.user_name = None
        st.rerun()

# ======================================
# MAIN EXECUTION
# ======================================

def main():
    initialize_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
