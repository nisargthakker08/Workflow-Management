import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
import io
import email
from email import policy
from email.parser import BytesParser
import re

# Set page configuration
st.set_page_config(
    page_title="ARMS Workflow Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=[
        'Task_ID', 'Task_Description', 'Priority', 'Status', 'Assigned_To', 
        'Created_Date', 'Due_Date', 'SLA_Days', 'Department', 'Complexity', 
        'Estimated_Hours', 'Actual_Hours', 'Completion_Date'
    ])

if 'achieved_data' not in st.session_state:
    st.session_state.achieved_data = pd.DataFrame()

if 'current_user' not in st.session_state:
    st.session_state.current_user = "Nisarg Thakker"

# Correct Analyst Names including Nisarg
ANALYSTS = [
    "Nisarg Thakker", "Alex Johnson", "Maria Garcia", "David Chen", "Sarah Williams",
    "James Brown", "Lisa Anderson", "Robert Taylor", "Emily Clark",
    "Michael Lee", "Jennifer Martinez", "Christopher Davis", "Amanda Rodriguez",
    "Daniel Wilson", "Jessica Thompson"
]

def create_sample_tasks():
    """Create sample tasks for demonstration"""
    sample_tasks = []
    for i in range(1, 151):
        task = {
            'Task_ID': f'TASK-{i:04d}',
            'Task_Description': f'Sample Task Description {i} for workflow processing',
            'Priority': np.random.choice(['Low', 'Medium', 'High', 'Critical'], p=[0.3, 0.4, 0.2, 0.1]),
            'Status': np.random.choice(['Pending', 'In Progress', 'Completed', 'On Hold'], p=[0.3, 0.2, 0.4, 0.1]),
            'Assigned_To': np.random.choice(ANALYSTS) if np.random.random() > 0.4 else 'Unassigned',
            'Created_Date': datetime.now() - timedelta(days=np.random.randint(1, 30)),
            'Due_Date': datetime.now() + timedelta(days=np.random.randint(1, 60)),
            'SLA_Days': np.random.randint(1, 30),
            'Department': np.random.choice(['Finance', 'HR', 'IT', 'Operations', 'Marketing']),
            'Complexity': np.random.choice(['Low', 'Medium', 'High']),
            'Estimated_Hours': np.random.randint(1, 24),
            'Actual_Hours': np.random.randint(1, 24) if np.random.random() > 0.5 else None,
            'Completion_Date': datetime.now() - timedelta(days=np.random.randint(1, 15)) if np.random.random() > 0.6 else None
        }
        sample_tasks.append(task)
    return pd.DataFrame(sample_tasks)

def render_top_navigation():
    """Render the top navigation bar"""
    st.markdown("""
        <style>
        .top-nav {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .nav-title {
            color: white;
            font-size: 1.8rem;
            font-weight: bold;
            text-align: center;
            margin: 0;
        }
        .nav-subtitle {
            color: rgba(255, 255, 255, 0.9);
            text-align: center;
            margin: 0;
            font-size: 1rem;
        }
        </style>
        <div class="top-nav">
            <div class="nav-title">🚀 ARMS Workflow Management System</div>
            <div class="nav-subtitle">Ultimate Task Management System</div>
        </div>
    """, unsafe_allow_html=True)

def render_task_management():
    """Render the task management page"""
    st.header("📋 Task Management")
    
    # Initialize sample data if empty
    if st.session_state.tasks.empty:
        st.session_state.tasks = create_sample_tasks()
    
    # Task Overview Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Get New Task - unassigned tasks
        new_tasks_count = len(st.session_state.tasks[
            (st.session_state.tasks['Status'] == 'Pending') & 
            (st.session_state.tasks['Assigned_To'] == 'Unassigned')
        ])
        st.metric("Get New Task", new_tasks_count)
    
    with col2:
        # My Tasks - tasks assigned to current user
        my_tasks_count = len(st.session_state.tasks[
            (st.session_state.tasks['Assigned_To'] == st.session_state.current_user) &
            (st.session_state.tasks['Status'].isin(['In Progress', 'Pending']))
        ])
        st.metric("My Tasks", my_tasks_count)
    
    with col3:
        total_tasks = len(st.session_state.tasks)
        st.metric("Total Tasks", total_tasks)
    
    with col4:
        if st.button("Create Task", use_container_width=True):
            st.info("Task creation modal would open here")
    
    # Last Assigned Task Summary
    st.subheader("Last Assigned Task Summary")
    user_tasks = st.session_state.tasks[
        st.session_state.tasks['Assigned_To'] == st.session_state.current_user
    ]
    
    if not user_tasks.empty:
        latest_task = user_tasks.sort_values('Created_Date', ascending=False).iloc[0]
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**Task ID:** {latest_task['Task_ID']}")
            st.write(f"**Description:** {latest_task['Task_Description']}")
        
        with col2:
            st.write(f"**Priority:** {latest_task['Priority']}")
            st.write(f"**Status:** {latest_task['Status']}")
        
        with col3:
            st.write(f"**Due Date:** {latest_task['Due_Date'].strftime('%Y-%m-%d')}")
            st.write(f"**SLA Days:** {latest_task['SLA_Days']}")
    else:
        st.info("No tasks assigned to you yet.")
    
    # Task Actions
    st.subheader("Available Tasks")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=['All', 'Pending', 'In Progress', 'Completed', 'On Hold']
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority",
            options=['All', 'Low', 'Medium', 'High', 'Critical']
        )
    
    with col3:
        show_my_tasks = st.checkbox("Show Only My Tasks", value=True)
    
    # Apply filters
    filtered_tasks = st.session_state.tasks.copy()
    
    if status_filter != 'All':
        filtered_tasks = filtered_tasks[filtered_tasks['Status'] == status_filter]
    
    if priority_filter != 'All':
        filtered_tasks = filtered_tasks[filtered_tasks['Priority'] == priority_filter]
    
    if show_my_tasks:
        filtered_tasks = filtered_tasks[filtered_tasks['Assigned_To'] == st.session_state.current_user]
    
    # Display tasks with action buttons
    for idx, task in filtered_tasks.iterrows():
        # Find the actual index in the main tasks dataframe
        task_idx = st.session_state.tasks[st.session_state.tasks['Task_ID'] == task['Task_ID']].index[0]
        
        with st.expander(f"{task['Task_ID']} - {task['Task_Description'][:50]}..."):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Description:** {task['Task_Description']}")
                st.write(f"**Priority:** {task['Priority']}")
                st.write(f"**Status:** {task['Status']}")
                st.write(f"**Assigned To:** {task['Assigned_To']}")
                st.write(f"**Due Date:** {task['Due_Date'].strftime('%Y-%m-%d')}")
                st.write(f"**Department:** {task['Department']}")
            
            with col2:
                # Action buttons based on status
                if task['Status'] == 'Pending' and task['Assigned_To'] == 'Unassigned':
                    if st.button("Accept Task", key=f"accept_{task_idx}"):
                        st.session_state.tasks.at[task_idx, 'Status'] = 'In Progress'
                        st.session_state.tasks.at[task_idx, 'Assigned_To'] = st.session_state.current_user
                        st.rerun()
                
                elif task['Status'] == 'In Progress' and task['Assigned_To'] == st.session_state.current_user:
                    col2a, col2b = st.columns(2)
                    with col2a:
                        if st.button("Pause", key=f"pause_{task_idx}"):
                            st.session_state.tasks.at[task_idx, 'Status'] = 'On Hold'
                            st.rerun()
                    with col2b:
                        if st.button("Complete", key=f"complete_{task_idx}"):
                            st.session_state.tasks.at[task_idx, 'Status'] = 'Completed'
                            st.session_state.tasks.at[task_idx, 'Completion_Date'] = datetime.now()
                            st.rerun()
                
                elif task['Status'] == 'On Hold' and task['Assigned_To'] == st.session_state.current_user:
                    if st.button("Resume", key=f"resume_{task_idx}"):
                        st.session_state.tasks.at[task_idx, 'Status'] = 'In Progress'
                        st.rerun()
            
            with col3:
                if st.button("View Details", key=f"details_{task_idx}"):
                    st.session_state.selected_task = task
                    st.info(f"Detailed view for {task['Task_ID']}")

def render_analytics():
    """Render the analytics page"""
    st.header("📊 Analytics Dashboard")
    
    # Create sample analytics data
    dates = pd.date_range(start='2024-01-01', end='2024-03-20', freq='D')
    analytics_data = []
    
    for date in dates:
        for analyst in ANALYSTS[:8]:
            analytics_data.append({
                'Date': date,
                'Analyst': analyst,
                'Tasks_Completed': np.random.randint(1, 12),
                'Quality_Score': np.random.uniform(85, 99),
                'SLA_Compliance': np.random.uniform(90, 100),
                'Department': np.random.choice(['Finance', 'HR', 'IT', 'Operations']),
                'Workflow_Type': np.random.choice(['Processing', 'Review', 'Approval', 'Validation'])
            })
    
    df = pd.DataFrame(analytics_data)
    
    # Upload section
    st.subheader("Upload Analytics Data")
    uploaded_file = st.file_uploader("Upload your Excel file with analytics data", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.success(f"✅ Data loaded successfully! {len(df)} rows")
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_range = st.date_input(
            "Date Range",
            value=(df['Date'].min(), df['Date'].max()),
            min_value=df['Date'].min(),
            max_value=df['Date'].max()
        )
    
    with col2:
        analysts = ['All'] + list(df['Analyst'].unique())
        selected_analyst = st.selectbox("Analyst", analysts)
    
    with col3:
        departments = ['All'] + list(df['Department'].unique())
        selected_dept = st.selectbox("Department", departments)
    
    # Apply filters
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df['Date'] >= pd.to_datetime(start_date)) & 
               (df['Date'] <= pd.to_datetime(end_date))]
    
    if selected_analyst != 'All':
        df = df[df['Analyst'] == selected_analyst]
    
    if selected_dept != 'All':
        df = df[df['Department'] == selected_dept]
    
    # Metrics
    st.subheader("Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tasks = df['Tasks_Completed'].sum()
        st.metric("Total Tasks Completed", int(total_tasks))
    
    with col2:
        avg_quality = df['Quality_Score'].mean()
        st.metric("Average Quality Score", f"{avg_quality:.1f}%")
    
    with col3:
        avg_sla = df['SLA_Compliance'].mean()
        st.metric("SLA Compliance", f"{avg_sla:.1f}%")
    
    with col4:
        avg_daily = df.groupby('Date')['Tasks_Completed'].sum().mean()
        st.metric("Avg Daily Tasks", f"{avg_daily:.1f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Analyst performance
        analyst_perf = df.groupby('Analyst')['Tasks_Completed'].sum().reset_index()
        fig = px.bar(analyst_perf, x='Analyst', y='Tasks_Completed', 
                     title="Tasks Completed by Analyst", color='Tasks_Completed')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Daily trend
        daily_trend = df.groupby('Date')['Tasks_Completed'].sum().reset_index()
        fig = px.line(daily_trend, x='Date', y='Tasks_Completed', 
                      title="Daily Task Completion Trend")
        st.plotly_chart(fig, use_container_width=True)

def render_data_import():
    """Render data import page"""
    st.header("📁 Data Import")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📧 Email Import")
        uploaded_eml = st.file_uploader("Upload .eml files", type=['eml'], accept_multiple_files=True)
        if uploaded_eml:
            st.success(f"✅ {len(uploaded_eml)} email files uploaded successfully!")
            for email_file in uploaded_eml:
                st.write(f"📧 {email_file.name}")
    
    with col2:
        st.subheader("📊 Excel Import")
        uploaded_excel = st.file_uploader("Upload Excel files", type=['xlsx', 'xls'], accept_multiple_files=True)
        if uploaded_excel:
            st.success(f"✅ {len(uploaded_excel)} Excel files uploaded successfully!")
            for excel_file in uploaded_excel:
                st.write(f"📊 {excel_file.name}")

def render_team_metrics():
    """Render team metrics page"""
    st.header("👥 Team Metrics")
    
    # Sample team data
    team_data = []
    for analyst in ANALYSTS:
        team_data.append({
            'Analyst': analyst,
            'Tasks_Completed': np.random.randint(50, 200),
            'Quality_Score': np.random.uniform(85, 99),
            'SLA_Compliance': np.random.uniform(88, 100),
            'Avg_Completion_Time_Hours': np.random.uniform(2, 8),
            'Department': np.random.choice(['Finance', 'HR', 'IT', 'Operations'])
        })
    
    df = pd.DataFrame(team_data)
    
    # Display team metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Team Performance")
        for _, analyst in df.iterrows():
            with st.expander(f"{analyst['Analyst']} - {analyst['Department']}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Tasks Completed:** {analyst['Tasks_Completed']}")
                    st.write(f"**Quality Score:** {analyst['Quality_Score']:.1f}%")
                with col_b:
                    st.write(f"**SLA Compliance:** {analyst['SLA_Compliance']:.1f}%")
                    st.write(f"**Avg Time:** {analyst['Avg_Completion_Time_Hours']:.1f}h")
    
    with col2:
        st.subheader("Performance Charts")
        fig = px.bar(df, x='Analyst', y='Tasks_Completed', title="Tasks Completed by Analyst")
        st.plotly_chart(fig, use_container_width=True)

def render_achieved_data():
    """Render achieved data analytics page"""
    st.header("📈 Achieved Data / ARMS Excel Analytics")
    
    st.subheader("Upload Your ARMS Excel Data")
    uploaded_file = st.file_uploader(
        "Upload your achieved data Excel file",
        type=['xlsx', 'xls'],
        key="arms_upload"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.session_state.achieved_data = df
            st.success(f"✅ ARMS data loaded successfully! {len(df)} rows")
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    # Use sample data if no upload
    if st.session_state.achieved_data.empty:
        st.info("📊 Using sample ARMS data. Upload your Excel file for real analytics.")
        # Create comprehensive sample data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        sample_data = []
        for date in dates:
            for workflow in ['Loan Processing', 'Claims Approval', 'Document Verification', 'Risk Assessment']:
                sample_data.append({
                    'Date': date,
                    'Workflow_Type': workflow,
                    'Analyst': np.random.choice(ANALYSTS),
                    'Tasks_Completed': np.random.randint(5, 25),
                    'Avg_Processing_Time_Hours': np.random.uniform(1, 6),
                    'Quality_Score': np.random.uniform(90, 99.5),
                    'SLA_Compliance_Percent': np.random.uniform(95, 100),
                    'Department': np.random.choice(['Finance', 'Operations', 'Risk', 'Customer Service']),
                    'Backlog_Count': np.random.randint(0, 15)
                })
        df = pd.DataFrame(sample_data)
    else:
        df = st.session_state.achieved_data
    
    # Enhanced filtering
    st.subheader("Data Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'Date' in df.columns:
            min_date = df['Date'].min()
            max_date = df['Date'].max()
            date_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="arms_date"
            )
    
    with col2:
        if 'Workflow_Type' in df.columns:
            workflows = ['All'] + list(df['Workflow_Type'].unique())
            selected_workflow = st.selectbox("Workflow Type", workflows)
    
    with col3:
        if 'Analyst' in df.columns:
            analysts = ['All'] + list(df['Analyst'].unique())
            selected_analyst = st.selectbox("Analyst", analysts, key="arms_analyst")
    
    with col4:
        if 'Department' in df.columns:
            depts = ['All'] + list(df['Department'].unique())
            selected_dept = st.selectbox("Department", depts, key="arms_dept")
    
    # Apply filters
    if 'Date' in df.columns and len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df['Date'] >= pd.to_datetime(start_date)) & 
               (df['Date'] <= pd.to_datetime(end_date))]
    
    if selected_workflow != 'All':
        df = df[df['Workflow_Type'] == selected_workflow]
    
    if selected_analyst != 'All':
        df = df[df['Analyst'] == selected_analyst]
    
    if selected_dept != 'All':
        df = df[df['Department'] == selected_dept]
    
    # Key Metrics
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        with col1:
            total_tasks = df['Tasks_Completed'].sum() if 'Tasks_Completed' in df.columns else len(df)
            st.metric("Total Tasks Processed", int(total_tasks))
        
        with col2:
            if 'Quality_Score' in df.columns:
                avg_quality = df['Quality_Score'].mean()
                st.metric("Average Quality Score", f"{avg_quality:.1f}%")
            else:
                st.metric("Data Quality", "N/A")
        
        with col3:
            if 'SLA_Compliance_Percent' in df.columns:
                avg_sla = df['SLA_Compliance_Percent'].mean()
                st.metric("SLA Compliance", f"{avg_sla:.1f}%")
            else:
                st.metric("SLA Compliance", "N/A")
        
        with col4:
            if 'Avg_Processing_Time_Hours' in df.columns:
                avg_time = df['Avg_Processing_Time_Hours'].mean()
                st.metric("Avg Processing Time", f"{avg_time:.1f} hrs")
            else:
                st.metric("Processing Time", "N/A")
                
    except Exception as e:
        st.error(f"Error calculating metrics: {e}")
    
    # Visualizations
    st.subheader("📈 Interactive Analytics")
    
    col1, col2 = st.columns(2)
    
    try:
        with col1:
            if 'Workflow_Type' in df.columns and 'Tasks_Completed' in df.columns:
                workflow_summary = df.groupby('Workflow_Type')['Tasks_Completed'].sum().reset_index()
                fig = px.pie(workflow_summary, values='Tasks_Completed', names='Workflow_Type', 
                            title="Task Distribution by Workflow Type")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Date' in df.columns and 'Tasks_Completed' in df.columns:
                daily_trend = df.groupby('Date')['Tasks_Completed'].sum().reset_index()
                fig = px.area(daily_trend, x='Date', y='Tasks_Completed', 
                             title="Daily Task Completion Trend")
                st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error creating charts: {e}")

def main():
    """Main application function"""
    render_top_navigation()
    
    # Sidebar navigation - matching your requirements exactly
    st.sidebar.title("Navigation")
    
    # User info - removed dropdown, fixed to Nisarg Thakker
    st.sidebar.subheader("Analyst")
    st.sidebar.info("Nisarg Thakker")
    
    # Navigation options
    nav_options = [
        "📋 Task Management",
        "📊 Analytics", 
        "📁 Data Import",
        "👥 Team Metrics",
        "📈 Achieved Data / ARMS Excel"
    ]
    
    selected_nav = st.sidebar.radio("Go to", nav_options)
    
    # Render selected page
    if selected_nav == "📋 Task Management":
        render_task_management()
    elif selected_nav == "📊 Analytics":
        render_analytics()
    elif selected_nav == "📁 Data Import":
        render_data_import()
    elif selected_nav == "👥 Team Metrics":
        render_team_metrics()
    elif selected_nav == "📈 Achieved Data / ARMS Excel":
        render_achieved_data()

if __name__ == "__main__":
    main()
