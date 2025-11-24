# arms_complete_system.py
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

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="ARMS Workflow Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>
    /* Top Navigation */
    .top-nav {
        background: linear-gradient(135deg, #0052cc 0%, #0747a6 100%);
        padding: 1rem 2rem;
        border-radius: 0px;
        margin-bottom: 2rem;
    }
    
    .nav-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
    }
    
    .nav-btn {
        background: rgba(255,255,255,0.2);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .nav-btn:hover {
        background: rgba(255,255,255,0.3);
    }
    
    .nav-btn.active {
        background: white;
        color: #0747a6;
    }
    
    /* Cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        text-align: center;
        cursor: pointer;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    .task-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2ecc71;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Status badges */
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-new { background: #3498db; color: white; }
    .status-in-progress { background: #f39c12; color: white; }
    .status-completed { background: #27ae60; color: white; }
    .status-pending { background: #95a5a6; color: white; }
    
    .priority-high { background: #e74c3c; color: white; }
    .priority-medium { background: #f39c12; color: white; }
    .priority-low { background: #27ae60; color: white; }
    
    /* Filters */
    .filter-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #dde1e6;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Task Management"

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

if 'analysts' not in st.session_state:
    st.session_state.analysts = [
        "Nisarg Thakker", "Jen Shears", "Komal Khamar", "Janet Yanatos",
        "Rondrea Carroll", "Devanshi Joshi", "Divyesh Fofandi", 
        "Parth Chelani", "Prerna Kesrani", "Ayushi Chandel"
    ]

if 'current_user' not in st.session_state:
    st.session_state.current_user = "Nisarg Thakker"

if 'show_new_task_modal' not in st.session_state:
    st.session_state.show_new_task_modal = False

if 'show_get_task_modal' not in st.session_state:
    st.session_state.show_get_task_modal = False

# =========================
# SAMPLE DATA GENERATION
# =========================

def generate_sample_tasks():
    """Generate realistic sample tasks"""
    companies = [
        'US Foods Holding Corp.', 'Medline Inc.', 'Soléero', 'Bath & Body Works, Inc.', 
        'Ace Hardware', 'Walmart Inc.', 'Amazon.com Inc.', 'Microsoft Corporation',
        'Apple Inc.', 'Google LLC', 'Tesla Inc.', 'Johnson & Johnson'
    ]
    
    document_types = ['10-Q', '10-K', '8-K', 'S-1', 'DEF 14A']
    task_types = ['Tier I', 'Tier II', 'Tier III']
    priorities = ['High', 'Medium', 'Low']
    statuses = ['New', 'In Progress', 'Completed', 'Pending Review']
    
    tasks = []
    for i in range(50):
        task_id = 1300 - i
        company = np.random.choice(companies)
        task_type = np.random.choice(task_types)
        doc_type = np.random.choice(document_types)
        priority = np.random.choice(priorities, p=[0.6, 0.3, 0.1])
        status = np.random.choice(statuses, p=[0.2, 0.3, 0.4, 0.1])
        assigned_user = np.random.choice(st.session_state.analysts)
        
        created_date = datetime.now() - timedelta(days=np.random.randint(1, 60))
        due_date = created_date + timedelta(days=np.random.randint(7, 30))
        
        completed_date = None
        if status == 'Completed':
            completed_date = created_date + timedelta(days=np.random.randint(1, 20))
        
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
            'Description': f"Review {doc_type} filing for {company}"
        })
    
    return tasks

# Initialize with sample data if empty
if not st.session_state.tasks:
    st.session_state.tasks = generate_sample_tasks()

# =========================
# HELPER FUNCTIONS
# =========================

def get_user_tasks(user):
    """Get tasks assigned to specific user"""
    return [task for task in st.session_state.tasks if task['Assigned User'] == user]

def get_new_available_tasks():
    """Get unassigned new tasks"""
    return [task for task in st.session_state.tasks if task['Status'] == 'New' and task['Assigned User'] == 'Unassigned']

def create_task_from_excel(file):
    """Create tasks from Excel file"""
    try:
        df = pd.read_excel(file)
        new_tasks = []
        
        for idx, row in df.iterrows():
            task_id = max([task['Task ID'] for task in st.session_state.tasks]) + 1 if st.session_state.tasks else 1300
            
            new_task = {
                'Task ID': task_id + idx,
                'Task Type': row.get('Task Type', 'Tier II'),
                'Company Name': row.get('Company Name', f'Company {idx}'),
                'Document Type': row.get('Document Type', '10-Q'),
                'Priority': row.get('Priority', 'Medium'),
                'Status': 'New',
                'Assigned User': 'Unassigned',
                'Created Date': datetime.now(),
                'Due Date': datetime.now() + timedelta(days=14),
                'Completed Date': None,
                'Description': row.get('Description', f'Task from Excel row {idx}'),
                'Source': 'Excel Import'
            }
            new_tasks.append(new_task)
        
        st.session_state.tasks.extend(new_tasks)
        return len(new_tasks)
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return 0

def process_email_file(email_file):
    """Process .eml file and create task"""
    try:
        raw_bytes = email_file.read()
        msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)
        
        subject = msg["subject"] or "No Subject"
        sender = msg["from"] or "Unknown Sender"
        
        # Extract body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_content()
                        break
                    except:
                        continue
        else:
            body = msg.get_content()
        
        # Create task from email
        task_id = max([task['Task ID'] for task in st.session_state.tasks]) + 1 if st.session_state.tasks else 1300
        
        new_task = {
            'Task ID': task_id,
            'Task Type': 'Tier I',
            'Company Name': f"Email: {sender}",
            'Document Type': 'Email',
            'Priority': 'Medium',
            'Status': 'New',
            'Assigned User': 'Unassigned',
            'Created Date': datetime.now(),
            'Due Date': datetime.now() + timedelta(days=7),
            'Completed Date': None,
            'Description': f"Subject: {subject}\n\nFrom: {sender}\n\n{body[:500]}...",
            'Source': 'Email Import'
        }
        
        st.session_state.tasks.append(new_task)
        return True
    except Exception as e:
        st.error(f"Error processing email: {str(e)}")
        return False

# =========================
# TOP NAVIGATION
# =========================

def render_top_navigation():
    st.markdown("""
    <div class="top-nav">
        <div style="text-align: center; color: white; margin-bottom: 1rem;">
            <h1 style="margin: 0; font-size: 2rem;">ARMS Workflow Management System</h1>
            <p style="margin: 0; opacity: 0.8;">Welcome, {}</p>
        </div>
        <div class="nav-buttons">
    """.format(st.session_state.current_user), unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
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
        if st.button("👥 Analyst Metrics", use_container_width=True,
                    type="primary" if st.session_state.current_page == "Analyst Metrics" else "secondary"):
            st.session_state.current_page = "Analyst Metrics"
            st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# =========================
# TASK MANAGEMENT PAGE
# =========================

def render_task_management():
    st.header("🎯 Task Management")
    
    # Task Overview Cards
    col1, col2, col3, col4 = st.columns(4)
    
    user_tasks = get_user_tasks(st.session_state.current_user)
    new_tasks = get_new_available_tasks()
    all_tasks = st.session_state.tasks
    
    with col1:
        if st.button(f"🚀 Get New Task\n{len(new_tasks)} available", use_container_width=True, 
                    help="Click to get a new task from available pool"):
            st.session_state.show_get_task_modal = True
            st.rerun()
    
    with col2:
        st.metric("My Tasks", len(user_tasks))
    
    with col3:
        st.metric("Total Tasks", len(all_tasks))
    
    with col4:
        if st.button("➕ Create Task", use_container_width=True, type="primary"):
            st.session_state.show_new_task_modal = True
            st.rerun()
    
    # Date Filters
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.subheader("📅 Date Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
    
    with col2:
        end_date = st.date_input("End Date", value=date.today())
    
    with col3:
        date_filter_type = st.selectbox("Filter by", ["Created Date", "Due Date", "Completed Date"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Task View Selection
    view_option = st.radio("View Tasks:", ["My Tasks", "All Tasks", "New Tasks"], horizontal=True)
    
    # Filter tasks based on selection and date
    if view_option == "My Tasks":
        filtered_tasks = user_tasks
    elif view_option == "New Tasks":
        filtered_tasks = new_tasks
    else:
        filtered_tasks = all_tasks
    
    # Apply date filters
    filtered_tasks = [task for task in filtered_tasks if task['Created Date'].date() >= start_date and task['Created Date'].date() <= end_date]
    
    # Display tasks
    render_task_table(filtered_tasks, view_option)
    
    # Modals
    if st.session_state.show_get_task_modal:
        render_get_task_modal()
    
    if st.session_state.show_new_task_modal:
        render_new_task_modal()

def render_task_table(tasks, view_type):
    """Render tasks in a table format"""
    if not tasks:
        st.info(f"No {view_type.lower()} found.")
        return
    
    # Convert to DataFrame for easier display
    df = pd.DataFrame(tasks)
    
    # Display key columns
    display_columns = ['Task ID', 'Task Type', 'Company Name', 'Document Type', 'Priority', 'Status', 'Assigned User', 'Due Date']
    
    # Create a styled DataFrame
    for idx, task in enumerate(tasks):
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                st.write(f"**{task['Company Name']}**")
                st.write(f"Task #{task['Task ID']} | {task['Task Type']} | {task['Document Type']}")
                st.write(task['Description'][:100] + "..." if len(task['Description']) > 100 else task['Description'])
            
            with col2:
                st.write(f"**Assigned to:** {task['Assigned User']}")
                st.write(f"**Created:** {task['Created Date'].strftime('%Y-%m-%d')}")
                st.write(f"**Due:** {task['Due Date'].strftime('%Y-%m-%d')}")
            
            with col3:
                status_class = f"status-{task['Status'].lower().replace(' ', '-')}"
                st.markdown(f'<span class="status-badge {status_class}">{task["Status"]}</span>', unsafe_allow_html=True)
            
            with col4:
                priority_class = f"priority-{task['Priority'].lower()}"
                st.markdown(f'<span class="status-badge {priority_class}">{task["Priority"]}</span>', unsafe_allow_html=True)
                
                if task['Assigned User'] == 'Unassigned' and view_type == 'New Tasks':
                    if st.button("Assign to Me", key=f"assign_{task['Task ID']}"):
                        task['Assigned User'] = st.session_state.current_user
                        task['Status'] = 'In Progress'
                        st.success(f"Task {task['Task ID']} assigned to you!")
                        st.rerun()
            
            st.markdown("---")

def render_get_task_modal():
    """Modal for getting new tasks"""
    with st.form("get_task_form"):
        st.subheader("🎯 Get New Task")
        
        available_tasks = get_new_available_tasks()
        
        if not available_tasks:
            st.info("No new tasks available at the moment.")
            if st.form_submit_button("Close"):
                st.session_state.show_get_task_modal = False
                st.rerun()
            return
        
        # Show available tasks
        selected_task_id = st.selectbox(
            "Select a task to assign:",
            options=[task['Task ID'] for task in available_tasks],
            format_func=lambda x: f"Task {x}: {next(task['Company Name'] for task in available_tasks if task['Task ID'] == x)}"
        )
        
        selected_task = next(task for task in available_tasks if task['Task ID'] == selected_task_id)
        
        st.write("**Task Details:**")
        st.write(f"**Company:** {selected_task['Company Name']}")
        st.write(f"**Type:** {selected_task['Task Type']} | {selected_task['Document Type']}")
        st.write(f"**Priority:** {selected_task['Priority']}")
        st.write(f"**Description:** {selected_task['Description']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("✅ Assign to Me", use_container_width=True):
                selected_task['Assigned User'] = st.session_state.current_user
                selected_task['Status'] = 'In Progress'
                st.session_state.show_get_task_modal = False
                st.success("Task assigned successfully!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.show_get_task_modal = False
                st.rerun()

def render_new_task_modal():
    """Modal for creating new tasks"""
    with st.form("new_task_form"):
        st.subheader("➕ Create New Task")
        
        col1, col2 = st.columns(2)
        
        with col1:
            task_type = st.selectbox("Task Type", ["Tier I", "Tier II", "Tier III"])
            company_name = st.text_input("Company Name")
            document_type = st.selectbox("Document Type", ["10-Q", "10-K", "8-K", "S-1", "DEF 14A", "Other"])
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        with col2:
            assigned_user = st.selectbox("Assign To", ["Unassigned"] + st.session_state.analysts)
            due_date = st.date_input("Due Date", value=date.today() + timedelta(days=14))
            description = st.text_area("Description")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("✅ Create Task", use_container_width=True):
                # Create new task
                task_id = max([task['Task ID'] for task in st.session_state.tasks]) + 1 if st.session_state.tasks else 1300
                
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
                    'Source': 'Manual Creation'
                }
                
                st.session_state.tasks.append(new_task)
                st.session_state.show_new_task_modal = False
                st.success("Task created successfully!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.show_new_task_modal = False
                st.rerun()

# =========================
# DATA IMPORT PAGE
# =========================

def render_data_import():
    st.header("📁 Data Import")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📧 Email Import")
        
        email_file = st.file_uploader("Upload .eml file", type=['eml'], key="email_upload")
        
        if email_file:
            if st.button("Process Email", use_container_width=True):
                with st.spinner("Processing email..."):
                    if process_email_file(email_file):
                        st.success("Email processed successfully! Task created.")
                    else:
                        st.error("Failed to process email.")
    
    with col2:
        st.subheader("📊 Excel Import")
        
        excel_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'], key="excel_upload")
        
        if excel_file:
            if st.button("Create Tasks from Excel", use_container_width=True):
                with st.spinner("Processing Excel file..."):
                    task_count = create_task_from_excel(excel_file)
                    if task_count > 0:
                        st.success(f"Created {task_count} new tasks from Excel!")
                    else:
                        st.error("Failed to create tasks from Excel.")
    
    # Current tasks overview
    st.subheader("📋 Current Tasks Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tasks = len(st.session_state.tasks)
        st.metric("Total Tasks", total_tasks)
    
    with col2:
        new_tasks = len(get_new_available_tasks())
        st.metric("New Tasks", new_tasks)
    
    with col3:
        in_progress = len([t for t in st.session_state.tasks if t['Status'] == 'In Progress'])
        st.metric("In Progress", in_progress)
    
    with col4:
        completed = len([t for t in st.session_state.tasks if t['Status'] == 'Completed'])
        st.metric("Completed", completed)
    
    # Recent tasks
    st.subheader("Recent Tasks")
    recent_tasks = sorted(st.session_state.tasks, key=lambda x: x['Created Date'], reverse=True)[:10]
    render_task_table(recent_tasks, "Recent")

# =========================
# ANALYTICS DASHBOARD
# =========================

def render_dashboard():
    st.header("📊 Analytics Dashboard")
    
    # Ensure we have tasks data
    if not st.session_state.tasks:
        st.info("No tasks data available. Please import data or create tasks first.")
        return
    
    # Convert tasks to DataFrame safely
    try:
        tasks_df = pd.DataFrame(st.session_state.tasks)
        
        # Quick metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tasks = len(tasks_df)
            st.metric("Total Tasks", total_tasks)
        
        with col2:
            completed_tasks = len(tasks_df[tasks_df['Status'] == 'Completed'])
            st.metric("Completed", completed_tasks)
        
        with col3:
            in_progress_tasks = len(tasks_df[tasks_df['Status'] == 'In Progress'])
            st.metric("In Progress", in_progress_tasks)
        
        with col4:
            high_priority_tasks = len(tasks_df[tasks_df['Priority'] == 'High'])
            st.metric("High Priority", high_priority_tasks)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Task status distribution
            if 'Status' in tasks_df.columns:
                status_counts = tasks_df['Status'].value_counts()
                fig1 = px.pie(values=status_counts.values, names=status_counts.index, 
                             title="Task Status Distribution")
                st.plotly_chart(fig1, use_container_width=True)
            
            # Priority distribution
            if 'Priority' in tasks_df.columns:
                priority_counts = tasks_df['Priority'].value_counts()
                fig3 = px.bar(x=priority_counts.index, y=priority_counts.values,
                             title="Tasks by Priority", color=priority_counts.index,
                             color_discrete_map={'High': '#e74c3c', 'Medium': '#f39c12', 'Low': '#27ae60'})
                st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Tasks by user
            if 'Assigned User' in tasks_df.columns:
                user_counts = tasks_df['Assigned User'].value_counts()
                fig2 = px.bar(y=user_counts.index, x=user_counts.values, orientation='h',
                             title="Tasks by User", color=user_counts.values)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Task type distribution
            if 'Task Type' in tasks_df.columns:
                type_counts = tasks_df['Task Type'].value_counts()
                fig4 = px.pie(values=type_counts.values, names=type_counts.index,
                             title="Tasks by Type")
                st.plotly_chart(fig4, use_container_width=True)
        
        # Performance metrics
        st.subheader("Performance Analytics")
        
        # Generate time series data
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        performance_data = []
        
        for i, day in enumerate(dates):
            performance_data.append({
                'Date': day,
                'Tasks Completed': np.random.randint(2, 15),
                'Tasks Created': np.random.randint(5, 20),
                'Avg Completion Time (hrs)': np.random.uniform(4, 12)
            })
        
        perf_df = pd.DataFrame(performance_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=perf_df['Date'], y=perf_df['Tasks Completed'], 
                                name='Tasks Completed', line=dict(color='#4caf50')))
        fig.add_trace(go.Scatter(x=perf_df['Date'], y=perf_df['Tasks Created'], 
                                name='Tasks Created', line=dict(color='#2196f3')))
        fig.add_trace(go.Scatter(x=perf_df['Date'], y=perf_df['Avg Completion Time (hrs)'], 
                                name='Avg Completion Time', line=dict(color='#ff9800'), yaxis='y2'))
        
        fig.update_layout(
            title='30-Day Performance Trends',
            yaxis=dict(title='Number of Tasks'),
            yaxis2=dict(title='Hours', overlaying='y', side='right'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error generating analytics: {str(e)}")
        st.info("Please ensure your tasks data is properly formatted.")

# =========================
# ANALYST METRICS PAGE
# =========================

def render_analyst_metrics():
    st.header("👥 Analyst Performance Metrics")
    
    if not st.session_state.tasks:
        st.info("No tasks data available.")
        return
    
    tasks_df = pd.DataFrame(st.session_state.tasks)
    
    # Analyst performance summary
    st.subheader("Analyst Performance Summary")
    
    analyst_stats = []
    for analyst in st.session_state.analysts:
        analyst_tasks = tasks_df[tasks_df['Assigned User'] == analyst]
        total_tasks = len(analyst_tasks)
        completed_tasks = len(analyst_tasks[analyst_tasks['Status'] == 'Completed'])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        analyst_stats.append({
            'Analyst': analyst,
            'Total Tasks': total_tasks,
            'Completed': completed_tasks,
            'Completion Rate': f"{completion_rate:.1f}%",
            'Avg Completion Time': f"{np.random.uniform(2, 8):.1f} days"
        })
    
    stats_df = pd.DataFrame(analyst_stats)
    st.dataframe(stats_df, use_container_width=True)
    
    # Performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(stats_df, x='Analyst', y='Total Tasks', 
                     title='Tasks per Analyst', color='Total Tasks')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        completion_rates = stats_df.copy()
        completion_rates['Completion Rate Num'] = completion_rates['Completion Rate'].str.rstrip('%').astype(float)
        fig2 = px.bar(completion_rates, x='Analyst', y='Completion Rate Num',
                     title='Completion Rate by Analyst', color='Completion Rate Num')
        st.plotly_chart(fig2, use_container_width=True)

# =========================
# MAIN APPLICATION
# =========================

def main():
    # Render top navigation
    render_top_navigation()
    
    # Render current page
    if st.session_state.current_page == "Task Management":
        render_task_management()
    elif st.session_state.current_page == "Analytics Dashboard":
        render_dashboard()
    elif st.session_state.current_page == "Data Import":
        render_data_import()
    elif st.session_state.current_page == "Analyst Metrics":
        render_analyst_metrics()

if __name__ == "__main__":
    main()
