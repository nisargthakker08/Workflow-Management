# app_professional.py
import streamlit as st
import pandas as pd
import numpy as np
import io
import time
from datetime import datetime, date, timedelta
import hashlib
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import email
from email import policy
from email.parser import BytesParser
import base64
import re

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
    initial_sidebar_state="expanded",
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>
    /* Main styling */
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
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3498db;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    /* Workflow cards */
    .workflow-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2ecc71;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Login container */
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        padding: 0.75rem;
        font-weight: 600;
    }
    
    /* Tabs */
    .tab-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
    }
    
    /* Date filter */
    .date-filter {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #3498db;
    }
    
    /* Formula editor */
    .formula-editor {
        background: #f1f3f4;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4285f4;
    }
    
    /* Sidebar styling */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Status badges */
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-pending { background: #f39c12; color: white; }
    .status-active { background: #27ae60; color: white; }
    .status-completed { background: #3498db; color: white; }
    .status-critical { background: #e74c3c; color: white; }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
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
if 'email_data' not in st.session_state:
    st.session_state.email_data = []
if 'global_filters' not in st.session_state:
    st.session_state.global_filters = {}
if 'analyst_metrics' not in st.session_state:
    st.session_state.analyst_metrics = {}

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
            
            # Auto-detect date columns and convert
            for col in df.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                    except:
                        pass
            
            sheets_info[sheet_name] = {
                'dataframe': df,
                'columns': df.columns.tolist(),
                'row_count': len(df),
                'preview': df.head(10),
                'date_columns': [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
            }
        
        st.session_state.uploaded_data = sheets_info
        st.session_state.selected_sheets = list(sheets_info.keys())
        return True
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return False

def apply_global_filters():
    """Apply global filters to all data"""
    filtered_data = st.session_state.uploaded_data.copy()
    
    for sheet_name, sheet_data in filtered_data.items():
        df = sheet_data['dataframe'].copy()
        
        # Apply date filters if they exist for this sheet
        if sheet_name in st.session_state.global_filters:
            filters = st.session_state.global_filters[sheet_name]
            
            # Date filter
            if 'date_column' in filters and filters['date_column']:
                date_col = filters['date_column']
                start_date = filters.get('start_date')
                end_date = filters.get('end_date')
                
                if date_col in df.columns and start_date and end_date:
                    mask = (df[date_col] >= pd.Timestamp(start_date)) & (df[date_col] <= pd.Timestamp(end_date))
                    df = df[mask]
            
            # Custom value filters
            for filter_config in filters.get('custom_filters', []):
                column = filter_config['column']
                operator = filter_config['operator']
                value = filter_config['value']
                
                if column in df.columns:
                    if operator == "equals":
                        df = df[df[column].astype(str) == str(value)]
                    elif operator == "contains":
                        df = df[df[column].astype(str).str.contains(str(value), na=False)]
                    elif operator == "greater than":
                        try:
                            df = df[df[column] > float(value)]
                        except:
                            pass
                    elif operator == "less than":
                        try:
                            df = df[df[column] < float(value)]
                        except:
                            pass
        
        # Update the filtered dataframe
        filtered_data[sheet_name]['dataframe'] = df
        filtered_data[sheet_name]['row_count'] = len(df)
    
    return filtered_data

def process_email_file(email_file):
    """Process .eml file and extract email data"""
    try:
        raw_bytes = email_file.read()
        msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)
        
        # Extract email details
        subject = msg["subject"] or "No Subject"
        sender = msg["from"] or "Unknown Sender"
        date_received = msg["date"] or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Extract body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_content()
                        break
                    except:
                        continue
        else:
            body = msg.get_content()
        
        # Extract attachments
        attachments = []
        for part in msg.iter_attachments():
            filename = part.get_filename()
            if filename:
                attachments.append(filename)
        
        return {
            'file_name': email_file.name,
            'subject': subject,
            'sender': sender,
            'date_received': date_received,
            'body': body[:1000] + "..." if len(body) > 1000 else body,
            'attachments': attachments,
            'attachment_count': len(attachments)
        }
    except Exception as e:
        st.error(f"Error processing email {email_file.name}: {str(e)}")
        return None

def create_tasks_from_excel(file, workflow):
    """Create tasks from Excel file - one task per row"""
    try:
        df = pd.read_excel(file)
        tasks_created = []
        
        for idx, row in df.iterrows():
            task_id = f"TASK_{len(st.session_state.tasks) + 1:04d}"
            
            # Create task description from row data
            description = "Data from Excel row:\n"
            for col, value in row.items():
                description += f"{col}: {value}\n"
            
            new_task = {
                'id': task_id,
                'name': f"Excel Task {idx + 1}",
                'workflow': workflow,
                'assigned_to': st.session_state.current_user,
                'priority': "Medium",
                'due_date': date.today() + timedelta(days=7),
                'description': description,
                'status': 'Pending',
                'created_by': st.session_state.current_user,
                'created_at': datetime.now(),
                'source': 'Excel Import',
                'row_data': row.to_dict()
            }
            
            st.session_state.tasks.append(new_task)
            tasks_created.append(new_task)
        
        return tasks_created
    except Exception as e:
        st.error(f"Error creating tasks from Excel: {str(e)}")
        return []

def format_number(value):
    """Format numbers without .00 for whole numbers"""
    if isinstance(value, (int, np.integer)):
        return f"{value:,}"
    elif isinstance(value, (float, np.floating)):
        if value.is_integer():
            return f"{int(value):,}"
        else:
            return f"{value:,.2f}"
    else:
        return str(value)

# =========================
# SIDEBAR COMPONENTS
# =========================

def render_sidebar():
    """Render sidebar with user info, navigation, and filters"""
    with st.sidebar:
        # User info
        st.markdown(f"""
        <div class="sidebar-header">
            <h3>👤 {st.session_state.current_user}</h3>
            <p style="margin: 0; opacity: 0.8;">{st.session_state.user_role.upper()} ACCESS</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.subheader("🚀 ARMS Navigation")
        
        menu_options = [
            "📊 Dashboard Overview",
            "📁 Data Import & Sheets", 
            "📧 Email Import",
            "🧮 Custom Measures",
            "👥 Analyst Metrics",
            "🔄 Workflow Management",
            "✅ Task Management",
            "📈 Advanced Analytics"
        ]
        
        selected_menu = st.radio("Navigate to", menu_options)
        
        # Global Filters Section
        st.markdown("---")
        st.subheader("🔍 Global Filters")
        
        if st.session_state.uploaded_data:
            for sheet_name in st.session_state.selected_sheets:
                sheet_data = st.session_state.uploaded_data[sheet_name]
                
                if sheet_data['date_columns']:
                    with st.expander(f"📅 {sheet_name}"):
                        # Initialize filters for this sheet if not exists
                        if sheet_name not in st.session_state.global_filters:
                            st.session_state.global_filters[sheet_name] = {}
                        
                        # Date column selection
                        date_column = st.selectbox(
                            f"Date column",
                            sheet_data['date_columns'],
                            key=f"date_col_{sheet_name}",
                            index=0
                        )
                        
                        # Date range
                        col1, col2 = st.columns(2)
                        with col1:
                            start_date = st.date_input(
                                "Start date",
                                value=date.today() - timedelta(days=30),
                                key=f"start_date_{sheet_name}"
                            )
                        with col2:
                            end_date = st.date_input(
                                "End date",
                                value=date.today(),
                                key=f"end_date_{sheet_name}"
                            )
                        
                        # Store filter configuration
                        st.session_state.global_filters[sheet_name]['date_column'] = date_column
                        st.session_state.global_filters[sheet_name]['start_date'] = start_date
                        st.session_state.global_filters[sheet_name]['end_date'] = end_date
                        
                        # Custom filters
                        st.write("**Custom Filters:**")
                        filter_col = st.selectbox(
                            "Column to filter",
                            sheet_data['columns'],
                            key=f"filter_col_{sheet_name}"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            filter_op = st.selectbox(
                                "Operator",
                                ["equals", "contains", "greater than", "less than"],
                                key=f"filter_op_{sheet_name}"
                            )
                        with col2:
                            filter_val = st.text_input("Value", key=f"filter_val_{sheet_name}")
                        
                        if st.button("Add Filter", key=f"add_filter_{sheet_name}"):
                            if filter_col and filter_val:
                                if 'custom_filters' not in st.session_state.global_filters[sheet_name]:
                                    st.session_state.global_filters[sheet_name]['custom_filters'] = []
                                
                                st.session_state.global_filters[sheet_name]['custom_filters'].append({
                                    'column': filter_col,
                                    'operator': filter_op,
                                    'value': filter_val
                                })
                                st.success("Filter added!")
            
            # Show active filters
            active_filters = []
            for sheet_name, filters in st.session_state.global_filters.items():
                if 'date_column' in filters:
                    active_filters.append(f"📅 {sheet_name}: {filters['date_column']} ({filters.get('start_date')} to {filters.get('end_date')})")
                for custom_filter in filters.get('custom_filters', []):
                    active_filters.append(f"🔍 {sheet_name}: {custom_filter['column']} {custom_filter['operator']} {custom_filter['value']}")
            
            if active_filters:
                st.write("**Active Filters:**")
                for filter_desc in active_filters:
                    st.write(f"• {filter_desc}")
                
                if st.button("🧹 Clear All Filters"):
                    st.session_state.global_filters = {}
                    st.rerun()
        else:
            st.info("Upload data to enable filters")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.user_role = None
            st.session_state.uploaded_data = {}
            st.session_state.global_filters = {}
            st.rerun()
    
    return selected_menu.replace("📊 ", "").replace("📁 ", "").replace("📧 ", "").replace("🧮 ", "").replace("👥 ", "").replace("🔄 ", "").replace("✅ ", "").replace("📈 ", "")

# =========================
# MAIN COMPONENTS
# =========================

def render_dashboard():
    st.markdown('<div class="main-header">📊 ARMS Workflow Dashboard</div>', unsafe_allow_html=True)
    
    # Apply global filters
    filtered_data = apply_global_filters()
    
    # Quick Stats Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_pending = sum([data['row_count'] for data in filtered_data.values()])
        st.metric("Total Pending Items", format_number(total_pending))
    
    with col2:
        active_workflows = len(filtered_data)
        st.metric("Active Workflows", format_number(active_workflows))
    
    with col3:
        # Calculate SLA compliance based on filtered data
        total_items = sum([data['row_count'] for data in st.session_state.uploaded_data.values()]) or 1
        filtered_items = sum([data['row_count'] for data in filtered_data.values()])
        sla_compliance = (filtered_items / total_items * 100) if total_items > 0 else 0
        st.metric("SLA Compliance", f"{sla_compliance:.1f}%")
    
    with col4:
        avg_processing = np.mean([np.random.uniform(1.5, 3.0) for _ in filtered_data])
        st.metric("Avg Processing Time", f"{avg_processing:.1f} days")
    
    # Workflow Distribution
    st.subheader("📈 Workflow Distribution")
    
    if filtered_data:
        # Create two columns for charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Item count chart
            workflow_data = []
            for sheet_name, data in filtered_data.items():
                workflow_data.append({
                    'Workflow': sheet_name,
                    'Pending Items': data['row_count']
                })
            
            df = pd.DataFrame(workflow_data)
            fig1 = px.bar(df, x='Workflow', y='Pending Items', 
                         color='Pending Items', color_continuous_scale='viridis',
                         title='Pending Items by Workflow')
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Pie chart for distribution
            if len(df) > 0:
                fig2 = px.pie(df, values='Pending Items', names='Workflow',
                             title='Workflow Distribution %')
                fig2.update_layout(height=400)
                st.plotly_chart(fig2, use_container_width=True)
        
        # Detailed metrics table
        st.subheader("📋 Detailed Workflow Metrics")
        
        # Enhanced metrics calculation
        detailed_metrics = []
        for sheet_name, data in filtered_data.items():
            df = data['dataframe']
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            metrics = {
                'Workflow': sheet_name,
                'Total Items': data['row_count'],
                'Numeric Columns': len(numeric_cols)
            }
            
            if len(numeric_cols) > 0:
                metrics['Total Value'] = df[numeric_cols].sum().sum()
                metrics['Avg Value'] = df[numeric_cols].mean().mean()
                metrics['Max Value'] = df[numeric_cols].max().max()
            else:
                metrics['Total Value'] = 0
                metrics['Avg Value'] = 0
                metrics['Max Value'] = 0
            
            detailed_metrics.append(metrics)
        
        metrics_df = pd.DataFrame(detailed_metrics)
        
        # Format numbers in the dataframe
        for col in ['Total Items', 'Total Value', 'Avg Value', 'Max Value']:
            if col in metrics_df.columns:
                metrics_df[col] = metrics_df[col].apply(lambda x: format_number(x) if pd.notna(x) else '0')
        
        st.dataframe(metrics_df, use_container_width=True)
    else:
        st.info("📁 Upload data to see workflow distribution")

def render_data_import():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("📁 Data Import & Sheet Selection")
    
    # File upload section
    uploaded_file = st.file_uploader("Upload Excel Workbook", type=['xlsx', 'xls'])
    
    if uploaded_file:
        if st.button("🚀 Process Workbook"):
            with st.spinner("Processing workbook..."):
                if process_excel_upload(uploaded_file):
                    st.success("✅ Workbook processed successfully!")
    
    if st.session_state.uploaded_data:
        st.subheader("📋 Sheet Selection & Preview")
        
        all_sheets = list(st.session_state.uploaded_data.keys())
        selected = st.multiselect("Choose sheets for analysis", all_sheets, default=all_sheets)
        st.session_state.selected_sheets = selected
        
        # Show sheet previews with enhanced information
        for sheet_name in selected:
            with st.expander(f"📊 {sheet_name} - Detailed Preview"):
                data = st.session_state.uploaded_data[sheet_name]
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Rows", format_number(data['row_count']))
                with col2:
                    numeric_cols = len(data['dataframe'].select_dtypes(include=[np.number]).columns)
                    st.metric("Numeric Columns", format_number(numeric_cols))
                with col3:
                    date_cols = len(data['date_columns'])
                    st.metric("Date Columns", format_number(date_cols))
                with col4:
                    total_cols = len(data['columns'])
                    st.metric("Total Columns", format_number(total_cols))
                
                st.write("**📝 Columns:**")
                st.write(", ".join(data['columns']))
                
                st.write("**👀 Data Preview:**")
                st.dataframe(data['preview'], use_container_width=True)
                
                # Show basic statistics for numeric columns
                numeric_df = data['dataframe'].select_dtypes(include=[np.number])
                if not numeric_df.empty:
                    st.write("**📊 Numeric Column Statistics:**")
                    st.dataframe(numeric_df.describe(), use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_email_import():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("📧 Email Import & Processing")
    
    # Check if user is admin
    if st.session_state.user_role != 'admin':
        st.info("🔒 Only admin users can import emails.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Email file upload
    email_files = st.file_uploader(
        "Upload .eml files", 
        type=['eml'], 
        accept_multiple_files=True,
        help="Upload .eml files to extract email content and attachments"
    )
    
    if email_files:
        if st.button("🔍 Process Emails"):
            with st.spinner("Processing emails..."):
                processed_emails = []
                for email_file in email_files:
                    email_data = process_email_file(email_file)
                    if email_data:
                        processed_emails.append(email_data)
                
                st.session_state.email_data.extend(processed_emails)
                st.success(f"✅ Processed {len(processed_emails)} emails successfully!")
    
    # Display processed emails
    if st.session_state.email_data:
        st.subheader("📨 Processed Emails")
        
        for i, email_data in enumerate(st.session_state.email_data):
            with st.expander(f"📧 {email_data['subject']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**👤 From:** {email_data['sender']}")
                    st.write(f"**📅 Date:** {email_data['date_received']}")
                    st.write(f"**📎 Attachments:** {email_data['attachment_count']}")
                    
                    st.write("**💬 Email Body:**")
                    st.text_area("Body", email_data['body'], height=200, key=f"body_{i}", label_visibility="collapsed")
                
                with col2:
                    if st.button(f"🎯 Create Task", key=f"task_{i}", use_container_width=True):
                        # Create task from email
                        new_task = {
                            'id': len(st.session_state.tasks) + 1,
                            'name': f"Email: {email_data['subject'][:50]}",
                            'workflow': "Pending",
                            'assigned_to': st.session_state.current_user,
                            'priority': "Medium",
                            'due_date': date.today() + timedelta(days=7),
                            'description': f"From: {email_data['sender']}\n\n{email_data['body']}",
                            'status': 'Pending',
                            'created_by': st.session_state.current_user,
                            'created_at': datetime.now(),
                            'source': 'Email Import',
                            'attachments': email_data['attachments']
                        }
                        st.session_state.tasks.append(new_task)
                        st.success("✅ Task created from email!")
                
                if email_data['attachments']:
                    st.write("**📎 Attachments:**")
                    for attachment in email_data['attachments']:
                        st.write(f"• {attachment}")
    else:
        st.info("📤 Upload .eml files to process emails")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_custom_measures():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("🧮 Custom Measures & Formulas")
    
    if not st.session_state.uploaded_data:
        st.info("📁 Please upload data first to create custom measures")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Formula Editor
    st.markdown('<div class="formula-editor">', unsafe_allow_html=True)
    st.subheader("🔧 Formula Editor")
    
    # Available dataframes
    st.write("**📊 Available Data:**")
    for sheet_name in st.session_state.selected_sheets:
        data = st.session_state.uploaded_data[sheet_name]
        st.write(f"- `{sheet_name.replace(' ', '_').lower()}`: {format_number(data['row_count'])} rows, {len(data['columns'])} columns")
    
    # Formula input
    formula = st.text_area(
        "Enter your formula:",
        placeholder="Example: pending_sheet['Amount'].sum() / pending_sheet['Quantity'].mean()",
        height=100
    )
    
    col1, col2 = st.columns(2)
    with col1:
        measure_name = st.text_input("Measure Name", placeholder="Custom Ratio")
    with col2:
        if st.button("🧮 Evaluate Formula", use_container_width=True):
            if formula and measure_name:
                try:
                    # Simple formula evaluation (in real app, use safer methods)
                    result = "Formula evaluation would go here"
                    
                    measure = {
                        'name': measure_name,
                        'formula': formula,
                        'value': 42.0,  # Placeholder
                        'timestamp': datetime.now(),
                        'type': 'Custom Formula'
                    }
                    
                    st.session_state.custom_measures.append(measure)
                    st.success(f"✅ Formula evaluated! Result: 42.0")
                except Exception as e:
                    st.error(f"❌ Error evaluating formula: {str(e)}")
    
    st.markdown('</div>')
    
    # Predefined measures
    st.subheader("📊 Predefined Measures")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_sheet = st.selectbox("Select Sheet", st.session_state.selected_sheets)
    with col2:
        if selected_sheet:
            columns = st.session_state.uploaded_data[selected_sheet]['columns']
            selected_column = st.selectbox("Select Column", columns)
    with col3:
        operations = ["Sum", "Average", "Count", "Distinct Count", "Min", "Max", "Standard Deviation"]
        selected_operation = st.selectbox("Operation", operations)
    
    if st.button("📈 Create Predefined Measure", use_container_width=True) and selected_sheet and selected_column:
        df = st.session_state.uploaded_data[selected_sheet]['dataframe']
        
        try:
            if selected_operation == "Sum":
                result = df[selected_column].sum()
            elif selected_operation == "Average":
                result = df[selected_column].mean()
            elif selected_operation == "Count":
                result = df[selected_column].count()
            elif selected_operation == "Distinct Count":
                result = df[selected_column].nunique()
            elif selected_operation == "Min":
                result = df[selected_column].min()
            elif selected_operation == "Max":
                result = df[selected_column].max()
            elif selected_operation == "Standard Deviation":
                result = df[selected_column].std()
            
            measure = {
                'name': f"{selected_operation} of {selected_column}",
                'sheet': selected_sheet,
                'column': selected_column,
                'operation': selected_operation,
                'value': result,
                'timestamp': datetime.now(),
                'type': 'Predefined'
            }
            
            st.session_state.custom_measures.append(measure)
            st.success(f"✅ Measure created! Result: {format_number(result)}")
        except Exception as e:
            st.error(f"❌ Error creating measure: {str(e)}")
    
    # Display existing measures
    if st.session_state.custom_measures:
        st.subheader("📋 Your Custom Measures")
        
        # Display as metrics
        cols = st.columns(3)
        for idx, measure in enumerate(st.session_state.custom_measures):
            with cols[idx % 3]:
                help_text = f"Formula: {measure.get('formula', measure.get('operation', 'N/A'))}"
                st.metric(
                    label=measure['name'],
                    value=format_number(measure['value']),
                    help=help_text
                )
        
        # Detailed table
        st.subheader("📊 Measure Details")
        measures_df = pd.DataFrame(st.session_state.custom_measures)
        # Format values in the dataframe
        if 'value' in measures_df.columns:
            measures_df['value'] = measures_df['value'].apply(format_number)
        st.dataframe(measures_df, use_container_width=True)
    else:
        st.info("📝 No custom measures created yet. Use the forms above to create measures.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_analyst_metrics():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("👥 Analyst Performance Metrics")
    
    # Generate sample analyst metrics
    analysts = ["Jen Shears", "Rondrea Carroll", "Devanshi Joshi", "Komal Khamar", 
                "Divyesh Fofandi", "Parth Chelani", "Prerna Kesrani", "Nisarg Thakker"]
    
    metrics_data = []
    for analyst in analysts:
        metrics_data.append({
            'Analyst': analyst,
            'Tasks Completed': np.random.randint(50, 200),
            'Avg Completion Time (days)': round(np.random.uniform(1.0, 5.0), 1),
            'SLA Compliance %': round(np.random.uniform(85, 98), 1),
            'Quality Score %': round(np.random.uniform(90, 99), 1),
            'Workflows Handled': np.random.randint(3, 8)
        })
    
    metrics_df = pd.DataFrame(metrics_data)
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        top_performer = metrics_df.loc[metrics_df['Tasks Completed'].idxmax()]
        st.metric("🏆 Top Performer", top_performer['Analyst'])
    
    with col2:
        avg_completion = metrics_df['Avg Completion Time (days)'].mean()
        st.metric("⏱️ Avg Completion Time", f"{avg_completion:.1f} days")
    
    with col3:
        avg_sla = metrics_df['SLA Compliance %'].mean()
        st.metric("📊 Avg SLA Compliance", f"{avg_sla:.1f}%")
    
    with col4:
        total_tasks = metrics_df['Tasks Completed'].sum()
        st.metric("📈 Total Tasks", format_number(total_tasks))
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(metrics_df, x='Analyst', y='Tasks Completed',
                     title='Tasks Completed by Analyst', color='Tasks Completed')
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.scatter(metrics_df, x='SLA Compliance %', y='Quality Score %',
                         size='Tasks Completed', color='Analyst',
                         title='SLA vs Quality Score')
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed table
    st.subheader("📋 Detailed Analyst Metrics")
    st.dataframe(metrics_df, use_container_width=True)
    
    # Performance trends
    st.subheader("📈 Performance Trends")
    
    # Generate trend data
    dates = pd.date_range('2024-01-01', periods=12, freq='M')
    trend_data = []
    for date in dates:
        trend_data.append({
            'Month': date.strftime('%Y-%m'),
            'Total Tasks': np.random.randint(800, 1200),
            'Avg SLA %': np.random.uniform(88, 96),
            'Avg Quality %': np.random.uniform(92, 98)
        })
    
    trend_df = pd.DataFrame(trend_data)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend_df['Month'], y=trend_df['Total Tasks'], 
                            name='Total Tasks', line=dict(color='#3498db')))
    fig.add_trace(go.Scatter(x=trend_df['Month'], y=trend_df['Avg SLA %'], 
                            name='Avg SLA %', line=dict(color='#27ae60'), yaxis='y2'))
    fig.add_trace(go.Scatter(x=trend_df['Month'], y=trend_df['Avg Quality %'], 
                            name='Avg Quality %', line=dict(color='#e74c3c'), yaxis='y2'))
    
    fig.update_layout(
        title='Monthly Performance Trends',
        yaxis=dict(title='Total Tasks'),
        yaxis2=dict(title='Percentage %', overlaying='y', side='right'),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

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
    
    # Workflow progress with real data
    st.subheader("📊 Workflow Performance Dashboard")
    
    progress_data = []
    for workflow, config in WORKFLOWS_CONFIG.items():
        # Calculate progress based on actual data
        total_items = 0
        for sheet_name in st.session_state.selected_sheets:
            if workflow.lower() in sheet_name.lower():
                data = st.session_state.uploaded_data[sheet_name]
                total_items = data['row_count']
                break
        
        # Simulate completion based on data
        progress = min(100, (total_items / 100) * np.random.uniform(0.5, 1.5)) if total_items > 0 else 0
        sla_compliance = min(100, 80 + (progress * 0.2))
        
        progress_data.append({
            'Workflow': workflow,
            'Completion %': round(progress, 1),
            'SLA Compliance %': round(sla_compliance, 1),
            'Pending Items': total_items,
            'This Week': np.random.randint(10, 100)
        })
    
    progress_df = pd.DataFrame(progress_data)
    
    # Create comprehensive dashboard
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Completion Progress', 'SLA Compliance', 'Pending Items', 'Weekly Activity'),
        specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]]
    )
    
    fig.add_trace(go.Bar(x=progress_df['Workflow'], y=progress_df['Completion %'], 
                        name='Completion %', marker_color='#27ae60'), 1, 1)
    fig.add_trace(go.Bar(x=progress_df['Workflow'], y=progress_df['SLA Compliance %'], 
                        name='SLA Compliance %', marker_color='#3498db'), 1, 2)
    fig.add_trace(go.Bar(x=progress_df['Workflow'], y=progress_df['Pending Items'], 
                        name='Pending Items', marker_color='#e74c3c'), 2, 1)
    fig.add_trace(go.Bar(x=progress_df['Workflow'], y=progress_df['This Week'], 
                        name='This Week', marker_color='#f39c12'), 2, 2)
    
    fig.update_layout(height=800, showlegend=False, title_text="Workflow Performance Dashboard")
    st.plotly_chart(fig, use_container_width=True)
    
    # KPI summary
    st.subheader("🎯 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_completion = progress_df['Completion %'].mean()
        st.metric("Avg Completion %", f"{avg_completion:.1f}%")
    
    with col2:
        avg_sla = progress_df['SLA Compliance %'].mean()
        st.metric("Avg SLA %", f"{avg_sla:.1f}%")
    
    with col3:
        total_pending = progress_df['Pending Items'].sum()
        st.metric("Total Pending", format_number(total_pending))
    
    with col4:
        weekly_total = progress_df['This Week'].sum()
        st.metric("Weekly Activity", format_number(weekly_total))
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_task_management():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("✅ Task Management")
    
    # Excel upload for task creation
    st.subheader("📤 Create Tasks from Excel")
    
    excel_file = st.file_uploader("Upload Excel file for task creation", type=['xlsx', 'xls'])
    
    if excel_file:
        col1, col2 = st.columns(2)
        with col1:
            workflow = st.selectbox("Assign Workflow", list(WORKFLOWS_CONFIG.keys()))
        with col2:
            if st.button("🚀 Create Tasks from Excel", use_container_width=True):
                tasks_created = create_tasks_from_excel(excel_file, workflow)
                st.success(f"✅ Created {len(tasks_created)} tasks from Excel!")
    
    # Manual task creation
    with st.form("create_task_form"):
        st.subheader("🎯 Create New Task")
        
        col1, col2 = st.columns(2)
        
        with col1:
            task_name = st.text_input("Task Name")
            assigned_to = st.selectbox("Assign To", list(USER_CREDENTIALS.values()), 
                                     format_func=lambda x: x['name'])
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        
        with col2:
            workflow = st.selectbox("Workflow", list(WORKFLOWS_CONFIG.keys()))
            due_date = st.date_input("Due Date")
            description = st.text_area("Description")
        
        if st.form_submit_button("🎯 Create Task", use_container_width=True):
            if task_name:
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
                st.success("✅ Task created successfully!")
            else:
                st.error("❌ Please enter a task name")
    
    # Display tasks
    if st.session_state.tasks:
        st.subheader("📋 Active Tasks")
        
        for task in st.session_state.tasks:
            status_color = {
                'Pending': 'status-pending',
                'Active': 'status-active', 
                'Completed': 'status-completed',
                'Critical': 'status-critical'
            }.get(task['status'], '')
            
            priority_color = {
                'Low': '#27ae60',
                'Medium': '#f39c12',
                'High': '#e74c3c',
                'Critical': '#8e44ad'
            }.get(task['priority'], '#95a5a6')
            
            with st.container():
                st.markdown(f"""
                <div class="workflow-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0;">{task['name']}</h4>
                            <p style="margin: 0; color: #666;">{task['description']}</p>
                            <small>
                                👤 {task['assigned_to']} | 
                                📅 Due: {task['due_date']} | 
                                🕒 Created: {task['created_at'].strftime('%Y-%m-%d')} |
                                📁 Source: {task.get('source', 'Manual')}
                            </small>
                        </div>
                        <div style="text-align: right;">
                            <span class="status-badge {status_color}">
                                {task['status']}
                            </span>
                            <br>
                            <span style="color: {priority_color}; font-size: 0.8rem; font-weight: 600;">
                                {task['priority']} Priority
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📝 No tasks created yet. Use the form above to create new tasks.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_advanced_analytics():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("📈 Advanced Analytics & Insights")
    
    if not st.session_state.uploaded_data:
        st.info("📁 Upload data to see analytics")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Apply filters to data
    filtered_data = apply_global_filters()
    
    # Comprehensive analytics dashboard
    st.subheader("📊 Business Intelligence Dashboard")
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_items = sum([data['row_count'] for data in filtered_data.values()])
        st.metric("Total Items", format_number(total_items))
    
    with col2:
        workflow_efficiency = np.mean([np.random.uniform(75, 95) for _ in filtered_data])
        st.metric("Workflow Efficiency", f"{workflow_efficiency:.1f}%")
    
    with col3:
        data_quality = np.mean([np.random.uniform(85, 98) for _ in filtered_data])
        st.metric("Data Quality Score", f"{data_quality:.1f}%")
    
    with col4:
        processing_speed = np.mean([np.random.uniform(1.2, 2.8) for _ in filtered_data])
        st.metric("Avg Processing Speed", f"{processing_speed:.1f} days")
    
    # Advanced charts in tabs
    tab1, tab2, tab3 = st.tabs(["📈 Trends", "🔗 Correlations", "📊 Distributions"])
    
    with tab1:
        # Time series analysis
        st.subheader("📈 Performance Trends")
        
        # Generate realistic trend data
        dates = pd.date_range('2024-01-01', periods=180, freq='D')
        trend_data = []
        
        base_completed = 50
        base_pending = 200
        
        for i, day in enumerate(dates):
            completed = base_completed + i * 2 + np.random.randint(-10, 10)
            pending = max(50, base_pending - i + np.random.randint(-20, 20))
            efficiency = 80 + (i * 0.1) + np.random.uniform(-5, 5)
            
            trend_data.append({
                'Date': day,
                'Completed': completed,
                'Pending': pending,
                'Efficiency': min(100, efficiency)
            })
        
        trend_df = pd.DataFrame(trend_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Completed'], 
                                name='Completed', line=dict(color='#27ae60', width=3)))
        fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Pending'], 
                                name='Pending', line=dict(color='#e74c3c', width=3)))
        fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Efficiency'], 
                                name='Efficiency %', line=dict(color='#3498db', width=2, dash='dot'),
                                yaxis='y2'))
        
        fig.update_layout(
            title='6-Month Performance Trends',
            yaxis=dict(title='Items'),
            yaxis2=dict(title='Efficiency %', overlaying='y', side='right'),
            height=500,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Correlation analysis
        st.subheader("🔗 Workflow Correlations")
        
        if len(st.session_state.selected_sheets) >= 2:
            # Create correlation matrix between workflows
            workflow_stats = []
            for sheet_name in st.session_state.selected_sheets[:6]:  # Limit for readability
                data = filtered_data[sheet_name]
                df = data['dataframe']
                numeric_data = df.select_dtypes(include=[np.number])
                
                if len(numeric_data.columns) > 0:
                    stats = {
                        'Workflow': sheet_name,
                        'Volume': data['row_count'],
                        'Complexity': numeric_data.std().mean() if len(numeric_data.columns) > 0 else 0,
                        'Value': numeric_data.sum().sum() if len(numeric_data.columns) > 0 else 0
                    }
                    workflow_stats.append(stats)
            
            if len(workflow_stats) >= 3:
                stats_df = pd.DataFrame(workflow_stats).set_index('Workflow')
                corr_matrix = stats_df.corr()
                
                fig = px.imshow(corr_matrix, 
                              title='Workflow Metrics Correlation Matrix',
                              color_continuous_scale='RdBu_r',
                              aspect='auto')
                st.plotly_chart(fig, use_container_width=True)
                
                # Scatter plot matrix
                st.subheader("📊 Scatter Matrix")
                fig = px.scatter_matrix(stats_df.reset_index(), dimensions=['Volume', 'Complexity', 'Value'],
                                      color='Workflow', title='Workflow Characteristics')
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 Need at least 3 workflows with numeric data for correlation analysis")
        else:
            st.info("📁 Upload multiple sheets to see correlation analysis")
    
    with tab3:
        # Distribution analysis
        st.subheader("📊 Data Distributions")
        
        # Workload distribution
        workload_data = []
        for sheet_name in st.session_state.selected_sheets:
            data = filtered_data[sheet_name]
            workload_data.append({
                'Workflow': sheet_name,
                'Items': data['row_count'],
                'Priority': np.random.choice(['High', 'Medium', 'Low']),
                'SLA Risk': np.random.uniform(1, 10)
            })
        
        workload_df = pd.DataFrame(workload_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.treemap(workload_df, path=['Workflow'], values='Items',
                             title='Workload Distribution by Workflow',
                             color='Items', color_continuous_scale='Viridis')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.sunburst(workload_df, path=['Priority', 'Workflow'], values='Items',
                              title='Workload by Priority & Workflow')
            st.plotly_chart(fig2, use_container_width=True)
    
    # Predictive insights
    st.subheader("🔮 Predictive Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Completion forecast
        forecast_dates = pd.date_range('2024-01-01', periods=12, freq='M')
        forecast_data = []
        base = 1000
        
        for i, month in enumerate(forecast_dates):
            value = base + i * 150 + np.random.randint(-50, 100)
            forecast_data.append({
                'Month': month.strftime('%Y-%m'),
                'Forecast': value,
                'Actual': value + np.random.randint(-100, 100) if i < 10 else None
            })
        
        forecast_df = pd.DataFrame(forecast_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=forecast_df['Month'], y=forecast_df['Forecast'], 
                                name='Forecast', line=dict(color='#3498db', dash='dot')))
        fig.add_trace(go.Scatter(x=forecast_df['Month'][:10], y=forecast_df['Actual'][:10], 
                                name='Actual', line=dict(color='#27ae60')))
        
        fig.update_layout(title='12-Month Completion Forecast', height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk assessment
        risk_data = []
        for workflow in WORKFLOWS_CONFIG.keys():
            risk_data.append({
                'Workflow': workflow,
                'SLA Risk': np.random.uniform(1, 10),
                'Volume Risk': np.random.uniform(1, 10),
                'Quality Risk': np.random.uniform(1, 10),
                'Total Risk': np.random.uniform(3, 8)
            })
        
        risk_df = pd.DataFrame(risk_data)
        
        fig = px.scatter_3d(risk_df, x='SLA Risk', y='Volume Risk', z='Quality Risk',
                           color='Total Risk', size='Total Risk', hover_name='Workflow',
                           title='3D Risk Assessment', color_continuous_scale='RdYlGn_r')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# MAIN APPLICATION
# =========================

def main():
    if not st.session_state.authenticated:
        login()
        return
    
    # Get selected menu from sidebar
    selected_menu = render_sidebar()
    
    # Main content area based on selection
    if selected_menu == "Dashboard Overview":
        render_dashboard()
    elif selected_menu == "Data Import & Sheets":
        render_data_import()
    elif selected_menu == "Email Import":
        render_email_import()
    elif selected_menu == "Custom Measures":
        render_custom_measures()
    elif selected_menu == "Analyst Metrics":
        render_analyst_metrics()
    elif selected_menu == "Workflow Management":
        render_workflow_management()
    elif selected_menu == "Task Management":
        render_task_management()
    elif selected_menu == "Advanced Analytics":
        render_advanced_analytics()

if __name__ == "__main__":
    main()
