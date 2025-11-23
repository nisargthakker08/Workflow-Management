# app_enhanced.py
import streamlit as st
import pandas as pd
import numpy as np
import io
import time
from datetime import datetime, date
import hashlib
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =========================
# AUTHENTICATION SYSTEM
# =========================

USER_CREDENTIALS = {
    "nisarg": {
        "password": "admin123",
        "name": "Nisarg Thakker",
        "role": "admin"
    },
    "jen": {
        "password": "admin123", 
        "name": "Jen Shears",
        "role": "admin"
    },
    "komal": {
        "password": "admin123",
        "name": "Komal Khamar", 
        "role": "admin"
    },
    "janet": {
        "password": "user123",
        "name": "Janet Yanatos",
        "role": "user"
    },
    "rondrea": {
        "password": "user123",
        "name": "Rondrea Carroll",
        "role": "user"
    },
    "devanshi": {
        "password": "user123", 
        "name": "Devanshi Joshi",
        "role": "user"
    }
}

WORKFLOWS_CONFIG = {
    "Trades Tape Imports": {
        "type": "Volume Completion %",
        "target_metric": "Batches",
        "monthly_target": "100%",
        "priority": "High",
        "sla_hours": 24,
        "quality_required": "Yes"
    },
    "Pending": {
        "type": "Volume Completion %", 
        "target_metric": "Items",
        "monthly_target": "100%",
        "priority": "High", 
        "sla_hours": 72,
        "quality_required": "Yes"
    },
    "Placements": {
        "type": "Target Placements",
        "target_metric": "Cases", 
        "monthly_target": "50",
        "priority": "Medium",
        "sla_hours": 72,
        "quality_required": "Yes"
    },
    "Judgments": {
        "type": "Target Accuracy %",
        "target_metric": "Judgments",
        "monthly_target": "98%",
        "priority": "Medium",
        "sla_hours": 72,
        "quality_required": "Yes"
    },
    "UCC": {
        "type": "Target UCC Filings", 
        "target_metric": "Filings",
        "monthly_target": "30",
        "priority": "Medium",
        "sla_hours": 72,
        "quality_required": "Yes"
    },
    "Credit Files": {
        "type": "Target Files",
        "target_metric": "Files",
        "monthly_target": "150", 
        "priority": "Low",
        "sla_hours": 72,
        "quality_required": "Yes"
    },
    "Chapter 11": {
        "type": "Quality Timeliness %",
        "target_metric": "Cases", 
        "monthly_target": "95%",
        "priority": "Critical",
        "sla_hours": 24,
        "quality_required": "Yes"
    },
    "Chapter 7": {
        "type": "Quality Timeliness %",
        "target_metric": "Cases",
        "monthly_target": "95%", 
        "priority": "Critical",
        "sla_hours": 24,
        "quality_required": "Yes"
    },
    "Trade References": {
        "type": "Volume Processing %",
        "target_metric": "References",
        "monthly_target": "100%",
        "priority": "High", 
        "sla_hours": 48,
        "quality_required": "Yes"
    },
    "Credit File Audits": {
        "type": "Quality Compliance %",
        "target_metric": "Audits", 
        "monthly_target": "100%",
        "priority": "Medium",
        "sla_hours": 72,
        "quality_required": "Yes"
    }
}

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
# CUSTOM CSS
# =========================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3498db;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .workflow-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2ecc71;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0.75rem;
        font-weight: 600;
    }
    .tab-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE INIT
# =========================

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = {}
if 'selected_sheets' not in st.session_state:
    st.session_state.selected_sheets = []
if 'custom_measures' not in st.session_state:
    st.session_state.custom_measures = []
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# =========================
# AUTHENTICATION FUNCTIONS
# =========================

def login():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #2c3e50;">🔐 ARMS Login</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7f8c8d;">Enter your credentials to access the workflow system</p>', unsafe_allow_html=True)
    
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🚀 Login", use_container_width=True):
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.current_user = USER_CREDENTIALS[username]["name"]
                st.session_state.user_role = USER_CREDENTIALS[username]["role"]
                st.success(f"Welcome {st.session_state.current_user}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# DATA PROCESSING FUNCTIONS
# =========================

def process_excel_upload(file):
    """Process uploaded Excel file and extract sheet information"""
    try:
        xls = pd.ExcelFile(file)
        sheets_info = {}
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            sheets_info[sheet_name] = {
                'dataframe': df,
                'columns': df.columns.tolist(),
                'row_count': len(df),
                'preview': df.head(10)
            }
        
        st.session_state.uploaded_data = sheets_info
        st.session_state.selected_sheets = list(sheets_info.keys())
        return True
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return False

def create_custom_measure(measure_name, sheet_name, column_name, operation):
    """Create custom measures like Power BI"""
    if sheet_name not in st.session_state.uploaded_data:
        return None
    
    df = st.session_state.uploaded_data[sheet_name]['dataframe']
    
    if column_name not in df.columns:
        return None
    
    try:
        if operation == "Sum":
            result = df[column_name].sum()
        elif operation == "Average":
            result = df[column_name].mean()
        elif operation == "Count":
            result = df[column_name].count()
        elif operation == "Distinct Count":
            result = df[column_name].nunique()
        elif operation == "Min":
            result = df[column_name].min()
        elif operation == "Max":
            result = df[column_name].max()
        else:
            return None
        
        measure = {
            'name': measure_name,
            'sheet': sheet_name,
            'column': column_name,
            'operation': operation,
            'value': result,
            'timestamp': datetime.now()
        }
        
        st.session_state.custom_measures.append(measure)
        return measure
    except Exception as e:
        st.error(f"Error creating measure: {str(e)}")
        return None

# =========================
# DASHBOARD COMPONENTS
# =========================

def render_dashboard():
    st.markdown('<div class="main-header">📊 ARMS Workflow Dashboard</div>', unsafe_allow_html=True)
    
    # Quick Stats Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_pending = sum([len(data['dataframe']) for data in st.session_state.uploaded_data.values()])
        st.metric("Total Pending Items", f"{total_pending:,}")
    
    with col2:
        active_workflows = len(st.session_state.uploaded_data)
        st.metric("Active Workflows", active_workflows)
    
    with col3:
        st.metric("SLA Compliance", "92%")
    
    with col4:
        st.metric("Avg Processing Time", "2.3 days")
    
    # Workflow Distribution Chart
    st.subheader("Workflow Distribution")
    
    if st.session_state.uploaded_data:
        workflow_data = []
        for sheet_name, data in st.session_state.uploaded_data.items():
            workflow_data.append({
                'Workflow': sheet_name,
                'Pending Items': len(data['dataframe'])
            })
        
        df = pd.DataFrame(workflow_data)
        fig = px.bar(df, x='Workflow', y='Pending Items', 
                    color='Pending Items',
                    color_continuous_scale='viridis')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Upload data to see workflow distribution")

def render_data_import():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("📁 Data Import & Sheet Selection")
    
    uploaded_file = st.file_uploader("Upload Excel Workbook", type=['xlsx', 'xls'])
    
    if uploaded_file:
        if st.button("Process Workbook"):
            with st.spinner("Processing workbook..."):
                if process_excel_upload(uploaded_file):
                    st.success("Workbook processed successfully!")
    
    if st.session_state.uploaded_data:
        st.subheader("Select Sheets to Analyze")
        
        all_sheets = list(st.session_state.uploaded_data.keys())
        selected = st.multiselect("Choose sheets for analysis", all_sheets, default=all_sheets)
        st.session_state.selected_sheets = selected
        
        # Show sheet previews
        for sheet_name in selected:
            with st.expander(f"📋 {sheet_name} - Preview"):
                data = st.session_state.uploaded_data[sheet_name]
                st.write(f"**Columns:** {', '.join(data['columns'])}")
                st.write(f"**Total Rows:** {data['row_count']:,}")
                st.dataframe(data['preview'], use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_custom_measures():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("🧮 Custom Measures (Power BI Style)")
    
    if not st.session_state.uploaded_data:
        st.info("Please upload data first to create custom measures")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Create new measure
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        measure_name = st.text_input("Measure Name", placeholder="Total Sales")
    
    with col2:
        available_sheets = list(st.session_state.uploaded_data.keys())
        selected_sheet = st.selectbox("Sheet", available_sheets)
    
    with col3:
        if selected_sheet:
            columns = st.session_state.uploaded_data[selected_sheet]['columns']
            selected_column = st.selectbox("Column", columns)
    
    with col4:
        operations = ["Sum", "Average", "Count", "Distinct Count", "Min", "Max"]
        selected_operation = st.selectbox("Operation", operations)
    
    if st.button("Create Measure") and measure_name and selected_sheet and selected_column:
        measure = create_custom_measure(measure_name, selected_sheet, selected_column, selected_operation)
        if measure:
            st.success(f"Measure '{measure_name}' created successfully!")
    
    # Display existing measures
    if st.session_state.custom_measures:
        st.subheader("Your Custom Measures")
        
        cols = st.columns(3)
        for idx, measure in enumerate(st.session_state.custom_measures):
            with cols[idx % 3]:
                st.metric(
                    label=measure['name'],
                    value=f"{measure['value']:,.2f}",
                    help=f"{measure['operation']} of {measure['column']} from {measure['sheet']}"
                )

def render_workflow_management():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("🔄 Workflow Configuration")
    
    # Workflows table
    workflows_df = pd.DataFrame([
        {
            'Workflow Name': name,
            'Workflow Type': config['type'],
            'Target Metric': config['target_metric'],
            'Monthly Target': config['monthly_target'],
            'Priority': config['priority'],
            'SLA Hours': config['sla_hours'],
            'Quality Required': config['quality_required']
        }
        for name, config in WORKFLOWS_CONFIG.items()
    ])
    
    st.dataframe(workflows_df, use_container_width=True)
    
    # Workflow progress
    st.subheader("Workflow Progress")
    
    progress_data = []
    for workflow in WORKFLOWS_CONFIG.keys():
        progress_data.append({
            'Workflow': workflow,
            'Completion %': np.random.randint(60, 95),
            'SLA Compliance': np.random.randint(85, 98)
        })
    
    progress_df = pd.DataFrame(progress_data)
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Completion %', 'SLA Compliance %'))
    
    fig.add_trace(
        go.Bar(x=progress_df['Workflow'], y=progress_df['Completion %'], name='Completion'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=progress_df['Workflow'], y=progress_df['SLA Compliance'], name='SLA Compliance'),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_task_management():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("✅ Task Management")
    
    # Manual task creation
    with st.form("create_task_form"):
        st.subheader("Create New Task")
        
        col1, col2 = st.columns(2)
        
        with col1:
            task_name = st.text_input("Task Name")
            assigned_to = st.selectbox("Assign To", list(USER_CREDENTIALS.values()), format_func=lambda x: x['name'])
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        
        with col2:
            workflow = st.selectbox("Workflow", list(WORKFLOWS_CONFIG.keys()))
            due_date = st.date_input("Due Date")
            description = st.text_area("Description")
        
        if st.form_submit_button("Create Task"):
            new_task = {
                'id': len(st.session_state.tasks) + 1,
                'name': task_name,
                'workflow': workflow,
                'assigned_to': assigned_to['name'],
                'priority': priority,
                'due_date': due_date,
                'description': description,
                'status': 'Pending',
                'created_by': st.session_state.current_user,
                'created_at': datetime.now()
            }
            st.session_state.tasks.append(new_task)
            st.success("Task created successfully!")
    
    # Display tasks
    if st.session_state.tasks:
        st.subheader("Active Tasks")
        
        for task in st.session_state.tasks:
            with st.container():
                st.markdown(f"""
                <div class="workflow-card">
                    <div style="display: flex; justify-content: between; align-items: center;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0;">{task['name']}</h4>
                            <p style="margin: 0; color: #666;">{task['description']}</p>
                            <small>Assigned to: {task['assigned_to']} | Due: {task['due_date']}</small>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: {'#e74c3c' if task['priority'] == 'Critical' else '#f39c12' if task['priority'] == 'High' else '#3498db' if task['priority'] == 'Medium' else '#27ae60'}; 
                                      color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">
                                {task['priority']}
                            </span>
                            <br>
                            <span style="color: #7f8c8d; font-size: 0.8rem;">{task['status']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No tasks created yet. Use the form above to create new tasks.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_analytics():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("📈 Advanced Analytics")
    
    if not st.session_state.uploaded_data:
        st.info("Upload data to see analytics")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Performance metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.plotly_chart(px.pie(
            values=[75, 15, 10],
            names=['Completed', 'In Progress', 'Pending'],
            title='Work Status Distribution'
        ), use_container_width=True)
    
    with col2:
        st.plotly_chart(px.bar(
            x=list(WORKFLOWS_CONFIG.keys())[:5],
            y=np.random.randint(50, 100, 5),
            title='Top 5 Workflows by Volume'
        ), use_container_width=True)
    
    with col3:
        timeline_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=30, freq='D'),
            'Completed': np.random.randint(50, 200, 30)
        })
        st.plotly_chart(px.line(
            timeline_data, x='Date', y='Completed',
            title='Daily Completion Trend'
        ), use_container_width=True)
    
    # Data correlations
    st.subheader("Data Correlations")
    
    if st.session_state.selected_sheets:
        # Show correlation matrix for first selected sheet
        first_sheet = st.session_state.selected_sheets[0]
        df = st.session_state.uploaded_data[first_sheet]['dataframe']
        
        numeric_df = df.select_dtypes(include=[np.number])
        if not numeric_df.empty:
            corr_matrix = numeric_df.corr()
            fig = px.imshow(corr_matrix, title=f'Correlation Matrix - {first_sheet}')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# MAIN APPLICATION
# =========================

def main():
    if not st.session_state.authenticated:
        login()
        return
    
    # Sidebar with user info and navigation
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; border-radius: 10px; margin-bottom: 2rem;">
            <h3>👤 {st.session_state.current_user}</h3>
            <p style="margin: 0; opacity: 0.8;">{st.session_state.user_role.upper()} ACCESS</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.subheader("📊 ARMS Navigation")
        
        menu_options = [
            "Dashboard Overview",
            "Data Import & Sheets", 
            "Custom Measures",
            "Workflow Management",
            "Task Management",
            "Advanced Analytics"
        ]
        
        selected_menu = st.radio("Go to", menu_options)
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.user_role = None
            st.rerun()
    
    # Main content area based on selection
    if selected_menu == "Dashboard Overview":
        render_dashboard()
    elif selected_menu == "Data Import & Sheets":
        render_data_import()
    elif selected_menu == "Custom Measures":
        render_custom_measures()
    elif selected_menu == "Workflow Management":
        render_workflow_management()
    elif selected_menu == "Task Management":
        render_task_management()
    elif selected_menu == "Advanced Analytics":
        render_analytics()

if __name__ == "__main__":
    main()
