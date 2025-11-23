import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime, timedelta
import time

# Configure the page
st.set_page_config(
    page_title="ARMS Workflow Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .workflow-card {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .task-active {
        border-left: 4px solid #28a745;
    }
    .task-paused {
        border-left: 4px solid #ffc107;
    }
    .task-completed {
        border-left: 4px solid #6c757d;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'active_tasks' not in st.session_state:
    st.session_state.active_tasks = {}
if 'task_history' not in st.session_state:
    st.session_state.task_history = []
if 'workflow_data' not in st.session_state:
    st.session_state.workflow_data = {}
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = pd.DataFrame()
if 'workflow_definitions' not in st.session_state:
    st.session_state.workflow_definitions = {}
if 'show_new_task' not in st.session_state:
    st.session_state.show_new_task = False

# App title and description
st.markdown('<div class="main-header">ARMS Workflow Management System</div>', unsafe_allow_html=True)

# Sidebar for navigation
with st.sidebar:
    st.header("ARMS Navigation")
    
    # File Upload Section
    st.subheader("📁 Data Import")
    uploaded_files = st.file_uploader(
        "Upload Excel/CSV Files:",
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        help="Upload historical data, current workflows, or performance metrics"
    )
    
    # Process uploaded files
    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Store historical data
                if st.session_state.historical_data.empty:
                    st.session_state.historical_data = df
                else:
                    st.session_state.historical_data = pd.concat([st.session_state.historical_data, df], ignore_index=True)
                
                st.sidebar.success(f"✅ {uploaded_file.name} loaded successfully!")
            except Exception as e:
                st.sidebar.error(f"Error processing {uploaded_file.name}: {str(e)}")
    
    # Workflow Selection
    st.markdown("---")
    st.subheader("Workflow Management")
    selected_workflow = st.selectbox(
        "Select Workflow:",
        [
            "Pending Trade Workflow",
            "Placements Processing", 
            "UCC Filings",
            "Judgments Processing",
            "Chapter 11 Bankruptcy",
            "Chapter 7 Bankruptcy",
            "Credit Files Analysis",
            "Data Import Monitoring",
            "Subscriber Management",
            "Quality Assurance"
        ]
    )
    
    # Task Management
    st.markdown("---")
    st.subheader("Task Controls")
    
    if st.button("🎯 Start New Task", use_container_width=True):
        st.session_state.show_new_task = True
        st.rerun()

# Main content area
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard", 
    "📋 Pending Workflow", 
    "📧 Email Import", 
    "⏱️ Task Management", 
    "📈 Analytics",
    "⚙️ Workflow Setup"
])

with tab1:
    st.markdown('<div class="section-header">ARMS Workflow Dashboard</div>', unsafe_allow_html=True)
    
    # Update dashboard based on selected workflow
    workflow_metrics = {
        "Pending Trade Workflow": {"pending": 71368, "analysts": 24, "time": "2.3 days", "sla": "92%"},
        "Placements Processing": {"pending": 2345, "analysts": 8, "time": "1.2 days", "sla": "95%"},
        "UCC Filings": {"pending": 1567, "analysts": 6, "time": "0.8 days", "sla": "98%"},
        "Judgments Processing": {"pending": 2890, "analysts": 7, "time": "1.5 days", "sla": "94%"},
        "Chapter 11 Bankruptcy": {"pending": 456, "analysts": 3, "time": "3.2 days", "sla": "89%"},
        "Chapter 7 Bankruptcy": {"pending": 321, "analysts": 2, "time": "2.8 days", "sla": "91%"},
        "Credit Files Analysis": {"pending": 1789, "analysts": 5, "time": "1.1 days", "sla": "96%"},
        "Data Import Monitoring": {"pending": 567, "analysts": 4, "time": "0.5 days", "sla": "99%"},
        "Subscriber Management": {"pending": 234, "analysts": 3, "time": "0.3 days", "sla": "97%"},
        "Quality Assurance": {"pending": 123, "analysts": 2, "time": "1.0 days", "sla": "93%"}
    }
    
    current_metrics = workflow_metrics.get(selected_workflow, workflow_metrics["Pending Trade Workflow"])
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pending Items", f"{current_metrics['pending']:,}")
    
    with col2:
        st.metric("Active Analysts", current_metrics['analysts'])
    
    with col3:
        st.metric("Avg Processing Time", current_metrics['time'])
    
    with col4:
        st.metric("SLA Compliance", current_metrics['sla'])
    
    # Workflow Overview
    st.subheader(f"{selected_workflow} - Distribution")
    
    # Dynamic data based on selected workflow
    workflow_data = {
        'Workflow': [
            'Pending Trades', 'Placements', 'UCC Filings', 'Judgments', 
            'Chapter 11', 'Chapter 7', 'Credit Files', 'Data Import',
            'Subscriber Mgmt', 'Quality Assurance'
        ],
        'Pending_Items': [71368, 2345, 1567, 2890, 456, 321, 1789, 567, 234, 123],
        'Active_Tasks': [45, 12, 8, 15, 6, 4, 10, 7, 5, 3]
    }
    
    workflow_df = pd.DataFrame(workflow_data)
    
    # Highlight selected workflow
    if selected_workflow in workflow_df['Workflow'].values:
        highlight_idx = workflow_df[workflow_df['Workflow'] == selected_workflow.replace(" Workflow", "").replace(" Processing", "").replace(" Analysis", "").replace(" Monitoring", "").replace(" Management", "")].index
        if not highlight_idx.empty:
            # Use Streamlit's native bar chart
            chart_data = workflow_df.set_index('Workflow')['Pending_Items']
            st.bar_chart(chart_data)

with tab2:
    st.markdown(f'<div class="section-header">📋 {selected_workflow} Analysis</div>', unsafe_allow_html=True)
    
    # Database Table Integration
    st.subheader("Database Table Integration")
    
    # Show available tables
    tables_info = {
        'Table 1': 'Trades Tape Import - File Dates',
        'Table 2': 'Trades Tape Import - Analyst & Performance',
        'Table 3': 'Pending Data - Import Timeline', 
        'Table 4': 'Pending Data - Analyst Assignment',
        'Table 5': 'Placements - Basic Metrics',
        'Table 6': 'Placements - Credit Files Analysis',
        'Table 7': 'UCC Filings - Basic Metrics',
        'Table 8': 'UCC Filings - Credit Files Analysis',
        'Table 9': 'Judgments - Basic Metrics',
        'Table 10': 'Judgments - Credit Files Analysis',
        'Table 11': 'Chapter 11 - Import Timeline',
        'Table 12': 'Chapter 11 - Analyst Assignment',
        'Table 13': 'Chapter 7 - Import Timeline',
        'Table 14': 'Chapter 7 - Analyst Assignment'
    }
    
    # Table selection for analysis
    selected_tables = st.multiselect(
        "Select tables to analyze:",
        list(tables_info.keys()),
        default=['Table 1', 'Table 2', 'Table 3', 'Table 4'],
        format_func=lambda x: f"{x}: {tables_info[x]}"
    )
    
    # Display historical data if available
    if not st.session_state.historical_data.empty:
        st.subheader("Historical Data Overview")
        st.dataframe(st.session_state.historical_data, use_container_width=True)
        
        # Basic statistics
        st.subheader("Data Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(st.session_state.historical_data))
        
        with col2:
            st.metric("Columns", len(st.session_state.historical_data.columns))
        
        with col3:
            st.metric("Data Period", f"{st.session_state.historical_data.select_dtypes(include=['datetime64']).min().iloc[0] if not st.session_state.historical_data.select_dtypes(include=['datetime64']).empty else 'N/A'}")

with tab3:
    st.markdown('<div class="section-header">📧 Email Work Import & Management</div>', unsafe_allow_html=True)
    
    # Email file upload
    st.subheader("Upload Email Work Files")
    
    email_files = st.file_uploader(
        "Upload email files or work request spreadsheets:",
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        help="Upload multiple email files or Excel sheets containing work requests",
        key="email_uploader"
    )
    
    if email_files:
        st.success(f"✅ {len(email_files)} email file(s) uploaded successfully!")
        
        # Process email files
        email_data = []
        for email_file in email_files:
            try:
                if email_file.name.endswith('.csv'):
                    df = pd.read_csv(email_file)
                else:
                    df = pd.read_excel(email_file)
                
                # Extract work items from email data
                for _, row in df.iterrows():
                    email_data.append({
                        'email_file': email_file.name,
                        'work_item_id': f"EMAIL_{len(email_data)+1:04d}",
                        'subject': row.get('subject', 'N/A'),
                        'requestor': row.get('from', 'Unknown'),
                        'received_date': row.get('date', datetime.now().strftime('%Y-%m-%d')),
                        'priority': row.get('priority', 'Medium'),
                        'estimated_effort_minutes': row.get('estimated_effort', 30),
                        'assigned_to': 'Unassigned',
                        'status': 'New'
                    })
            except Exception as e:
                st.error(f"Error processing {email_file.name}: {str(e)}")
        
        if email_data:
            email_df = pd.DataFrame(email_data)
            st.subheader("Extracted Work Items from Emails")
            st.dataframe(email_df, use_container_width=True)
            
            # Assignment interface
            st.subheader("Assign Work Items & Create Tasks")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_items = st.multiselect(
                    "Select work items to assign:",
                    options=email_df['work_item_id'].tolist()
                )
            
            with col2:
                assigned_analyst = st.selectbox(
                    "Assign to Analyst:",
                    options=['Analyst A', 'Analyst B', 'Analyst C', 'Analyst D', 'Analyst E', 'Analyst F']
                )
                
                workflow_type = st.selectbox(
                    "Workflow Type:",
                    [
                        "Pending Trade Workflow", "Placements Processing", "UCC Filings",
                        "Judgments Processing", "Chapter 11 Bankruptcy", "Chapter 7 Bankruptcy",
                        "Credit Files Analysis", "Data Import Monitoring", "Subscriber Management", 
                        "Quality Assurance"
                    ]
                )
                
                if st.button("Create Tasks from Selected Items", type="primary"):
                    for item_id in selected_items:
                        # Update assignment in the dataframe
                        email_df.loc[email_df['work_item_id'] == item_id, 'assigned_to'] = assigned_analyst
                        email_df.loc[email_df['work_item_id'] == item_id, 'status'] = 'Assigned'
                        
                        # Create a task in the task management system
                        task_id = f"TASK_{len(st.session_state.active_tasks) + 1:04d}"
                        item_data = email_df[email_df['work_item_id'] == item_id].iloc[0]
                        
                        st.session_state.active_tasks[task_id] = {
                            'task_name': f"Email: {item_data['subject']}",
                            'workflow': workflow_type,
                            'assigned_analyst': assigned_analyst,
                            'description': f"From: {item_data['requestor']} - {item_data['subject']}",
                            'estimated_duration': item_data['estimated_effort_minutes'],
                            'priority': item_data['priority'],
                            'start_time': datetime.now(),
                            'status': 'Active',
                            'paused_time': None,
                            'total_paused_duration': 0,
                            'source': 'Email Import'
                        }
                    
                    st.success(f"✅ {len(selected_items)} tasks created and assigned to {assigned_analyst}")
                    st.rerun()

with tab4:
    st.markdown('<div class="section-header">⏱️ Task Time Tracking & Management</div>', unsafe_allow_html=True)
    
    # Current Active Tasks
    st.subheader("Active Task Management")
    
    # Task creation interface
    if st.session_state.show_new_task:
        with st.form("new_task_form"):
            st.subheader("Create New Task")
            
            col1, col2 = st.columns(2)
            
            with col1:
                task_name = st.text_input("Task Name:", placeholder="Enter task name")
                task_workflow = st.selectbox(
                    "Workflow Type:",
                    [
                        "Pending Trade Workflow", "Placements Processing", "UCC Filings",
                        "Judgments Processing", "Chapter 11 Bankruptcy", "Chapter 7 Bankruptcy",
                        "Credit Files Analysis", "Data Import Monitoring", "Subscriber Management", 
                        "Quality Assurance"
                    ]
                )
                assigned_analyst = st.selectbox(
                    "Assign to Analyst:",
                    ['Analyst A', 'Analyst B', 'Analyst C', 'Analyst D', 'Analyst E', 'Analyst F']
                )
            
            with col2:
                task_description = st.text_area("Task Description:", placeholder="Describe the task...")
                estimated_duration = st.number_input("Estimated Duration (minutes):", min_value=5, value=30)
                priority = st.selectbox("Priority:", ["Low", "Medium", "High", "Critical"])
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("🎯 Start Task")
            with col2:
                cancel = st.form_submit_button("❌ Cancel")
            
            if submitted and task_name:
                task_id = f"TASK_{len(st.session_state.active_tasks) + 1:04d}"
                st.session_state.active_tasks[task_id] = {
                    'task_name': task_name,
                    'workflow': task_workflow,
                    'assigned_analyst': assigned_analyst,
                    'description': task_description,
                    'estimated_duration': estimated_duration,
                    'priority': priority,
                    'start_time': datetime.now(),
                    'status': 'Active',
                    'paused_time': None,
                    'total_paused_duration': 0,
                    'source': 'Manual Creation'
                }
                st.session_state.show_new_task = False
                st.success(f"✅ Task '{task_name}' started successfully!")
                st.rerun()
            elif cancel:
                st.session_state.show_new_task = False
                st.rerun()
    
    # Display active tasks
    if st.session_state.active_tasks:
        st.subheader("Currently Active Tasks")
        
        for task_id, task in st.session_state.active_tasks.items():
            task_class = "task-active" if task['status'] == 'Active' else "task-paused"
            with st.container():
                st.markdown(f'<div class="workflow-card {task_class}">', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{task['task_name']}**")
                    st.write(f"Workflow: {task['workflow']} | Analyst: {task['assigned_analyst']}")
                    st.write(f"Priority: {task['priority']} | Started: {task['start_time'].strftime('%Y-%m-%d %H:%M')}")
                    if task.get('source'):
                        st.write(f"Source: {task['source']}")
                
                with col2:
                    current_duration = (datetime.now() - task['start_time']).total_seconds() / 60
                    st.write(f"Duration: {current_duration:.1f} min")
                    st.write(f"Status: {task['status']}")
                
                with col3:
                    if task['status'] == 'Active':
                        if st.button("⏸️ Pause", key=f"pause_{task_id}"):
                            st.session_state.active_tasks[task_id]['status'] = 'Paused'
                            st.session_state.active_tasks[task_id]['paused_time'] = datetime.now()
                            st.rerun()
                        
                        if st.button("✅ Complete", key=f"complete_{task_id}"):
                            # Move to history
                            task_data = st.session_state.active_tasks[task_id].copy()
                            task_data['end_time'] = datetime.now()
                            task_data['total_duration'] = (task_data['end_time'] - task_data['start_time']).total_seconds() / 60
                            st.session_state.task_history.append(task_data)
                            del st.session_state.active_tasks[task_id]
                            st.rerun()
                    
                    elif task['status'] == 'Paused':
                        if st.button("▶️ Resume", key=f"resume_{task_id}"):
                            paused_duration = (datetime.now() - st.session_state.active_tasks[task_id]['paused_time']).total_seconds() / 60
                            st.session_state.active_tasks[task_id]['total_paused_duration'] += paused_duration
                            st.session_state.active_tasks[task_id]['status'] = 'Active'
                            st.session_state.active_tasks[task_id]['paused_time'] = None
                            st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No active tasks. Click 'Start New Task' in the sidebar to begin tracking work.")
    
    # Task History
    if st.session_state.task_history:
        st.subheader("Task History")
        history_df = pd.DataFrame(st.session_state.task_history)
        st.dataframe(history_df, use_container_width=True)

with tab5:
    st.markdown('<div class="section-header">📈 Comprehensive Analytics</div>', unsafe_allow_html=True)
    
    # Combine historical data with current task history
    all_data = st.session_state.historical_data.copy()
    if st.session_state.task_history:
        task_history_df = pd.DataFrame(st.session_state.task_history)
        if not all_data.empty:
            all_data = pd.concat([all_data, task_history_df], ignore_index=True)
        else:
            all_data = task_history_df
    
    if not all_data.empty:
        st.subheader("Combined Historical & Current Data")
        st.dataframe(all_data, use_container_width=True)
        
        # Performance metrics
        st.subheader("Performance Analytics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'total_duration' in all_data.columns:
                avg_duration = all_data['total_duration'].mean()
                st.metric("Average Task Duration", f"{avg_duration:.1f} min")
        
        with col2:
            if 'priority' in all_data.columns:
                high_priority = len(all_data[all_data['priority'] == 'High'])
                st.metric("High Priority Tasks", high_priority)
        
        with col3:
            if 'workflow' in all_data.columns:
                unique_workflows = all_data['workflow'].nunique()
                st.metric("Active Workflows", unique_workflows)
    
    # Department Metrics
    st.subheader("Department Performance Metrics")
    
    dept_metrics_data = {
        'Metric': [
            'Total Items Processed', 'Average Processing Time', 'SLA Compliance Rate',
            'Quality Score', 'Cost per Item', 'Analyst Utilization', 'Backlog Size',
            'Customer Satisfaction'
        ],
        'Current': [15432, '2.3 days', '92%', '94.5%', '$4.67', '78%', 71368, '4.2/5.0'],
        'Target': [16000, '2.0 days', '95%', '96%', '$4.50', '85%', 50000, '4.5/5.0'],
        'Variance': ['-3.5%', '+15%', '-3%', '-1.5%', '+3.8%', '-7%', '+42.7%', '-0.3']
    }
    
    dept_metrics_df = pd.DataFrame(dept_metrics_data)
    st.dataframe(dept_metrics_df, use_container_width=True)

with tab6:
    st.markdown('<div class="section-header">⚙️ Workflow Setup & Configuration</div>', unsafe_allow_html=True)
    
    # Workflow Definition
    st.subheader("Define New Workflow")
    
    with st.form("workflow_definition"):
        col1, col2 = st.columns(2)
        
        with col1:
            workflow_name = st.text_input("Workflow Name:")
            sla_target = st.number_input("SLA Target (%):", min_value=0, max_value=100, value=95)
            max_processing_time = st.number_input("Max Processing Time (hours):", min_value=1, value=24)
        
        with col2:
            assigned_team = st.text_input("Assigned Team:")
            required_approvals = st.number_input("Required Approvals:", min_value=0, value=1)
            priority_level = st.selectbox("Default Priority:", ["Low", "Medium", "High", "Critical"])
        
        data_points = st.text_area("Required Data Points (comma-separated):", 
                                 placeholder="subscriber_id, trade_date, amount, status...")
        
        submitted = st.form_submit_button("Create Workflow Definition")
        
        if submitted and workflow_name:
            workflow_id = f"WF_{len(st.session_state.workflow_definitions) + 1:03d}"
            st.session_state.workflow_definitions[workflow_id] = {
                'workflow_name': workflow_name,
                'sla_target': sla_target,
                'max_processing_time': max_processing_time,
                'assigned_team': assigned_team,
                'required_approvals': required_approvals,
                'priority_level': priority_level,
                'data_points': [dp.strip() for dp in data_points.split(',')] if data_points else [],
                'created_date': datetime.now().strftime('%Y-%m-%d')
            }
            st.success(f"✅ Workflow '{workflow_name}' defined successfully!")
    
    # Display defined workflows
    if st.session_state.workflow_definitions:
        st.subheader("Defined Workflows")
        workflows_df = pd.DataFrame.from_dict(st.session_state.workflow_definitions, orient='index')
        st.dataframe(workflows_df, use_container_width=True)

# Export functionality
st.markdown("---")
st.subheader("📤 Export Data & Reports")

col1, col2, col3 = st.columns(3)

with col1:
    export_format = st.radio("Export Format:", ["Excel", "CSV"])

with col2:
    include_sections = st.multiselect(
        "Include Sections:",
        ["Task History", "Active Tasks", "Workflow Definitions", "Historical Data", "Performance Metrics"],
        default=["Task History", "Active Tasks"]
    )

with col3:
    st.write("")  # Spacer
    if st.button("Generate Comprehensive Report", type="primary"):
        with st.spinner("Generating export file..."):
            time.sleep(2)
            
            # Create export data
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                if "Task History" in include_sections and st.session_state.task_history:
                    pd.DataFrame(st.session_state.task_history).to_excel(writer, sheet_name='Task_History', index=False)
                
                if "Active Tasks" in include_sections and st.session_state.active_tasks:
                    pd.DataFrame.from_dict(st.session_state.active_tasks, orient='index').to_excel(writer, sheet_name='Active_Tasks', index=False)
                
                if "Workflow Definitions" in include_sections and st.session_state.workflow_definitions:
                    pd.DataFrame.from_dict(st.session_state.workflow_definitions, orient='index').to_excel(writer, sheet_name='Workflow_Definitions', index=False)
                
                if "Historical Data" in include_sections and not st.session_state.historical_data.empty:
                    st.session_state.historical_data.to_excel(writer, sheet_name='Historical_Data', index=False)
            
            st.success("Export generated successfully!")
            
            st.download_button(
                label="Download Export File",
                data=output.getvalue(),
                file_name=f"ARMS_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.ms-excel"
            )

# Footer
st.markdown("---")
st.markdown("ARMS Workflow Management System v4.1 | Ready for GitHub Deployment | For internal use only")

# GitHub deployment instructions
with st.expander("🚀 GitHub Deployment Instructions"):
    st.markdown("""
    ### How to Deploy to GitHub:
    
    1. **Create a new GitHub repository**
       - Go to GitHub.com → New Repository
       - Name: `arms-workflow-manager`
       - Add README.md
    
    2. **Prepare your files:**
       ```bash
       # Required files for GitHub:
       arms_workflow.py          # This main application
       requirements.txt          # Python dependencies
       README.md                 # Documentation
       ```
    
    3. **Create requirements.txt:**
       ```txt
       streamlit==1.28.0
       pandas==2.0.3
       numpy==1.24.3
       openpyxl==3.1.2
       ```
    
    4. **Deploy to Streamlit Cloud:**
       - Go to share.streamlit.io
       - Connect your GitHub repository
       - Deploy automatically!
    
    5. **Share the URL with your team**
    """)
