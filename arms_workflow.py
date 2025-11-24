# appian_style_task_manager.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import io
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="ARMS Task Management System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# CUSTOM CSS - Appian Style
# =========================

st.markdown("""
<style>
    /* Appian-like styling */
    .main-header {
        font-size: 2.2rem;
        background: linear-gradient(135deg, #0052cc 0%, #0747a6 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    
    .appian-card {
        background: white;
        border: 1px solid #dde1e6;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .task-table {
        background: white;
        border: 1px solid #dde1e6;
        border-radius: 6px;
        overflow: hidden;
    }
    
    .status-in-progress {
        background: #ffeb3b;
        color: #333;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-completed {
        background: #4caf50;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-pending {
        background: #ff9800;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .priority-high {
        background: #f44336;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .priority-medium {
        background: #ff9800;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .priority-low {
        background: #4caf50;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .filter-bar {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #dde1e6;
        margin-bottom: 1rem;
    }
    
    .new-task-btn {
        background: #0747a6;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .pagination {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        background: #f8f9fa;
        border-top: 1px solid #dde1e6;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================

if 'tasks' not in st.session_state:
    # Sample task data matching Appian screenshot
    st.session_state.tasks = [
        {
            'Task ID': 1270, 'Task Type': 'Tier I', 'Company Name': 'US Foods Holding Corp.',
            'Document Type': '10-Q', 'Priority': 'High', 'Status': 'In Progress',
            'Completed DateTime': '-', 'Assigned User': 'Ayushi Chandel'
        },
        {
            'Task ID': 1269, 'Task Type': 'Tier II', 'Company Name': 'Medline Inc.- P/E 2022',
            'Document Type': '10-K', 'Priority': 'High', 'Status': 'Completed',
            'Completed DateTime': 'November 21, 2025 2:28 PM', 'Assigned User': 'Komal Khamar'
        },
        {
            'Task ID': 1268, 'Task Type': 'Tier II', 'Company Name': 'Medline Inc.- 2Q',
            'Document Type': '10-Q', 'Priority': 'High', 'Status': 'Completed',
            'Completed DateTime': 'November 21, 2025 2:20 PM', 'Assigned User': 'Komal Khamar'
        },
        {
            'Task ID': 1267, 'Task Type': 'Tier II', 'Company Name': 'Medline Inc.- 2Q',
            'Document Type': '10-Q', 'Priority': 'High', 'Status': 'Completed',
            'Completed DateTime': 'November 21, 2025 2:06 PM', 'Assigned User': 'Komal Khamar'
        },
        {
            'Task ID': 1266, 'Task Type': 'Tier II', 'Company Name': 'Medline Inc.- P/E 2023',
            'Document Type': '10-K', 'Priority': 'High', 'Status': 'Completed',
            'Completed DateTime': 'November 21, 2025 1:55 PM', 'Assigned User': 'Komal Khamar'
        },
        {
            'Task ID': 1265, 'Task Type': 'Tier II', 'Company Name': 'Medline Inc.- P/E 2024',
            'Document Type': '10-K', 'Priority': 'High', 'Status': 'Completed',
            'Completed DateTime': 'November 21, 2025 1:06 PM', 'Assigned User': 'Komal Khamar'
        },
        {
            'Task ID': 1264, 'Task Type': 'Tier II', 'Company Name': 'Soléero',
            'Document Type': '10-K', 'Priority': 'High', 'Status': 'Completed',
            'Completed DateTime': 'November 21, 2025 1:15 AM', 'Assigned User': 'Komal Khamar'
        },
        {
            'Task ID': 1263, 'Task Type': 'Tier II', 'Company Name': 'Bath & Body Works, Inc.',
            'Document Type': '10-Q', 'Priority': 'Low', 'Status': 'Completed',
            'Completed DateTime': 'November 21, 2025 6:04 AM', 'Assigned User': 'Komal Khamar'
        },
        {
            'Task ID': 1262, 'Task Type': 'Tier II', 'Company Name': 'Ace Hardware',
            'Document Type': '10-Q', 'Priority': 'High', 'Status': 'Completed',
            'Completed DateTime': 'November 21, 2025 6:29 AM', 'Assigned User': 'Komal Khamar'
        },
        {
            'Task ID': 1261, 'Task Type': 'Tier I', 'Company Name': 'Medline Inc.',
            'Document Type': '', 'Priority': 'High', 'Status': 'Completed',
            'Completed DateTime': 'November 21, 2025 6:16 AM', 'Assigned User': 'Ayushi Chandel'
        }
    ]

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Task Management"

if 'task_filters' not in st.session_state:
    st.session_state.task_filters = {
        'view': 'All Tasks',
        'search': '',
        'task_type': 'Any',
        'priority': 'Any',
        'status': 'Any',
        'assigned_user': 'Any'
    }

if 'current_user' not in st.session_state:
    st.session_state.current_user = "Nisarg Thakker"

# =========================
# SAMPLE DATA GENERATION
# =========================

def generate_sample_tasks(count=1240):
    """Generate large sample dataset matching Appian style"""
    companies = [
        'US Foods Holding Corp.', 'Medline Inc.', 'Soléero', 'Bath & Body Works, Inc.', 
        'Ace Hardware', 'Walmart Inc.', 'Amazon.com Inc.', 'Microsoft Corporation',
        'Apple Inc.', 'Google LLC', 'Tesla Inc.', 'Johnson & Johnson'
    ]
    
    document_types = ['10-Q', '10-K', '8-K', 'S-1', 'DEF 14A']
    task_types = ['Tier I', 'Tier II', 'Tier III']
    priorities = ['High', 'Medium', 'Low']
    statuses = ['In Progress', 'Completed', 'Pending Review', 'Not Started']
    users = ['Ayushi Chandel', 'Komal Khamar', 'Nisarg Thakker', 'Jen Shears', 'Rondrea Carroll']
    
    tasks = []
    for i in range(count):
        task_id = 1270 - i
        company = np.random.choice(companies)
        task_type = np.random.choice(task_types)
        doc_type = np.random.choice(document_types) if task_type != 'Tier I' else ''
        priority = np.random.choice(priorities, p=[0.6, 0.3, 0.1])
        status = np.random.choice(statuses, p=[0.3, 0.5, 0.1, 0.1])
        user = np.random.choice(users)
        
        completed_dt = ''
        if status == 'Completed':
            days_ago = np.random.randint(1, 30)
            hours = np.random.randint(0, 23)
            minutes = np.random.randint(0, 59)
            completed_date = datetime.now() - timedelta(days=days_ago, hours=hours, minutes=minutes)
            completed_dt = completed_date.strftime('%B %d, %Y %I:%M %p')
        
        tasks.append({
            'Task ID': task_id,
            'Task Type': task_type,
            'Company Name': company,
            'Document Type': doc_type,
            'Priority': priority,
            'Status': status,
            'Completed DateTime': completed_dt,
            'Assigned User': user
        })
    
    return tasks

# =========================
# TASK MANAGEMENT PAGE
# =========================

def render_task_management():
    st.markdown('<div class="main-header">ARMS Task Management System</div>', unsafe_allow_html=True)
    
    # View selector and New Task button
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        view_options = ["My Tasks", "All Tasks"]
        selected_view = st.radio("", view_options, horizontal=True, 
                               index=view_options.index(st.session_state.task_filters['view']),
                               label_visibility="collapsed")
        st.session_state.task_filters['view'] = selected_view
    
    with col3:
        if st.button("➕ NEW TASK", use_container_width=True):
            st.session_state.show_new_task = True
    
    # Filter bar
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    st.write("**Search Task information**")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        search_term = st.text_input("Search", value=st.session_state.task_filters['search'], 
                                  placeholder="Search tasks...", label_visibility="collapsed")
        st.session_state.task_filters['search'] = search_term
    
    with col2:
        task_type = st.selectbox("Task Type", ["Any", "Tier I", "Tier II", "Tier III"], 
                               index=0, label_visibility="collapsed")
        st.session_state.task_filters['task_type'] = task_type
    
    with col3:
        priority = st.selectbox("Priority", ["Any", "High", "Medium", "Low"], 
                              index=0, label_visibility="collapsed")
        st.session_state.task_filters['priority'] = priority
    
    with col4:
        status = st.selectbox("Status", ["Any", "In Progress", "Completed", "Pending Review", "Not Started"], 
                            index=0, label_visibility="collapsed")
        st.session_state.task_filters['status'] = status
    
    with col5:
        users = ["Any", "Ayushi Chandel", "Komal Khamar", "Nisarg Thakker", "Jen Shears", "Rondrea Carroll"]
        assigned_user = st.selectbox("Assigned User", users, index=0, label_visibility="collapsed")
        st.session_state.task_filters['assigned_user'] = assigned_user
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_tasks = filter_tasks(st.session_state.tasks)
    
    # Display tasks table
    render_task_table(filtered_tasks)
    
    # New Task Modal
    if st.session_state.get('show_new_task', False):
        render_new_task_modal()

def filter_tasks(tasks):
    """Apply filters to tasks"""
    filtered = tasks.copy()
    
    # View filter
    if st.session_state.task_filters['view'] == 'My Tasks':
        filtered = [task for task in filtered if task['Assigned User'] == st.session_state.current_user]
    
    # Search filter
    if st.session_state.task_filters['search']:
        search_term = st.session_state.task_filters['search'].lower()
        filtered = [task for task in filtered if 
                   search_term in str(task['Task ID']).lower() or
                   search_term in task['Company Name'].lower() or
                   search_term in task['Document Type'].lower()]
    
    # Task Type filter
    if st.session_state.task_filters['task_type'] != 'Any':
        filtered = [task for task in filtered if task['Task Type'] == st.session_state.task_filters['task_type']]
    
    # Priority filter
    if st.session_state.task_filters['priority'] != 'Any':
        filtered = [task for task in filtered if task['Priority'] == st.session_state.task_filters['priority']]
    
    # Status filter
    if st.session_state.task_filters['status'] != 'Any':
        filtered = [task for task in filtered if task['Status'] == st.session_state.task_filters['status']]
    
    # Assigned User filter
    if st.session_state.task_filters['assigned_user'] != 'Any':
        filtered = [task for task in filtered if task['Assigned User'] == st.session_state.task_filters['assigned_user']]
    
    return filtered

def render_task_table(tasks):
    """Render the task table with Appian styling"""
    if not tasks:
        st.info("No tasks found matching your filters.")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(tasks)
    
    # Apply styling
    def style_status(val):
        if val == 'In Progress':
            return 'status-in-progress'
        elif val == 'Completed':
            return 'status-completed'
        else:
            return 'status-pending'
    
    def style_priority(val):
        if val == 'High':
            return 'priority-high'
        elif val == 'Medium':
            return 'priority-medium'
        else:
            return 'priority-low'
    
    # Display the table
    st.markdown('<div class="task-table">', unsafe_allow_html=True)
    
    # Create HTML table with custom styling
    html = """
    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background: #f8f9fa; border-bottom: 2px solid #dde1e6;">
                <th style="padding: 12px; text-align: left; font-weight: 600;">Task ID</th>
                <th style="padding: 12px; text-align: left; font-weight: 600;">Task Type</th>
                <th style="padding: 12px; text-align: left; font-weight: 600;">Company Name</th>
                <th style="padding: 12px; text-align: left; font-weight: 600;">Document Type</th>
                <th style="padding: 12px; text-align: left; font-weight: 600;">Priority</th>
                <th style="padding: 12px; text-align: left; font-weight: 600;">Status</th>
                <th style="padding: 12px; text-align: left; font-weight: 600;">Completed Date Time</th>
                <th style="padding: 12px; text-align: left; font-weight: 600;">Assigned User</th>
                <th style="padding: 12px; text-align: left; font-weight: 600;">Actions</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for _, task in df.iterrows():
        status_class = style_status(task['Status'])
        priority_class = style_priority(task['Priority'])
        
        html += f"""
        <tr style="border-bottom: 1px solid #dde1e6;">
            <td style="padding: 12px;">{task['Task ID']}</td>
            <td style="padding: 12px;">{task['Task Type']}</td>
            <td style="padding: 12px;">{task['Company Name']}</td>
            <td style="padding: 12px;">{task['Document Type']}</td>
            <td style="padding: 12px;"><span class="{priority_class}">{task['Priority']}</span></td>
            <td style="padding: 12px;"><span class="{status_class}">{task['Status']}</span></td>
            <td style="padding: 12px;">{task['Completed DateTime']}</td>
            <td style="padding: 12px;">{task['Assigned User']}</td>
            <td style="padding: 12px;">
                <button style="background: #0747a6; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem;">
                    Task Summary
                </button>
            </td>
        </tr>
        """
    
    html += """
        </tbody>
    </table>
    """
    
    st.markdown(html, unsafe_allow_html=True)
    
    # Pagination
    st.markdown('<div class="pagination">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.write(f"<span style='color: #666;'>&lt; ←</span>", unsafe_allow_html=True)
    
    with col2:
        st.write(f"<span style='color: #666; text-align: center;'>10 of {len(tasks)}</span>", unsafe_allow_html=True)
    
    with col3:
        st.write(f"<span style='color: #666;'>→ &gt;</span>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_new_task_modal():
    """Render new task creation modal"""
    with st.form("new_task_form"):
        st.subheader("Create New Task")
        
        col1, col2 = st.columns(2)
        
        with col1:
            task_type = st.selectbox("Task Type", ["Tier I", "Tier II", "Tier III"])
            company_name = st.text_input("Company Name")
            document_type = st.selectbox("Document Type", ["10-Q", "10-K", "8-K", "S-1", "DEF 14A", ""])
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        with col2:
            status = st.selectbox("Status", ["Not Started", "In Progress", "Pending Review"])
            assigned_user = st.selectbox("Assign To", ["Ayushi Chandel", "Komal Khamar", "Nisarg Thakker", "Jen Shears", "Rondrea Carroll"])
            due_date = st.date_input("Due Date")
            description = st.text_area("Description")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Create Task", use_container_width=True):
                # Create new task
                new_task_id = max([task['Task ID'] for task in st.session_state.tasks]) + 1
                new_task = {
                    'Task ID': new_task_id,
                    'Task Type': task_type,
                    'Company Name': company_name,
                    'Document Type': document_type,
                    'Priority': priority,
                    'Status': status,
                    'Completed DateTime': '',
                    'Assigned User': assigned_user
                }
                st.session_state.tasks.append(new_task)
                st.session_state.show_new_task = False
                st.success("Task created successfully!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.show_new_task = False
                st.rerun()

# =========================
# DASHBOARD & ANALYTICS PAGE
# =========================

def render_dashboard():
    st.markdown('<div class="main-header">ARMS Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Quick metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_tasks = len(st.session_state.tasks)
    completed_tasks = len([t for t in st.session_state.tasks if t['Status'] == 'Completed'])
    in_progress_tasks = len([t for t in st.session_state.tasks if t['Status'] == 'In Progress'])
    high_priority_tasks = len([t for t in st.session_state.tasks if t['Priority'] == 'High'])
    
    with col1:
        st.metric("Total Tasks", total_tasks)
    with col2:
        st.metric("Completed", completed_tasks)
    with col3:
        st.metric("In Progress", in_progress_tasks)
    with col4:
        st.metric("High Priority", high_priority_tasks)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Task status distribution
        status_counts = pd.DataFrame(st.session_state.tasks)['Status'].value_counts()
        fig1 = px.pie(values=status_counts.values, names=status_counts.index, 
                     title="Task Status Distribution")
        st.plotly_chart(fig1, use_container_width=True)
        
        # Priority distribution
        priority_counts = pd.DataFrame(st.session_state.tasks)['Priority'].value_counts()
        fig3 = px.bar(x=priority_counts.index, y=priority_counts.values,
                     title="Tasks by Priority", color=priority_counts.index,
                     color_discrete_map={'High': '#f44336', 'Medium': '#ff9800', 'Low': '#4caf50'})
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Tasks by user
        user_counts = pd.DataFrame(st.session_state.tasks)['Assigned User'].value_counts()
        fig2 = px.bar(y=user_counts.index, x=user_counts.values, orientation='h',
                     title="Tasks by User", color=user_counts.values)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Task type distribution
        type_counts = pd.DataFrame(st.session_state.tasks)['Task Type'].value_counts()
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
            'Tasks Completed': np.random.randint(5, 20),
            'Tasks Created': np.random.randint(8, 25),
            'Avg Completion Time (hrs)': np.random.uniform(2, 8)
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
    
    # Detailed analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Task Completion Rate")
        
        # Calculate completion rates by user
        user_stats = []
        for user in pd.DataFrame(st.session_state.tasks)['Assigned User'].unique():
            user_tasks = [t for t in st.session_state.tasks if t['Assigned User'] == user]
            completed = len([t for t in user_tasks if t['Status'] == 'Completed'])
            total = len(user_tasks)
            completion_rate = (completed / total * 100) if total > 0 else 0
            
            user_stats.append({
                'User': user,
                'Completion Rate': round(completion_rate, 1),
                'Total Tasks': total,
                'Completed': completed
            })
        
        user_stats_df = pd.DataFrame(user_stats)
        st.dataframe(user_stats_df, use_container_width=True)
    
    with col2:
        st.subheader("SLA Compliance")
        
        # Mock SLA data
        sla_data = []
        for task_type in ['Tier I', 'Tier II', 'Tier III']:
            sla_data.append({
                'Task Type': task_type,
                'SLA Target': '24 hours',
                'Actual Avg': f"{np.random.uniform(18, 30):.1f} hours",
                'Compliance %': f"{np.random.uniform(85, 98):.1f}%"
            })
        
        sla_df = pd.DataFrame(sla_data)
        st.dataframe(sla_df, use_container_width=True)

# =========================
# MAIN APPLICATION
# =========================

def main():
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #0052cc 0%, #0747a6 100%); 
                    color: white; border-radius: 8px; margin-bottom: 2rem;">
            <h3>ARMS System</h3>
            <p style="margin: 0; opacity: 0.8;">{st.session_state.current_user}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        page_options = ["📋 Task Management", "📊 Analytics Dashboard"]
        selected_page = st.radio("Navigate to", page_options)
        
        # Update current page
        if "Task Management" in selected_page:
            st.session_state.current_page = "Task Management"
        else:
            st.session_state.current_page = "Analytics Dashboard"
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("Quick Actions")
        if st.button("🔄 Generate Sample Data", use_container_width=True):
            st.session_state.tasks = generate_sample_tasks(1240)
            st.success("Generated 1240 sample tasks!")
            st.rerun()
        
        if st.button("📥 Export Tasks", use_container_width=True):
            export_tasks()
        
        st.markdown("---")
        
        # System info
        st.subheader("System Info")
        st.write(f"**Total Tasks:** {len(st.session_state.tasks)}")
        st.write(f"**Completed:** {len([t for t in st.session_state.tasks if t['Status'] == 'Completed'])}")
        st.write(f"**In Progress:** {len([t for t in st.session_state.tasks if t['Status'] == 'In Progress'])}")
    
    # Render selected page
    if st.session_state.current_page == "Task Management":
        render_task_management()
    else:
        render_dashboard()

def export_tasks():
    """Export tasks to CSV"""
    df = pd.DataFrame(st.session_state.tasks)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"arms_tasks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

if __name__ == "__main__":
    main()
