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
    st.session_state.current_user = "Analyst 1"

# Correct Analyst Names
ANALYSTS = [
    "Alex Johnson", "Maria Garcia", "David Chen", "Sarah Williams",
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
            'Task_Description': f'Sample Task Description {i}',
            'Priority': np.random.choice(['Low', 'Medium', 'High', 'Critical'], p=[0.3, 0.4, 0.2, 0.1]),
            'Status': np.random.choice(['Pending', 'In Progress', 'Completed', 'On Hold'], p=[0.2, 0.3, 0.4, 0.1]),
            'Assigned_To': np.random.choice(ANALYSTS) if np.random.random() > 0.3 else 'Unassigned',
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
            <div class="nav-title">ARMS Workflow Management</div>
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
        my_tasks_count = len(st.session_state.tasks[
            st.session_state.tasks['Assigned_To'] == st.session_state.current_user
        ])
        st.metric("My Tasks", my_tasks_count)
    
    with col2:
        total_tasks = len(st.session_state.tasks)
        st.metric("Total Tasks", total_tasks)
    
    with col3:
        pending_tasks = len(st.session_state.tasks[st.session_state.tasks['Status'] == 'Pending'])
        st.metric("Pending Tasks", pending_tasks)
    
    with col4:
        st.button("Create New Task", use_container_width=True)
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect(
            "Status",
            options=['Pending', 'In Progress', 'Completed', 'On Hold'],
            default=['Pending', 'In Progress']
        )
    
    with col2:
        priority_filter = st.multiselect(
            "Priority",
            options=['Low', 'Medium', 'High', 'Critical'],
            default=['Low', 'Medium', 'High', 'Critical']
        )
    
    with col3:
        date_filter = st.selectbox(
            "Date Filter",
            options=['All', 'Today', 'Last 7 Days', 'Last 30 Days', 'Custom Range']
        )
    
    with col4:
        analyst_filter = st.multiselect(
            "Assigned To",
            options=ANALYSTS + ['Unassigned'],
            default=ANALYSTS + ['Unassigned']
        )
    
    # Apply filters
    filtered_tasks = st.session_state.tasks.copy()
    if status_filter:
        filtered_tasks = filtered_tasks[filtered_tasks['Status'].isin(status_filter)]
    if priority_filter:
        filtered_tasks = filtered_tasks[filtered_tasks['Priority'].isin(priority_filter)]
    if analyst_filter:
        filtered_tasks = filtered_tasks[filtered_tasks['Assigned_To'].isin(analyst_filter)]
    
    # Display tasks
    st.subheader("Task List")
    for idx, task in filtered_tasks.iterrows():
        with st.expander(f"{task['Task_ID']} - {task['Task_Description']}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Description:** {task['Task_Description']}")
                st.write(f"**Priority:** {task['Priority']}")
                st.write(f"**Status:** {task['Status']}")
                st.write(f"**Assigned To:** {task['Assigned_To']}")
                st.write(f"**Due Date:** {task['Due_Date'].strftime('%Y-%m-%d')}")
            
            with col2:
                if task['Status'] == 'Pending':
                    if st.button("Accept", key=f"accept_{idx}"):
                        st.session_state.tasks.at[idx, 'Status'] = 'In Progress'
                        st.session_state.tasks.at[idx, 'Assigned_To'] = st.session_state.current_user
                        st.rerun()
                elif task['Status'] == 'In Progress':
                    col2a, col2b = st.columns(2)
                    with col2a:
                        if st.button("Pause", key=f"pause_{idx}"):
                            st.session_state.tasks.at[idx, 'Status'] = 'On Hold'
                            st.rerun()
                    with col2b:
                        if st.button("Complete", key=f"complete_{idx}"):
                            st.session_state.tasks.at[idx, 'Status'] = 'Completed'
                            st.session_state.tasks.at[idx, 'Completion_Date'] = datetime.now()
                            st.rerun()
            
            with col3:
                if st.button("View Details", key=f"details_{idx}"):
                    st.session_state.selected_task = task
                    st.rerun()

def render_analytics_dashboard():
    """Render the analytics dashboard with upload functionality"""
    st.header("📊 Analytics Dashboard")
    
    # Upload section for analytics data
    st.subheader("📤 Upload Analytics Data")
    uploaded_file = st.file_uploader(
        "Upload your analytics Excel file", 
        type=['xlsx', 'xls'],
        key="analytics_upload"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.session_state.analytics_data = df
            st.success(f"✅ Analytics data loaded successfully! {len(df)} rows")
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    # Use sample data if no upload
    if 'analytics_data' not in st.session_state or st.session_state.analytics_data.empty:
        st.info("📊 Using sample analytics data. Upload your own Excel file for real analytics.")
        # Create sample analytics data
        dates = pd.date_range(start='2024-01-01', end='2024-03-20', freq='D')
        sample_data = []
        for date in dates:
            for analyst in ANALYSTS[:5]:  # Use first 5 analysts for sample
                sample_data.append({
                    'Date': date,
                    'Analyst': analyst,
                    'Tasks_Completed': np.random.randint(1, 15),
                    'Quality_Score': np.random.uniform(85, 99),
                    'SLA_Compliance': np.random.uniform(90, 100),
                    'Department': np.random.choice(['Finance', 'HR', 'IT', 'Operations'])
                })
        st.session_state.analytics_data = pd.DataFrame(sample_data)
    
    df = st.session_state.analytics_data
    
    # Advanced Date Filtering
    st.subheader("📅 Advanced Date Filtering")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'Date' in df.columns:
            min_date = df['Date'].min()
            max_date = df['Date'].max()
            date_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                df = df[(df['Date'] >= pd.to_datetime(start_date)) & 
                       (df['Date'] <= pd.to_datetime(end_date))]
    
    with col2:
        if 'Department' in df.columns:
            departments = ['All'] + list(df['Department'].unique())
            selected_dept = st.selectbox("Department", departments)
            if selected_dept != 'All':
                df = df[df['Department'] == selected_dept]
    
    with col3:
        if 'Analyst' in df.columns:
            analysts_list = ['All'] + list(df['Analyst'].unique())
            selected_analyst = st.selectbox("Analyst", analysts_list)
            if selected_analyst != 'All':
                df = df[df['Analyst'] == selected_analyst]
    
    # Key Metrics
    st.subheader("📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'Tasks_Completed' in df.columns:
            total_tasks = df['Tasks_Completed'].sum()
            st.metric("Total Tasks Completed", int(total_tasks))
    
    with col2:
        if 'Quality_Score' in df.columns:
            avg_quality = df['Quality_Score'].mean()
            st.metric("Average Quality Score", f"{avg_quality:.1f}%")
    
    with col3:
        if 'SLA_Compliance' in df.columns:
            avg_sla = df['SLA_Compliance'].mean()
            st.metric("SLA Compliance", f"{avg_sla:.1f}%")
    
    with col4:
        if 'Analyst' in df.columns and 'Tasks_Completed' in df.columns:
            top_performer = df.groupby('Analyst')['Tasks_Completed'].sum().idxmax()
            st.metric("Top Performer", top_performer)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Analyst' in df.columns and 'Tasks_Completed' in df.columns:
            analyst_performance = df.groupby('Analyst')['Tasks_Completed'].sum().reset_index()
            fig = px.bar(
                analyst_performance, 
                x='Analyst', 
                y='Tasks_Completed',
                title="Tasks Completed by Analyst",
                color='Tasks_Completed'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Date' in df.columns and 'Tasks_Completed' in df.columns:
            daily_tasks = df.groupby('Date')['Tasks_Completed'].sum().reset_index()
            fig = px.line(
                daily_tasks,
                x='Date',
                y='Tasks_Completed',
                title="Daily Task Completion Trend"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Additional charts
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Department' in df.columns and 'Tasks_Completed' in df.columns:
            dept_performance = df.groupby('Department')['Tasks_Completed'].sum().reset_index()
            fig = px.pie(
                dept_performance,
                values='Tasks_Completed',
                names='Department',
                title="Tasks by Department"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Quality_Score' in df.columns and 'SLA_Compliance' in df.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['Quality_Score'],
                y=df['SLA_Compliance'],
                mode='markers',
                marker=dict(size=8, color=df['Tasks_Completed']),
                text=df['Analyst'] if 'Analyst' in df.columns else None
            ))
            fig.update_layout(
                title="Quality Score vs SLA Compliance",
                xaxis_title="Quality Score (%)",
                yaxis_title="SLA Compliance (%)"
            )
            st.plotly_chart(fig, use_container_width=True)

def render_achieved_data():
    """Render the achieved data analytics with proper error handling"""
    st.header("📈 Ultimate Achieved Data Analytics")
    
    st.subheader("📤 Upload Your Achieved Data")
    uploaded_file = st.file_uploader(
        "Upload Achieved Data Excel File",
        type=['xlsx', 'xls'],
        key="achieved_upload"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.session_state.achieved_data = df
            st.success(f"✅ Achieved data loaded successfully! Data Loaded: {len(df)} rows")
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    if st.session_state.achieved_data.empty:
        st.info("📁 Please upload an Excel file to see the analytics.")
        
        # Create sample achieved data structure
        sample_achieved = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=100, freq='D'),
            'Workflow_Type': np.random.choice(['Processing', 'Review', 'Approval', 'Validation'], 100),
            'Analyst': np.random.choice(ANALYSTS, 100),
            'Tasks_Completed': np.random.randint(1, 20, 100),
            'Avg_Completion_Time_Hours': np.random.uniform(0.5, 8.0, 100),
            'Quality_Score': np.random.uniform(85, 99, 100),
            'SLA_Compliance': np.random.uniform(90, 100, 100),
            'Department': np.random.choice(['Finance', 'HR', 'IT', 'Operations'], 100)
        })
        st.session_state.achieved_data = sample_achieved
        st.warning("⚠️ Using sample data for demonstration. Upload your Excel file for real analytics.")
    
    df = st.session_state.achieved_data
    
    # Enhanced filtering
    st.subheader("🔍 Advanced Filtering")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'Date' in df.columns:
            min_date = df['Date'].min()
            max_date = df['Date'].max()
            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="achieved_date"
            )
    
    with col2:
        if 'Workflow_Type' in df.columns:
            workflow_types = ['All'] + list(df['Workflow_Type'].unique())
            selected_workflow = st.selectbox("Workflow Type", workflow_types)
    
    with col3:
        if 'Analyst' in df.columns:
            analysts_list = ['All'] + list(df['Analyst'].unique())
            selected_analyst = st.selectbox("Analyst", analysts_list, key="achieved_analyst")
    
    with col4:
        if 'Department' in df.columns:
            departments = ['All'] + list(df['Department'].unique())
            selected_dept = st.selectbox("Department", departments, key="achieved_dept")
    
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
    
    # Enhanced metrics with error handling
    st.subheader("📊 Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        with col1:
            if 'Tasks_Completed' in df.columns:
                total_tasks = df['Tasks_Completed'].sum()
                st.metric("Total Tasks", int(total_tasks))
        
        with col2:
            if 'Quality_Score' in df.columns:
                avg_quality = df['Quality_Score'].mean()
                st.metric("Avg Quality Score", f"{avg_quality:.1f}%")
        
        with col3:
            if 'SLA_Compliance' in df.columns:
                avg_sla = df['SLA_Compliance'].mean()
                st.metric("SLA Compliance", f"{avg_sla:.1f}%")
        
        with col4:
            if 'Avg_Completion_Time_Hours' in df.columns:
                avg_time = df['Avg_Completion_Time_Hours'].mean()
                st.metric("Avg Completion Time", f"{avg_time:.1f} hrs")
    except Exception as e:
        st.error(f"Error calculating metrics: {e}")
    
    # Enhanced visualizations
    st.subheader("📈 Interactive Analytics Dashboard")
    
    col1, col2 = st.columns(2)
    
    try:
        with col1:
            if 'Workflow_Type' in df.columns and 'Tasks_Completed' in df.columns:
                workflow_data = df.groupby('Workflow_Type')['Tasks_Completed'].sum().reset_index()
                fig = px.bar(
                    workflow_data,
                    x='Workflow_Type',
                    y='Tasks_Completed',
                    title="Tasks by Workflow Type",
                    color='Tasks_Completed'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Date' in df.columns and 'Tasks_Completed' in df.columns:
                daily_trend = df.groupby('Date')['Tasks_Completed'].sum().reset_index()
                fig = px.line(
                    daily_trend,
                    x='Date',
                    y='Tasks_Completed',
                    title="Daily Completion Trend",
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Additional charts
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Analyst' in df.columns and 'Tasks_Completed' in df.columns:
                analyst_perf = df.groupby('Analyst')['Tasks_Completed'].sum().reset_index()
                fig = px.pie(
                    analyst_perf,
                    values='Tasks_Completed',
                    names='Analyst',
                    title="Task Distribution by Analyst"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Quality_Score' in df.columns and 'SLA_Compliance' in df.columns:
                fig = px.scatter(
                    df,
                    x='Quality_Score',
                    y='SLA_Compliance',
                    color='Department' if 'Department' in df.columns else None,
                    size='Tasks_Completed' if 'Tasks_Completed' in df.columns else None,
                    title="Quality vs SLA Compliance",
                    hover_data=['Analyst'] if 'Analyst' in df.columns else None
                )
                st.plotly_chart(fig, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error creating charts: {e}")
        st.info("Please check your data columns and try again.")

def main():
    """Main application function"""
    render_top_navigation()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Task Management", "Analytics Dashboard", "Achieved Data Analytics"]
    )
    
    # User selection
    st.sidebar.subheader("User Settings")
    selected_user = st.sidebar.selectbox("Select Your Profile", ANALYSTS)
    st.session_state.current_user = selected_user
    
    # Render selected page
    if page == "Task Management":
        render_task_management()
    elif page == "Analytics Dashboard":
        render_analytics_dashboard()
    elif page == "Achieved Data Analytics":
        render_achieved_data()

if __name__ == "__main__":
    main()
