import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import base64
import io
import time
import hashlib
import json

# ======================================
# PAGE CONFIG & STYLING
# ======================================

st.set_page_config(
    page_title="ARMS Enterprise Workflow",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Appian-like styling
st.markdown("""
<style>
    /* Main container */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header */
    .enterprise-header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 0px;
        margin-bottom: 0rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-bottom: 4px solid #2980b9;
    }
    
    /* Cards */
    .enterprise-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #3498db;
        margin-bottom: 1rem;
        border: 1px solid #e1e8ed;
    }
    
    /* Metrics */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        text-align: center;
        border-top: 4px solid #3498db;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #2980b9 0%, #21618c 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
    }
    
    /* Status badges */
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-new { background: #e3f2fd; color: #1976d2; }
    .status-in-progress { background: #fff3e0; color: #f57c00; }
    .status-paused { background: #f5f5f5; color: #616161; }
    .status-completed { background: #e8f5e8; color: #388e3c; }
    
    /* Priority badges */
    .priority-critical { background: #ffebee; color: #d32f2f; }
    .priority-high { background: #fce4ec; color: #c2185b; }
    .priority-medium { background: #fff3e0; color: #ef6c00; }
    .priority-low { background: #e8f5e8; color: #388e3c; }
    
    /* Tables */
    .dataframe {
        border: 1px solid #e1e8ed;
        border-radius: 8px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0px 0px;
        gap: 1rem;
        padding: 1rem 2rem;
        font-weight: 600;
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
    "ayushi": {"password": "ayushi123", "role": "analyst", "name": "Ayushi Chandel"}
}

ANALYSTS = ["Nisarg Thakker", "Komal Khamar", "Ayushi Chandel", "Jen Shears", "Janet Yanatos"]

def authenticate(username, password):
    if username in USERS and USERS[username]["password"] == password:
        return USERS[username]
    return None

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
        st.session_state.tasks = []
    if "next_task_id" not in st.session_state:
        st.session_state.next_task_id = 1001
        
    # Analytics data
    if "analytics_data" not in st.session_state:
        st.session_state.analytics_data = {}
    if "current_sheet" not in st.session_state:
        st.session_state.current_sheet = None

def login_page():
    st.markdown('<div class="enterprise-header"><h1 style="margin:0; color:white;">🚀 ARMS Enterprise Workflow System</h1><p style="margin:0; opacity:0.9;">Secure Workflow Management Platform</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container():
            st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
            st.subheader("🔐 User Login")
            
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Login", use_container_width=True):
                    user = authenticate(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.current_user = username
                        st.session_state.user_role = user["role"]
                        st.session_state.user_name = user["name"]
                        st.success(f"Welcome {user['name']}!")
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
                st.write("**Analysts:** nisarg / nisarg123, komal / komal123, ayushi / ayushi123")

# ======================================
# TASK MANAGEMENT SYSTEM
# ======================================

def create_sample_tasks():
    """Create realistic sample tasks"""
    companies = ["US Foods Holding Corp.", "Medline Inc.", "Sodexo", "Bath & Body Works, Inc.", "Ace Hardware"]
    doc_types = ["10-Q", "10-K", "8-K", "Annual Report", "Filing"]
    departments = ["Finance", "Legal", "Compliance", "Operations", "Risk Management"]
    
    sample_tasks = []
    for i in range(20):
        task_id = 1000 + i
        company = np.random.choice(companies)
        doc_type = np.random.choice(doc_types)
        priority = np.random.choice(["Critical", "High", "Medium", "Low"], p=[0.1, 0.3, 0.4, 0.2])
        
        # Create realistic task titles
        if doc_type in ["10-Q", "10-K"]:
            title = f"{company} - {doc_type} Filing Review"
        else:
            title = f"{company} - {doc_type} Processing"
            
        status = np.random.choice(["New", "In Progress", "Completed", "Paused"], p=[0.3, 0.3, 0.3, 0.1])
        
        # Assign tasks realistically
        if status == "New":
            assigned_to = "Unassigned"
        else:
            assigned_to = np.random.choice(ANALYSTS)
            
        created_date = datetime.now() - timedelta(days=np.random.randint(1, 30))
        due_date = created_date + timedelta(days=np.random.randint(1, 14))
        
        task = {
            "Task ID": task_id,
            "Title": title,
            "Company": company,
            "Document Type": doc_type,
            "Priority": priority,
            "Status": status,
            "Assigned To": assigned_to,
            "Created Date": created_date,
            "Due Date": due_date,
            "Completed Date": due_date - timedelta(days=1) if status == "Completed" else None,
            "Department": np.random.choice(departments),
            "Description": f"Review and process {doc_type} filing for {company}. Ensure compliance with regulatory requirements.",
            "Source": "Manual",
            "Attachments": []
        }
        sample_tasks.append(task)
    
    return sample_tasks

def create_task(task_data):
    """Create a new task"""
    task_id = st.session_state.next_task_id
    st.session_state.next_task_id += 1
    
    task = {
        "Task ID": task_id,
        **task_data
    }
    st.session_state.tasks.append(task)
    return task

def update_task_status(task_id, new_status, assigned_to=None):
    """Update task status and assignment"""
    for task in st.session_state.tasks:
        if task["Task ID"] == task_id:
            task["Status"] = new_status
            if assigned_to:
                task["Assigned To"] = assigned_to
            if new_status == "Completed":
                task["Completed Date"] = datetime.now()
            return True
    return False

def get_user_tasks(user_name):
    """Get tasks assigned to specific user"""
    return [task for task in st.session_state.tasks if task["Assigned To"] == user_name]

def get_available_tasks():
    """Get unassigned new tasks"""
    return [task for task in st.session_state.tasks if task["Status"] == "New" and task["Assigned To"] == "Unassigned"]

# ======================================
# EMAIL INTEGRATION
# ======================================

def process_email_file(uploaded_file):
    """Process uploaded .eml file and create task"""
    try:
        # For .eml processing, we'll create a simple task without full email parsing
        task_data = {
            "Title": f"Email Task: {uploaded_file.name}",
            "Company": "Email Import",
            "Document Type": "Email Processing",
            "Priority": "Medium",
            "Status": "New",
            "Assigned To": "Unassigned",
            "Created Date": datetime.now(),
            "Due Date": datetime.now() + timedelta(days=3),
            "Completed Date": None,
            "Department": "Operations",
            "Description": f"Task created from email file: {uploaded_file.name}",
            "Source": "Email",
            "Attachments": [{
                "filename": uploaded_file.name,
                "content": uploaded_file.getvalue()
            }]
        }
        
        task = create_task(task_data)
        return task
        
    except Exception as e:
        st.error(f"Error processing email: {str(e)}")
        return None

# ======================================
# EXCEL PROCESSING
# ======================================

def process_task_excel(uploaded_file):
    """Process Excel file for task creation"""
    try:
        df = pd.read_excel(uploaded_file)
        tasks_created = 0
        
        for _, row in df.iterrows():
            # Map columns to task fields
            title = row.get('Title') or row.get('Task Title') or f"Task from Excel {st.session_state.next_task_id}"
            company = row.get('Company') or row.get('Company Name') or 'N/A'
            doc_type = row.get('Document Type') or row.get('Type') or 'General'
            priority = row.get('Priority') or 'Medium'
            department = row.get('Department') or 'Operations'
            
            task_data = {
                "Title": str(title),
                "Company": str(company),
                "Document Type": str(doc_type),
                "Priority": priority,
                "Status": "New",
                "Assigned To": "Unassigned",
                "Created Date": datetime.now(),
                "Due Date": datetime.now() + timedelta(days=7),
                "Completed Date": None,
                "Department": str(department),
                "Description": f"Task created from Excel import: {title}",
                "Source": f"Excel: {uploaded_file.name}",
                "Attachments": []
            }
            
            create_task(task_data)
            tasks_created += 1
            
        return tasks_created
        
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return 0

def process_analytics_excel(uploaded_file):
    """Process Excel file for analytics dashboard"""
    try:
        xl_file = pd.ExcelFile(uploaded_file)
        sheet_data = {}
        
        for sheet_name in xl_file.sheet_names:
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            sheet_data[sheet_name] = df
            
        st.session_state.analytics_data = sheet_data
        return True
        
    except Exception as e:
        st.error(f"Error processing analytics Excel: {str(e)}")
        return False

# ======================================
# DASHBOARD & ANALYTICS
# ======================================

def create_analytics_dashboard(df, selected_columns):
    """Create Power BI-like dashboard"""
    
    st.markdown("### 📊 Interactive Analytics Dashboard")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    date_columns = [col for col in selected_columns if pd.api.types.is_datetime64_any_dtype(df[col])]
    category_columns = [col for col in selected_columns if df[col].dtype == 'object']
    value_columns = [col for col in selected_columns if pd.api.types.is_numeric_dtype(df[col])]
    
    with col1:
        if date_columns:
            date_col = st.selectbox("Date Column", date_columns)
        else:
            date_col = None
    
    with col2:
        if category_columns:
            category_col = st.selectbox("Category Column", category_columns)
        else:
            category_col = None
    
    with col3:
        if value_columns:
            value_col = st.selectbox("Value Column", value_columns)
        else:
            value_col = None
    
    # Charts
    if value_columns:
        col1, col2 = st.columns(2)
        
        with col1:
            if category_col and value_col:
                # Bar chart
                chart_data = df.groupby(category_col)[value_col].sum().reset_index()
                fig = px.bar(chart_data, x=category_col, y=value_col, 
                           title=f"{value_col} by {category_col}")
                st.plotly_chart(fig, use_container_width=True)
            
            # Pie chart
            if category_col and len(df[category_col].unique()) <= 10:
                pie_data = df[category_col].value_counts()
                fig = px.pie(values=pie_data.values, names=pie_data.index,
                           title=f"Distribution by {category_col}")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if date_col and value_col:
                # Time series
                time_data = df.groupby(date_col)[value_col].sum().reset_index()
                fig = px.line(time_data, x=date_col, y=value_col,
                            title=f"{value_col} Trend Over Time")
                st.plotly_chart(fig, use_container_width=True)
            
            # Scatter plot
            if len(value_columns) >= 2:
                scatter_col1, scatter_col2 = st.columns(2)
                with scatter_col1:
                    x_val = st.selectbox("X-Axis", value_columns, key="scatter_x")
                with scatter_col2:
                    y_val = st.selectbox("Y-Axis", value_columns, key="scatter_y")
                
                if category_columns:
                    color_col = st.selectbox("Color by", [None] + category_columns, key="scatter_color")
                else:
                    color_col = None
                    
                fig = px.scatter(df, x=x_val, y=y_val, color=color_col,
                               title=f"{y_val} vs {x_val}")
                st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.markdown("### Data Preview")
    st.dataframe(df[selected_columns].head(100), use_container_width=True)

# ======================================
# MAIN APPLICATION
# ======================================

def main_app():
    """Main application after login"""
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="enterprise-header"><h1 style="margin:0; color:white;">🚀 ARMS Enterprise Workflow</h1><p style="margin:0; opacity:0.9;">Welcome, {st.session_state.user_name} ({st.session_state.user_role.title()})</p></div>', unsafe_allow_html=True)
    with col2:
        st.write("")  # Spacer
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.user_role = None
            st.session_state.user_name = None
            st.rerun()
    
    # Initialize sample data if empty
    if not st.session_state.tasks:
        st.session_state.tasks = create_sample_tasks()
        st.session_state.next_task_id = 1021
    
    # Navigation
    if st.session_state.user_role == "manager":
        tabs = st.tabs(["📋 Task Management", "📊 Analytics Dashboard", "👥 Team Management", "📁 Data Import"])
    else:
        tabs = st.tabs(["📋 My Tasks", "📊 Analytics", "📁 Data Import"])
    
    # ======================================
    # TASK MANAGEMENT TAB
    # ======================================
    with tabs[0]:
        st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
        st.header("📋 Task Management")
        
        # Task metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_tasks = len(st.session_state.tasks)
        my_tasks = len(get_user_tasks(st.session_state.user_name))
        available_tasks = len(get_available_tasks())
        completed_tasks = len([t for t in st.session_state.tasks if t["Status"] == "Completed"])
        critical_tasks = len([t for t in st.session_state.tasks if t["Priority"] == "Critical"])
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{available_tasks}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Available Tasks</div>', unsafe_allow_html=True)
            
            if available_tasks > 0 and st.session_state.user_role == "analyst":
                if st.button("Get New Task", key="get_new_btn", use_container_width=True):
                    available = get_available_tasks()
                    if available:
                        task = available[0]
                        update_task_status(task["Task ID"], "In Progress", st.session_state.user_name)
                        st.success(f"Task #{task['Task ID']} assigned to you!")
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{my_tasks}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">My Tasks</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{total_tasks}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Tasks</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{completed_tasks}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Completed</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col5:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{critical_tasks}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Critical</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Task creation for managers
        if st.session_state.user_role == "manager":
            st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
            st.subheader("Create New Task")
            
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Task Title")
                company = st.text_input("Company Name")
                doc_type = st.selectbox("Document Type", ["10-Q", "10-K", "8-K", "Annual Report", "Filing", "Review"])
                priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"])
                
            with col2:
                assigned_to = st.selectbox("Assign To", ["Unassigned"] + ANALYSTS)
                department = st.selectbox("Department", ["Finance", "Legal", "Compliance", "Operations", "Risk Management"])
                due_date = st.date_input("Due Date", value=date.today() + timedelta(days=7))
                
            description = st.text_area("Description", height=100)
            
            if st.button("Create Task", type="primary"):
                if title:
                    task_data = {
                        "Title": title,
                        "Company": company,
                        "Document Type": doc_type,
                        "Priority": priority,
                        "Status": "New" if assigned_to == "Unassigned" else "In Progress",
                        "Assigned To": assigned_to,
                        "Created Date": datetime.now(),
                        "Due Date": due_date,
                        "Completed Date": None,
                        "Department": department,
                        "Description": description,
                        "Source": "Manual",
                        "Attachments": []
                    }
                    
                    task = create_task(task_data)
                    st.success(f"Task #{task['Task ID']} created successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a task title")
                    
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Task list
        st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
        st.subheader("Task List")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            view_filter = st.selectbox("View", ["All Tasks", "My Tasks", "Available Tasks", "Completed"])
        with col2:
            status_filter = st.multiselect("Status", ["New", "In Progress", "Completed", "Paused"], default=["New", "In Progress"])
        with col3:
            priority_filter = st.multiselect("Priority", ["Critical", "High", "Medium", "Low"], default=["Critical", "High", "Medium", "Low"])
        with col4:
            department_filter = st.multiselect("Department", ["Finance", "Legal", "Compliance", "Operations", "Risk Management"])
        
        # Filter tasks
        filtered_tasks = st.session_state.tasks.copy()
        
        if view_filter == "My Tasks":
            filtered_tasks = get_user_tasks(st.session_state.user_name)
        elif view_filter == "Available Tasks":
            filtered_tasks = get_available_tasks()
        elif view_filter == "Completed":
            filtered_tasks = [t for t in filtered_tasks if t["Status"] == "Completed"]
            
        filtered_tasks = [t for t in filtered_tasks if t["Status"] in status_filter and t["Priority"] in priority_filter]
        if department_filter:
            filtered_tasks = [t for t in filtered_tasks if t["Department"] in department_filter]
        
        # Display tasks
        if not filtered_tasks:
            st.info("No tasks match the current filters.")
        else:
            for task in filtered_tasks:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    
                    with col1:
                        st.write(f"**#{task['Task ID']} - {task['Title']}**")
                        st.caption(f"{task['Company']} | {task['Document Type']} | {task['Department']}")
                        
                    with col2:
                        st.write(f"**Assigned:** {task['Assigned To']}")
                        st.write(f"**Due:** {task['Due Date'].strftime('%Y-%m-%d')}")
                        
                    with col3:
                        status_class = task['Status'].lower().replace(' ', '-')
                        st.markdown(f'<span class="status-badge status-{status_class}">{task["Status"]}</span>', unsafe_allow_html=True)
                        priority_class = task['Priority'].lower()
                        st.markdown(f'<span class="status-badge priority-{priority_class}">{task["Priority"]}</span>', unsafe_allow_html=True)
                        
                    with col4:
                        # Action buttons
                        if task["Status"] == "New" and task["Assigned To"] == "Unassigned":
                            if st.button("Accept", key=f"accept_{task['Task ID']}"):
                                update_task_status(task["Task ID"], "In Progress", st.session_state.user_name)
                                st.rerun()
                                
                        elif task["Assigned To"] == st.session_state.user_name:
                            if task["Status"] == "In Progress":
                                col4a, col4b = st.columns(2)
                                with col4a:
                                    if st.button("Pause", key=f"pause_{task['Task ID']}"):
                                        update_task_status(task["Task ID"], "Paused")
                                        st.rerun()
                                with col4b:
                                    if st.button("Complete", key=f"complete_{task['Task ID']}"):
                                        update_task_status(task["Task ID"], "Completed")
                                        st.rerun()
                                        
                            elif task["Status"] == "Paused":
                                if st.button("Resume", key=f"resume_{task['Task ID']}"):
                                    update_task_status(task["Task ID"], "In Progress")
                                    st.rerun()
                    
                    with st.expander(f"Task Details #{task['Task ID']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Company:** {task['Company']}")
                            st.write(f"**Document Type:** {task['Document Type']}")
                            st.write(f"**Priority:** {task['Priority']}")
                            st.write(f"**Status:** {task['Status']}")
                        with col2:
                            st.write(f"**Assigned To:** {task['Assigned To']}")
                            st.write(f"**Created:** {task['Created Date'].strftime('%Y-%m-%d %H:%M')}")
                            st.write(f"**Due Date:** {task['Due Date'].strftime('%Y-%m-%d')}")
                            if task['Completed Date']:
                                st.write(f"**Completed:** {task['Completed Date'].strftime('%Y-%m-%d %H:%M')}")
                        
                        st.write("**Description:**")
                        st.write(task['Description'])
                        
                        # Show attachments if any
                        if task.get('Attachments'):
                            st.write("**Attachments:**")
                            for att in task['Attachments']:
                                st.download_button(
                                    label=f"📎 {att['filename']}",
                                    data=att['content'],
                                    file_name=att['filename'],
                                    key=f"att_{task['Task ID']}_{att['filename']}"
                                )
                    
                    st.markdown("---")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ======================================
    # ANALYTICS TAB
    # ======================================
    with tabs[1]:
        st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
        st.header("📊 Analytics Dashboard")
        
        # Upload analytics data
        st.subheader("Upload Analytics Data")
        analytics_file = st.file_uploader("Upload Excel file for analytics", type=["xlsx", "xls"], key="analytics_upload")
        
        if analytics_file:
            if st.button("Process Analytics Data"):
                if process_analytics_excel(analytics_file):
                    st.success("Analytics data loaded successfully!")
                else:
                    st.error("Failed to load analytics data")
        
        # Sheet selection
        if st.session_state.analytics_data:
            st.subheader("Data Selection")
            sheet_names = list(st.session_state.analytics_data.keys())
            selected_sheet = st.selectbox("Select Sheet", sheet_names)
            
            if selected_sheet:
                df = st.session_state.analytics_data[selected_sheet]
                st.session_state.current_sheet = selected_sheet
                
                # Column selection
                st.subheader("Configure Dashboard")
                available_columns = df.columns.tolist()
                selected_columns = st.multiselect("Select Columns for Analysis", available_columns, default=available_columns[:min(5, len(available_columns))])
                
                if selected_columns:
                    create_analytics_dashboard(df[selected_columns], selected_columns)
        else:
            st.info("Please upload an Excel file with analytics data to get started.")
            
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ======================================
    # TEAM MANAGEMENT TAB (For managers) / DATA IMPORT (For analysts)
    # ======================================
    with tabs[2]:
        if st.session_state.user_role == "manager":
            st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
            st.header("👥 Team Management")
            
            # Team performance metrics
            team_performance = []
            for analyst in ANALYSTS:
                analyst_tasks = get_user_tasks(analyst)
                total = len(analyst_tasks)
                completed = len([t for t in analyst_tasks if t["Status"] == "Completed"])
                in_progress = len([t for t in analyst_tasks if t["Status"] == "In Progress"])
                overdue = len([t for t in analyst_tasks if t["Status"] != "Completed" and t["Due Date"] < datetime.now()])
                
                team_performance.append({
                    "Analyst": analyst,
                    "Total Tasks": total,
                    "Completed": completed,
                    "In Progress": in_progress,
                    "Overdue": overdue,
                    "Completion Rate": f"{(completed/total*100):.1f}%" if total > 0 else "0%"
                })
            
            performance_df = pd.DataFrame(team_performance)
            st.dataframe(performance_df, use_container_width=True)
            
            # Team charts
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(performance_df, x='Analyst', y='Completed', title='Tasks Completed by Analyst')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = px.pie(performance_df, values='Total Tasks', names='Analyst', title='Task Distribution')
                st.plotly_chart(fig, use_container_width=True)
                
            st.markdown("</div>", unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
            st.header("📁 Data Import")
            
            # Email import
            st.subheader("📧 Email Import")
            eml_files = st.file_uploader("Upload .eml files", type=["eml"], accept_multiple_files=True, key="email_import")
            
            if eml_files:
                if st.button("Process Emails", type="primary"):
                    processed = 0
                    for eml_file in eml_files:
                        task = process_email_file(eml_file)
                        if task:
                            processed += 1
                            st.success(f"Created task #{task['Task ID']} from {eml_file.name}")
                    
                    st.success(f"Processed {processed} email(s) successfully!")
            
            # Excel task import
            st.subheader("📊 Excel Task Import")
            task_excel = st.file_uploader("Upload Excel for task creation", type=["xlsx", "xls"], key="task_excel")
            
            if task_excel:
                if st.button("Create Tasks from Excel", type="primary"):
                    tasks_created = process_task_excel(task_excel)
                    st.success(f"Created {tasks_created} tasks from Excel file!")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # ======================================
    # DATA IMPORT TAB (For managers)
    # ======================================
    if st.session_state.user_role == "manager" and len(tabs) > 3:
        with tabs[3]:
            st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
            st.header("📁 Data Import")
            
            # Email import
            st.subheader("📧 Email Import")
            eml_files = st.file_uploader("Upload .eml files", type=["eml"], accept_multiple_files=True, key="manager_email_import")
            
            if eml_files:
                if st.button("Process Emails", type="primary", key="manager_email_btn"):
                    processed = 0
                    for eml_file in eml_files:
                        task = process_email_file(eml_file)
                        if task:
                            processed += 1
                            st.success(f"Created task #{task['Task ID']} from {eml_file.name}")
                    
                    st.success(f"Processed {processed} email(s) successfully!")
            
            # Excel task import
            st.subheader("📊 Excel Task Import")
            task_excel = st.file_uploader("Upload Excel for task creation", type=["xlsx", "xls"], key="manager_task_excel")
            
            if task_excel:
                if st.button("Create Tasks from Excel", type="primary", key="manager_excel_btn"):
                    tasks_created = process_task_excel(task_excel)
                    st.success(f"Created {tasks_created} tasks from Excel file!")
            
            st.markdown("</div>", unsafe_allow_html=True)

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
