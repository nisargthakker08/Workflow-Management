# ultimate_arms_system.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import io
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import email
from email import policy
from email.parser import BytesParser
import base64
from io import BytesIO

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="ARMS Workflow Management",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# CUSTOM CSS - ULTIMATE DESIGN
# =========================

st.markdown("""
<style>
    /* Ultimate Modern Design */
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Top Navigation */
    .top-nav {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        padding: 1rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .nav-btn {
        background: rgba(255,255,255,0.15);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0 0.5rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .nav-btn:hover {
        background: rgba(255,255,255,0.25);
        transform: translateY(-2px);
    }
    
    .nav-btn.active {
        background: white;
        color: #2c3e50;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Ultimate Cards */
    .ultimate-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 1px solid #eef2f7;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .ultimate-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.12);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.5rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    
    /* Task Cards */
    .task-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3498db;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border: 1px solid #f1f3f4;
    }
    
    .task-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    /* Status System */
    .status-new { 
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(52, 152, 219, 0.3);
    }
    
    .status-in-progress { 
        background: linear-gradient(135deg, #f39c12, #e67e22);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(243, 156, 18, 0.3);
    }
    
    .status-completed { 
        background: linear-gradient(135deg, #27ae60, #229954);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(39, 174, 96, 0.3);
    }
    
    .priority-high { 
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(231, 76, 60, 0.3);
    }
    
    .priority-medium { 
        background: linear-gradient(135deg, #f39c12, #e67e22);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(243, 156, 18, 0.3);
    }
    
    .priority-low { 
        background: linear-gradient(135deg, #27ae60, #229954);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(39, 174, 96, 0.3);
    }
    
    /* Filter Section */
    .filter-section {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border: 1px solid #dee2e6;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05);
    }
    
    /* Modal Overlay */
    .modal-overlay {
        background: rgba(0,0,0,0.8);
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .modal-content {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        max-width: 800px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
    }
    
    /* User Profile */
    .user-profile {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE - ENTERPRISE GRADE
# =========================

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Task Management"

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

if 'analysts' not in st.session_state:
    st.session_state.analysts = [
        "Nisarg Thakker", "Jen Shears", "Komal Khamar", "Janet Yanatos",
        "Rondrea Carroll", "Devanshi Joshi", "Divyesh Fofandi", 
        "Parth Chelani", "Prerna Kesrani", "Ayushi Chandel",
        "Rondrea Carroll", "John Smith", "Sarah Johnson", "Mike Davis"
    ]

if 'current_user' not in st.session_state:
    st.session_state.current_user = "Nisarg Thakker"

if 'show_new_task_modal' not in st.session_state:
    st.session_state.show_new_task_modal = False

if 'show_get_task_modal' not in st.session_state:
    st.session_state.show_get_task_modal = False

if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = {}

if 'achieved_data' not in st.session_state:
    st.session_state.achieved_data = None

# =========================
# ULTIMATE DATA GENERATION
# =========================

def generate_enterprise_tasks():
    """Generate enterprise-level sample tasks"""
    companies = [
        'US Foods Holding Corp.', 'Medline Inc.', 'Soléero', 'Bath & Body Works, Inc.', 
        'Ace Hardware', 'Walmart Inc.', 'Amazon.com Inc.', 'Microsoft Corporation',
        'Apple Inc.', 'Google LLC', 'Tesla Inc.', 'Johnson & Johnson',
        'JPMorgan Chase', 'Bank of America', 'Wells Fargo', 'Citigroup',
        'Goldman Sachs', 'Morgan Stanley', 'Ford Motor', 'General Motors'
    ]
    
    document_types = ['10-Q', '10-K', '8-K', 'S-1', 'DEF 14A', 'Form 4', 'Form 3']
    task_types = ['Tier I - Basic Review', 'Tier II - Detailed Analysis', 'Tier III - Complex Audit']
    priorities = ['Critical', 'High', 'Medium', 'Low']
    statuses = ['New', 'In Progress', 'Under Review', 'Completed', 'On Hold']
    
    tasks = []
    for i in range(150):
        task_id = 1500 - i
        company = np.random.choice(companies)
        task_type = np.random.choice(task_types, p=[0.5, 0.3, 0.2])
        doc_type = np.random.choice(document_types)
        priority = np.random.choice(priorities, p=[0.1, 0.4, 0.3, 0.2])
        status = np.random.choice(statuses, p=[0.15, 0.3, 0.2, 0.3, 0.05])
        
        # Smart assignment based on task type
        if task_type == 'Tier I - Basic Review':
            assigned_user = np.random.choice(st.session_state.analysts[:8])
        elif task_type == 'Tier II - Detailed Analysis':
            assigned_user = np.random.choice(st.session_state.analysts[4:12])
        else:
            assigned_user = np.random.choice(st.session_state.analysts[8:])
        
        created_date = datetime.now() - timedelta(days=np.random.randint(1, 90))
        due_date = created_date + timedelta(days=np.random.randint(7, 45))
        
        completed_date = None
        if status == 'Completed':
            completed_date = created_date + timedelta(days=np.random.randint(3, 30))
        
        tasks.append({
            'Task ID': task_id,
            'Task Type': task_type,
            'Company Name': company,
            'Document Type': doc_type,
            'Priority': priority,
            'Status': status,
            'Assigned User': assigned_user,
            'Created Date': created_date,
            'Due Date': due_date,
            'Completed Date': completed_date,
            'Description': f"Comprehensive review of {doc_type} filing for {company}. Requires detailed analysis of financial statements and compliance checks.",
            'Estimated Hours': np.random.randint(2, 16),
            'Complexity': np.random.choice(['Low', 'Medium', 'High'], p=[0.3, 0.5, 0.2]),
            'Department': np.random.choice(['Finance', 'Legal', 'Compliance', 'Operations']),
            'SLA Days': np.random.randint(3, 15)
        })
    
    return tasks

def generate_achieved_data():
    """Generate comprehensive achieved data for visualization"""
    months = pd.date_range('2024-01-01', periods=12, freq='M')
    workflows = ['Tier I Review', 'Tier II Analysis', 'Tier III Audit', 'UCC Filings', 'Judgments', 'Chapter 11', 'Chapter 7']
    
    data = []
    for month in months:
        for workflow in workflows:
            data.append({
                'Month': month.strftime('%Y-%m'),
                'Workflow': workflow,
                'Tasks_Completed': np.random.randint(50, 200),
                'Tasks_Created': np.random.randint(60, 220),
                'SLA_Compliance_Percent': np.random.uniform(85, 99),
                'Avg_Completion_Time_Days': np.random.uniform(2, 10),
                'Quality_Score_Percent': np.random.uniform(88, 98),
                'Backlog_Items': np.random.randint(100, 400),
                'Team_Productivity': np.random.uniform(75, 95)
            })
    
    return pd.DataFrame(data)

# Initialize with enterprise data
if not st.session_state.tasks:
    st.session_state.tasks = generate_enterprise_tasks()

if st.session_state.achieved_data is None:
    st.session_state.achieved_data = generate_achieved_data()

# =========================
# ULTIMATE HELPER FUNCTIONS
# =========================

def get_user_tasks(user):
    """Get tasks assigned to specific user"""
    return [task for task in st.session_state.tasks if task['Assigned User'] == user]

def get_new_available_tasks():
    """Get unassigned new tasks"""
    return [task for task in st.session_state.tasks if task['Status'] == 'New']

def create_tasks_from_excel(file):
    """Create multiple tasks from Excel file"""
    try:
        df = pd.read_excel(file)
        new_tasks = []
        
        for idx, row in df.iterrows():
            task_id = max([task['Task ID'] for task in st.session_state.tasks]) + 1 if st.session_state.tasks else 1500
            
            new_task = {
                'Task ID': task_id + idx,
                'Task Type': row.get('Task Type', 'Tier II - Detailed Analysis'),
                'Company Name': row.get('Company Name', f'Company {idx}'),
                'Document Type': row.get('Document Type', '10-Q'),
                'Priority': row.get('Priority', 'Medium'),
                'Status': 'New',
                'Assigned User': 'Unassigned',
                'Created Date': datetime.now(),
                'Due Date': datetime.now() + timedelta(days=14),
                'Completed Date': None,
                'Description': row.get('Description', f'Automated task creation from Excel import - Row {idx+1}'),
                'Estimated Hours': row.get('Estimated Hours', 4),
                'Complexity': row.get('Complexity', 'Medium'),
                'Department': row.get('Department', 'Compliance'),
                'SLA Days': row.get('SLA Days', 7),
                'Source': 'Excel Bulk Import'
            }
            new_tasks.append(new_task)
        
        st.session_state.tasks.extend(new_tasks)
        return len(new_tasks)
    except Exception as e:
        st.error(f"🚨 Error processing Excel file: {str(e)}")
        return 0

def process_email_file(email_file):
    """Process .eml file and create task with advanced parsing"""
    try:
        raw_bytes = email_file.read()
        msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)
        
        subject = msg["subject"] or "No Subject"
        sender = msg["from"] or "Unknown Sender"
        date_received = msg["date"] or datetime.now()
        
        # Advanced body extraction
        body = ""
        attachments = []
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append(filename)
                elif content_type == "text/plain":
                    try:
                        body = part.get_content()
                    except:
                        continue
        else:
            body = msg.get_content()
        
        # Create comprehensive task from email
        task_id = max([task['Task ID'] for task in st.session_state.tasks]) + 1 if st.session_state.tasks else 1500
        
        # Determine priority based on email content
        priority_keywords = {'urgent': 'Critical', 'asap': 'High', 'important': 'High'}
        priority = 'Medium'
        email_content = (subject + " " + body).lower()
        for keyword, pri in priority_keywords.items():
            if keyword in email_content:
                priority = pri
                break
        
        new_task = {
            'Task ID': task_id,
            'Task Type': 'Tier I - Basic Review',
            'Company Name': f"Email: {sender}",
            'Document Type': 'Email Processing',
            'Priority': priority,
            'Status': 'New',
            'Assigned User': 'Unassigned',
            'Created Date': datetime.now(),
            'Due Date': datetime.now() + timedelta(days=3 if priority in ['Critical', 'High'] else 7),
            'Completed Date': None,
            'Description': f"📧 Email Task\n\nSubject: {subject}\nFrom: {sender}\nReceived: {date_received}\n\nContent:\n{body[:800]}{'...' if len(body) > 800 else ''}",
            'Estimated Hours': 2,
            'Complexity': 'Low',
            'Department': 'Operations',
            'SLA Days': 3,
            'Source': 'Email Import',
            'Attachments': attachments
        }
        
        st.session_state.tasks.append(new_task)
        return True
    except Exception as e:
        st.error(f"🚨 Error processing email: {str(e)}")
        return False

def load_achieved_data(file):
    """Load and process achieved data Excel file"""
    try:
        df = pd.read_excel(file)
        st.session_state.achieved_data = df
        return True
    except Exception as e:
        st.error(f"🚨 Error loading achieved data: {str(e)}")
        return False

# =========================
# ULTIMATE TOP NAVIGATION
# =========================

def render_ultimate_navigation():
    """Render the ultimate top navigation system"""
    st.markdown("""
    <div class="top-nav">
        <div style="display: flex; align-items: center;">
            <h2 style="color: white; margin: 0; margin-right: 3rem;">🚀 ARMS Workflow Management</h2>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2, col3, col4, col5, col6 = st.columns([2,2,2,2,2,1])
    
    with col1:
        if st.button("📋 Task Management", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "Task Management" else "secondary"):
            st.session_state.current_page = "Task Management"
            st.rerun()
    
    with col2:
        if st.button("📊 Analytics Dashboard", use_container_width=True,
                    type="primary" if st.session_state.current_page == "Analytics Dashboard" else "secondary"):
            st.session_state.current_page = "Analytics Dashboard"
            st.rerun()
    
    with col3:
        if st.button("📁 Data Import", use_container_width=True,
                    type="primary" if st.session_state.current_page == "Data Import" else "secondary"):
            st.session_state.current_page = "Data Import"
            st.rerun()
    
    with col4:
        if st.button("👥 Team Metrics", use_container_width=True,
                    type="primary" if st.session_state.current_page == "Team Metrics" else "secondary"):
            st.session_state.current_page = "Team Metrics"
            st.rerun()
    
    with col5:
        if st.button("📈 Achieved Data", use_container_width=True,
                    type="primary" if st.session_state.current_page == "Achieved Data" else "secondary"):
            st.session_state.current_page = "Achieved Data"
            st.rerun()
    
    with col6:
        st.markdown(f"""
        <div class="user-profile">
            <div style="font-size: 0.9rem;">👤 {st.session_state.current_user}</div>
            <div style="font-size: 0.7rem; opacity: 0.8;">Administrator</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# =========================
# ULTIMATE TASK MANAGEMENT
# =========================

def render_ultimate_task_management():
    st.markdown('<div class="main-header">🎯 Ultimate Task Management System</div>', unsafe_allow_html=True)
    
    # Task Overview Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    user_tasks = get_user_tasks(st.session_state.current_user)
    new_tasks = get_new_available_tasks()
    all_tasks = st.session_state.tasks
    
    with col1:
        if st.button(f"""
        <div style="text-align: center;">
            <div style="font-size: 2rem;">🚀</div>
            <div style="font-size: 1.2rem; font-weight: bold;">Get New Task</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">{len(new_tasks)} Available</div>
        </div>
        """, use_container_width=True, help="Click to get a new task from available pool"):
            st.session_state.show_get_task_modal = True
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" onclick="alert('My Tasks')">
            <div style="font-size: 2rem;">📋</div>
            <div style="font-size: 1.5rem; font-weight: bold;">{len(user_tasks)}</div>
            <div style="font-size: 1rem;">My Tasks</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">📊</div>
            <div style="font-size: 1.5rem; font-weight: bold;">{len(all_tasks)}</div>
            <div style="font-size: 1rem;">Total Tasks</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if st.button(f"""
        <div style="text-align: center;">
            <div style="font-size: 2rem;">➕</div>
            <div style="font-size: 1.2rem; font-weight: bold;">Create Task</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Manual Creation</div>
        </div>
        """, use_container_width=True, type="primary"):
            st.session_state.show_new_task_modal = True
            st.rerun()
    
    # Ultimate Filter System
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.subheader("🎛️ Advanced Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_filter_type = st.selectbox("Date Filter", ["Created Date", "Due Date", "Completed Date", "All Dates"])
        start_date = st.date_input("From Date", value=date.today() - timedelta(days=30))
    
    with col2:
        end_date = st.date_input("To Date", value=date.today())
        priority_filter = st.multiselect("Priority", ["Critical", "High", "Medium", "Low"], default=["Critical", "High", "Medium", "Low"])
    
    with col3:
        status_filter = st.multiselect("Status", ["New", "In Progress", "Under Review", "Completed", "On Hold"], 
                                     default=["New", "In Progress", "Under Review"])
        task_type_filter = st.multiselect("Task Type", list(set([task['Task Type'] for task in all_tasks])), 
                                        default=list(set([task['Task Type'] for task in all_tasks])))
    
    with col4:
        department_filter = st.multiselect("Department", list(set([task.get('Department', 'General') for task in all_tasks])))
        assigned_filter = st.multiselect("Assigned To", ["My Tasks"] + st.session_state.analysts, default=["My Tasks"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Task View Selection
    view_option = st.radio("📋 Task View:", ["My Tasks", "Available Tasks", "All Tasks", "High Priority"], 
                          horizontal=True, label_visibility="collapsed")
    
    # Filter tasks
    if view_option == "My Tasks":
        filtered_tasks = user_tasks
    elif view_option == "Available Tasks":
        filtered_tasks = new_tasks
    elif view_option == "High Priority":
        filtered_tasks = [task for task in all_tasks if task['Priority'] in ['Critical', 'High']]
    else:
        filtered_tasks = all_tasks
    
    # Apply advanced filters
    filtered_tasks = [task for task in filtered_tasks if 
                     task['Priority'] in priority_filter and
                     task['Status'] in status_filter and
                     task['Task Type'] in task_type_filter and
                     (not department_filter or task.get('Department') in department_filter) and
                     (not assigned_filter or "My Tasks" not in assigned_filter or task['Assigned User'] == st.session_state.current_user or
                      task['Assigned User'] in assigned_filter)]
    
    # Apply date filters
    filtered_tasks = [task for task in filtered_tasks if 
                     task['Created Date'].date() >= start_date and 
                     task['Created Date'].date() <= end_date]
    
    # Display filtered tasks count
    st.info(f"📊 Showing {len(filtered_tasks)} tasks out of {len(all_tasks)} total tasks")
    
    # Render tasks
    render_ultimate_task_table(filtered_tasks, view_option)
    
    # Modals
    if st.session_state.show_get_task_modal:
        render_get_task_modal()
    
    if st.session_state.show_new_task_modal:
        render_new_task_modal()

def render_ultimate_task_table(tasks, view_type):
    """Render tasks in ultimate card format"""
    if not tasks:
        st.info(f"🎯 No {view_type.lower()} found matching your filters.")
        return
    
    # Sort tasks
    tasks = sorted(tasks, key=lambda x: (x['Priority'] in ['Critical', 'High'], x['Due Date']), reverse=True)
    
    for task in tasks[:20]:  # Show first 20 tasks for performance
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                st.write(f"### {task['Company Name']}")
                st.write(f"**Task ID:** #{task['Task ID']} | **Type:** {task['Task Type']} | **Document:** {task['Document Type']}")
                st.write(f"📝 {task['Description'][:120]}{'...' if len(task['Description']) > 120 else ''}")
                
                # Additional metadata
                col1a, col1b, col1c = st.columns(3)
                with col1a:
                    st.caption(f"🕒 Est: {task.get('Estimated Hours', 'N/A')}h")
                with col1b:
                    st.caption(f"🏢 {task.get('Department', 'General')}")
                with col1c:
                    st.caption(f"📅 SLA: {task.get('SLA Days', 'N/A')} days")
            
            with col2:
                st.write(f"**👤 Assigned to:** {task['Assigned User']}")
                st.write(f"**📅 Created:** {task['Created Date'].strftime('%b %d, %Y')}")
                st.write(f"**⏰ Due:** {task['Due Date'].strftime('%b %d, %Y')}")
                
                if task['Completed Date']:
                    st.write(f"**✅ Completed:** {task['Completed Date'].strftime('%b %d, %Y')}")
            
            with col3:
                status_class = f"status-{task['Status'].lower().replace(' ', '-')}"
                st.markdown(f'<div class="{status_class}">{task["Status"]}</div>', unsafe_allow_html=True)
            
            with col4:
                priority_class = f"priority-{task['Priority'].lower()}"
                st.markdown(f'<div class="{priority_class}">{task["Priority"]}</div>', unsafe_allow_html=True)
                
                # Action buttons
                if task['Assigned User'] == 'Unassigned' and view_type == 'Available Tasks':
                    if st.button("🎯 Assign to Me", key=f"assign_{task['Task ID']}", use_container_width=True):
                        task['Assigned User'] = st.session_state.current_user
                        task['Status'] = 'In Progress'
                        st.success(f"✅ Task #{task['Task ID']} assigned to you!")
                        st.rerun()
                elif task['Assigned User'] == st.session_state.current_user and task['Status'] != 'Completed':
                    if st.button("✅ Complete", key=f"complete_{task['Task ID']}", use_container_width=True):
                        task['Status'] = 'Completed'
                        task['Completed Date'] = datetime.now()
                        st.success(f"🎉 Task #{task['Task ID']} marked as completed!")
                        st.rerun()
            
            st.markdown("---")

def render_get_task_modal():
    """Ultimate modal for getting new tasks"""
    st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
    st.markdown('<div class="modal-content">', unsafe_allow_html=True)
    
    st.subheader("🚀 Get New Task")
    
    available_tasks = get_new_available_tasks()
    
    if not available_tasks:
        st.warning("📭 No new tasks available at the moment. Check back later!")
        if st.button("Close", use_container_width=True):
            st.session_state.show_get_task_modal = False
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)
        return
    
    # Show available tasks in a select box
    task_options = {f"Task {task['Task ID']}: {task['Company Name']} - {task['Task Type']}": task for task in available_tasks}
    selected_task_key = st.selectbox("Select a task to assign:", list(task_options.keys()))
    
    selected_task = task_options[selected_task_key]
    
    # Task details
    st.markdown("### 📋 Task Details")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Company:** {selected_task['Company Name']}")
        st.write(f"**Task Type:** {selected_task['Task Type']}")
        st.write(f"**Document:** {selected_task['Document Type']}")
        st.write(f"**Priority:** {selected_task['Priority']}")
    
    with col2:
        st.write(f"**Estimated Hours:** {selected_task.get('Estimated Hours', 'N/A')}")
        st.write(f"**Complexity:** {selected_task.get('Complexity', 'Medium')}")
        st.write(f"**Department:** {selected_task.get('Department', 'General')}")
        st.write(f"**SLA Days:** {selected_task.get('SLA Days', 'N/A')}")
    
    st.write(f"**Description:** {selected_task['Description']}")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Assign to Me", use_container_width=True, type="primary"):
            selected_task['Assigned User'] = st.session_state.current_user
            selected_task['Status'] = 'In Progress'
            st.session_state.show_get_task_modal = False
            st.success("🎉 Task assigned successfully!")
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.show_get_task_modal = False
            st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def render_new_task_modal():
    """Ultimate modal for creating new tasks"""
    st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
    st.markdown('<div class="modal-content">', unsafe_allow_html=True)
    
    st.subheader("➕ Create New Task")
    
    with st.form("ultimate_task_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            task_type = st.selectbox("Task Type", ["Tier I - Basic Review", "Tier II - Detailed Analysis", "Tier III - Complex Audit"])
            company_name = st.text_input("Company Name", placeholder="Enter company name")
            document_type = st.selectbox("Document Type", ["10-Q", "10-K", "8-K", "S-1", "DEF 14A", "Form 4", "Form 3", "Other"])
            priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"])
            department = st.selectbox("Department", ["Finance", "Legal", "Compliance", "Operations", "Risk Management"])
        
        with col2:
            assigned_user = st.selectbox("Assign To", ["Unassigned"] + st.session_state.analysts)
            due_date = st.date_input("Due Date", value=date.today() + timedelta(days=14))
            estimated_hours = st.slider("Estimated Hours", 1, 24, 4)
            complexity = st.selectbox("Complexity", ["Low", "Medium", "High"])
            sla_days = st.slider("SLA Days", 1, 30, 7)
        
        description = st.text_area("Task Description", placeholder="Provide detailed description of the task...", height=120)
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("🚀 Create Task", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submitted:
            if not company_name:
                st.error("❌ Please enter a company name")
            else:
                # Create new task
                task_id = max([task['Task ID'] for task in st.session_state.tasks]) + 1 if st.session_state.tasks else 1500
                
                new_task = {
                    'Task ID': task_id,
                    'Task Type': task_type,
                    'Company Name': company_name,
                    'Document Type': document_type,
                    'Priority': priority,
                    'Status': 'New' if assigned_user == 'Unassigned' else 'In Progress',
                    'Assigned User': assigned_user,
                    'Created Date': datetime.now(),
                    'Due Date': due_date,
                    'Completed Date': None,
                    'Description': description,
                    'Estimated Hours': estimated_hours,
                    'Complexity': complexity,
                    'Department': department,
                    'SLA Days': sla_days,
                    'Source': 'Manual Creation'
                }
                
                st.session_state.tasks.append(new_task)
                st.session_state.show_new_task_modal = False
                st.success(f"✅ Task #{task_id} created successfully!")
                st.rerun()
        
        if cancelled:
            st.session_state.show_new_task_modal = False
            st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# =========================
# ULTIMATE DATA IMPORT
# =========================

def render_ultimate_data_import():
    st.markdown('<div class="main-header">📁 Ultimate Data Import Center</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
        st.subheader("📧 Advanced Email Import")
        
        email_files = st.file_uploader("Upload .eml files", type=['eml'], accept_multiple_files=True, key="email_upload")
        
        if email_files:
            st.write(f"📨 {len(email_files)} email file(s) selected")
            
            if st.button("🚀 Process All Emails", use_container_width=True, type="primary"):
                success_count = 0
                with st.spinner("Processing emails..."):
                    for email_file in email_files:
                        if process_email_file(email_file):
                            success_count += 1
                
                if success_count > 0:
                    st.success(f"✅ Successfully processed {success_count} out of {len(email_files)} emails!")
                else:
                    st.error("❌ Failed to process any emails")
        
        st.markdown("""
        **Supported Features:**
        - 📧 Email body extraction
        - 📎 Attachment detection  
        - 🚨 Priority auto-detection
        - ⏰ Smart due date assignment
        - 🏷️ Automatic categorization
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
        st.subheader("📊 Excel Task Import")
        
        excel_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'], key="excel_upload")
        
        if excel_file:
            st.write("📋 Excel file ready for processing")
            
            # Show preview
            try:
                df_preview = pd.read_excel(excel_file)
                st.write(f"📊 Preview: {len(df_preview)} rows, {len(df_preview.columns)} columns")
                st.dataframe(df_preview.head(3), use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error previewing file: {str(e)}")
            
            if st.button("🚀 Create Tasks from Excel", use_container_width=True, type="primary"):
                with st.spinner("Processing Excel file..."):
                    task_count = create_tasks_from_excel(excel_file)
                    if task_count > 0:
                        st.success(f"✅ Created {task_count} new tasks from Excel!")
                    else:
                        st.error("❌ Failed to create tasks from Excel")
        
        st.markdown("""
        **Expected Columns:**
        - Company Name
        - Task Type  
        - Document Type
        - Priority
        - Description
        - Department
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Current System Overview
    st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
    st.subheader("📈 System Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    all_tasks = st.session_state.tasks
    
    with col1:
        total_tasks = len(all_tasks)
        st.metric("Total Tasks", total_tasks)
    
    with col2:
        new_tasks = len(get_new_available_tasks())
        st.metric("Available Tasks", new_tasks)
    
    with col3:
        in_progress = len([t for t in all_tasks if t['Status'] == 'In Progress'])
        st.metric("In Progress", in_progress)
    
    with col4:
        completed = len([t for t in all_tasks if t['Status'] == 'Completed'])
        st.metric("Completed", completed)
    
    with col5:
        high_priority = len([t for t in all_tasks if t['Priority'] in ['Critical', 'High']])
        st.metric("High Priority", high_priority)
    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ULTIMATE ACHIEVED DATA VISUALIZATION
# =========================

def render_achieved_data():
    st.markdown('<div class="main-header">📈 Ultimate Achieved Data Analytics</div>', unsafe_allow_html=True)
    
    # Data Upload Section
    st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
    st.subheader("📤 Upload Your Achieved Data")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        achieved_file = st.file_uploader("Upload Achieved Data Excel File", type=['xlsx', 'xls'], key="achieved_upload")
        
        if achieved_file:
            if st.button("🚀 Load Achieved Data", use_container_width=True, type="primary"):
                if load_achieved_data(achieved_file):
                    st.success("✅ Achieved data loaded successfully!")
                else:
                    st.error("❌ Failed to load achieved data")
    
    with col2:
        if st.session_state.achieved_data is not None:
            st.success(f"✅ Data Loaded: {len(st.session_state.achieved_data)} rows")
            if st.button("🔄 Generate Sample Data", use_container_width=True):
                st.session_state.achieved_data = generate_achieved_data()
                st.success("✅ Sample data generated!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.achieved_data is None:
        st.info("📊 Please upload your achieved data Excel file to see visualizations")
        return
    
    df = st.session_state.achieved_data
    
    # Ultimate Visualization Dashboard
    st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
    st.subheader("📊 Interactive Analytics Dashboard")
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_completion = df['Avg_Completion_Time_Days'].mean()
        st.metric("Avg Completion Time", f"{avg_completion:.1f} days")
    
    with col2:
        avg_sla = df['SLA_Compliance_Percent'].mean()
        st.metric("Avg SLA Compliance", f"{avg_sla:.1f}%")
    
    with col3:
        total_completed = df['Tasks_Completed'].sum()
        st.metric("Total Tasks Completed", f"{total_completed:,}")
    
    with col4:
        avg_quality = df['Quality_Score_Percent'].mean()
        st.metric("Avg Quality Score", f"{avg_quality:.1f}%")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
        st.subheader("📈 Performance Trends")
        
        # Time series analysis
        trend_data = df.groupby('Month').agg({
            'Tasks_Completed': 'sum',
            'SLA_Compliance_Percent': 'mean',
            'Quality_Score_Percent': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend_data['Month'], y=trend_data['Tasks_Completed'], 
                                name='Tasks Completed', line=dict(color='#3498db', width=3)))
        fig.add_trace(go.Scatter(x=trend_data['Month'], y=trend_data['SLA_Compliance_Percent'], 
                                name='SLA %', line=dict(color='#27ae60', width=3), yaxis='y2'))
        
        fig.update_layout(
            title='Monthly Performance Trends',
            yaxis=dict(title='Tasks Completed'),
            yaxis2=dict(title='SLA Compliance %', overlaying='y', side='right'),
            height=400,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
        st.subheader("📊 Workflow Distribution")
        
        # Workflow performance
        workflow_data = df.groupby('Workflow').agg({
            'Tasks_Completed': 'sum',
            'SLA_Compliance_Percent': 'mean',
            'Avg_Completion_Time_Days': 'mean'
        }).reset_index()
        
        fig = px.bar(workflow_data, x='Workflow', y='Tasks_Completed',
                     color='SLA_Compliance_Percent', 
                     title='Tasks Completed by Workflow',
                     color_continuous_scale='Viridis')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Advanced Analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
        st.subheader("🎯 Quality vs SLA Analysis")
        
        fig = px.scatter(df, x='SLA_Compliance_Percent', y='Quality_Score_Percent',
                        size='Tasks_Completed', color='Workflow',
                        hover_data=['Month'],
                        title='SLA Compliance vs Quality Score')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
        st.subheader("📋 Performance Matrix")
        
        # Heatmap
        pivot_data = df.pivot_table(values='Tasks_Completed', 
                                  index='Workflow', 
                                  columns='Month', 
                                  aggfunc='sum').fillna(0)
        
        fig = px.imshow(pivot_data, 
                       title='Tasks Completed Heatmap',
                       color_continuous_scale='Blues',
                       aspect='auto')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Raw Data Explorer
    st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
    st.subheader("🔍 Data Explorer")
    
    # Filters for data exploration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_workflows = st.multiselect("Select Workflows", df['Workflow'].unique(), default=df['Workflow'].unique())
    
    with col2:
        selected_months = st.multiselect("Select Months", df['Month'].unique(), default=df['Month'].unique())
    
    with col3:
        sla_threshold = st.slider("SLA Compliance Threshold (%)", 0, 100, 90)
    
    # Filter data
    filtered_df = df[(df['Workflow'].isin(selected_workflows)) & 
                    (df['Month'].isin(selected_months)) &
                    (df['SLA_Compliance_Percent'] >= sla_threshold)]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"arms_achieved_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Summary statistics
        st.write("**📊 Summary Statistics:**")
        st.write(f"- Total Records: {len(filtered_df)}")
        st.write(f"- Average SLA: {filtered_df['SLA_Compliance_Percent'].mean():.1f}%")
        st.write(f"- Average Quality: {filtered_df['Quality_Score_Percent'].mean():.1f}%")
    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ULTIMATE ANALYTICS DASHBOARD
# =========================

def render_ultimate_dashboard():
    st.markdown('<div class="main-header">📊 Ultimate Analytics Dashboard</div>', unsafe_allow_html=True)
    
    if not st.session_state.tasks:
        st.info("📋 No tasks data available. Please create or import tasks first.")
        return
    
    # Convert tasks to DataFrame
    tasks_df = pd.DataFrame(st.session_state.tasks)
    
    # Ultimate KPI Dashboard
    st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
    st.subheader("🎯 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_tasks = len(tasks_df)
        st.metric("Total Tasks", total_tasks)
    
    with col2:
        completed_tasks = len(tasks_df[tasks_df['Status'] == 'Completed'])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    with col3:
        in_progress_tasks = len(tasks_df[tasks_df['Status'] == 'In Progress'])
        st.metric("In Progress", in_progress_tasks)
    
    with col4:
        high_priority_tasks = len(tasks_df[tasks_df['Priority'].isin(['Critical', 'High'])])
        st.metric("High Priority", high_priority_tasks)
    
    with col5:
        overdue_tasks = len([t for t in st.session_state.tasks if t['Due Date'].date() < date.today() and t['Status'] != 'Completed'])
        st.metric("Overdue", overdue_tasks)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
        st.subheader("📈 Task Distribution Analysis")
        
        # Status distribution
        status_counts = tasks_df['Status'].value_counts()
        fig1 = px.pie(values=status_counts.values, names=status_counts.index, 
                     title="Task Status Distribution", hole=0.4)
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
        st.subheader("🎯 Priority & Complexity")
        
        # Priority vs Complexity
        if 'Complexity' in tasks_df.columns:
            pivot_data = tasks_df.groupby(['Priority', 'Complexity']).size().reset_index(name='Count')
            fig2 = px.bar(pivot_data, x='Priority', y='Count', color='Complexity',
                         title='Task Distribution by Priority & Complexity',
                         barmode='group')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            priority_counts = tasks_df['Priority'].value_counts()
            fig2 = px.bar(x=priority_counts.index, y=priority_counts.values,
                         title='Tasks by Priority', color=priority_counts.index)
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Team Performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
        st.subheader("👥 Team Workload Distribution")
        
        user_counts = tasks_df['Assigned User'].value_counts()
        fig3 = px.bar(y=user_counts.index, x=user_counts.values, orientation='h',
                     title="Tasks Assigned by User", color=user_counts.values)
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
        st.subheader("📊 Department Overview")
        
        if 'Department' in tasks_df.columns:
            dept_counts = tasks_df['Department'].value_counts()
            fig4 = px.pie(values=dept_counts.values, names=dept_counts.index,
                         title="Tasks by Department")
            st.plotly_chart(fig4, use_container_width=True)
        else:
            type_counts = tasks_df['Task Type'].value_counts()
            fig4 = px.pie(values=type_counts.values, names=type_counts.index,
                         title="Tasks by Type")
            st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ULTIMATE TEAM METRICS
# =========================

def render_ultimate_team_metrics():
    st.markdown('<div class="main-header">👥 Ultimate Team Performance Analytics</div>', unsafe_allow_html=True)
    
    if not st.session_state.tasks:
        st.info("📋 No tasks data available.")
        return
    
    tasks_df = pd.DataFrame(st.session_state.tasks)
    
    # Team Performance Dashboard
    st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
    st.subheader("🏆 Team Performance Summary")
    
    # Calculate comprehensive analyst metrics
    analyst_stats = []
    for analyst in st.session_state.analysts:
        analyst_tasks = tasks_df[tasks_df['Assigned User'] == analyst]
        total_tasks = len(analyst_tasks)
        
        if total_tasks > 0:
            completed_tasks = len(analyst_tasks[analyst_tasks['Status'] == 'Completed'])
            in_progress_tasks = len(analyst_tasks[analyst_tasks['Status'] == 'In Progress'])
            completion_rate = (completed_tasks / total_tasks * 100)
            
            # Calculate average completion time for completed tasks
            completed_with_dates = [t for t in st.session_state.tasks 
                                  if t['Assigned User'] == analyst and t['Status'] == 'Completed' 
                                  and t['Completed Date'] is not None and t['Created Date'] is not None]
            
            avg_completion_days = 0
            if completed_with_dates:
                completion_times = [(t['Completed Date'] - t['Created Date']).days for t in completed_with_dates]
                avg_completion_days = sum(completion_times) / len(completion_times)
            
            # Priority distribution
            high_priority = len(analyst_tasks[analyst_tasks['Priority'].isin(['Critical', 'High'])])
            
            analyst_stats.append({
                'Analyst': analyst,
                'Total Tasks': total_tasks,
                'Completed': completed_tasks,
                'In Progress': in_progress_tasks,
                'Completion Rate': f"{completion_rate:.1f}%",
                'Avg Completion Days': f"{avg_completion_days:.1f}",
                'High Priority Tasks': high_priority,
                'Productivity Score': f"{(completion_rate * (1 - avg_completion_days/30) * 100):.1f}" if avg_completion_days > 0 else "0.0"
            })
    
    stats_df = pd.DataFrame(analyst_stats)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        top_performer = stats_df.loc[stats_df['Total Tasks'].idxmax()] if not stats_df.empty else None
        if top_performer is not None:
            st.metric("🏆 Top Performer", top_performer['Analyst'])
    
    with col2:
        avg_completion = stats_df['Completion Rate'].str.rstrip('%').astype(float).mean() if not stats_df.empty else 0
        st.metric("📊 Avg Completion Rate", f"{avg_completion:.1f}%")
    
    with col3:
        total_team_tasks = stats_df['Total Tasks'].sum() if not stats_df.empty else 0
        st.metric("👥 Total Team Tasks", total_team_tasks)
    
    with col4:
        avg_productivity = stats_df['Productivity Score'].astype(float).mean() if not stats_df.empty else 0
        st.metric("🚀 Avg Productivity", f"{avg_productivity:.1f}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
        st.subheader("📈 Performance Comparison")
        
        if not stats_df.empty:
            fig1 = px.bar(stats_df, x='Analyst', y='Total Tasks', 
                         color='Completion Rate',
                         title='Tasks Assigned & Completion Rate',
                         hover_data=['Completed', 'In Progress'])
            st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
        st.subheader("🎯 Productivity Analysis")
        
        if not stats_df.empty:
            productivity_df = stats_df.copy()
            productivity_df['Productivity Score Num'] = productivity_df['Productivity Score'].astype(float)
            
            fig2 = px.scatter(productivity_df, x='Total Tasks', y='Productivity Score Num',
                            size='High Priority Tasks', color='Analyst',
                            title='Productivity vs Workload',
                            hover_data=['Completion Rate', 'Avg Completion Days'])
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Team Performance Table
    st.markdown('<div class="ultimate-card">', unsafe_allow_html=True)
    st.subheader("📋 Detailed Team Performance")
    
    if not stats_df.empty:
        st.dataframe(stats_df, use_container_width=True)
    else:
        st.info("No team performance data available.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ULTIMATE MAIN APPLICATION
# =========================

def main():
    # Render ultimate navigation
    render_ultimate_navigation()
    
    # Render current page with ultimate design
    if st.session_state.current_page == "Task Management":
        render_ultimate_task_management()
    elif st.session_state.current_page == "Analytics Dashboard":
        render_ultimate_dashboard()
    elif st.session_state.current_page == "Data Import":
        render_ultimate_data_import()
    elif st.session_state.current_page == "Team Metrics":
        render_ultimate_team_metrics()
    elif st.session_state.current_page == "Achieved Data":
        render_achieved_data()

if __name__ == "__main__":
    main()
