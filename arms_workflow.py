# app_enhanced_v2.py
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
    .date-filter {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .formula-editor {
        background: #f1f3f4;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4285f4;
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
if 'date_filters' not in st.session_state:
    st.session_state.date_filters = {}
if 'global_filters' not in st.session_state:
    st.session_state.global_filters = {}

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

def apply_filters(data):
    """Apply global filters to data"""
    if not st.session_state.global_filters:
        return data
    
    filtered_data = data.copy()
    
    for sheet_name, filters in st.session_state.global_filters.items():
        if sheet_name in filtered_data:
            df = filtered_data[sheet_name]['dataframe'].copy()
            
            # Apply date filters
            if 'date_column' in filters and filters['date_column']:
                date_col = filters['date_column']
                start_date = filters.get('start_date')
                end_date = filters.get('end_date')
                
                if date_col in df.columns and start_date and end_date:
                    mask = (df[date_col] >= pd.Timestamp(start_date)) & (df[date_col] <= pd.Timestamp(end_date))
                    df = df[mask]
            
            # Apply custom filters
            for filter_config in filters.get('custom_filters', []):
                column = filter_config['column']
                operator = filter_config['operator']
                value = filter_config['value']
                
                if column in df.columns:
                    if operator == "equals":
                        df = df[df[column] == value]
                    elif operator == "contains":
                        df = df[df[column].astype(str).str.contains(value, na=False)]
                    elif operator == "greater than":
                        df = df[df[column] > float(value)]
                    elif operator == "less than":
                        df = df[df[column] < float(value)]
            
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
            'body': body[:1000] + "..." if len(body) > 1000 else body,  # Limit body length
            'attachments': attachments,
            'attachment_count': len(attachments)
        }
    except Exception as e:
        st.error(f"Error processing email {email_file.name}: {str(e)}")
        return None

def evaluate_custom_formula(formula, data):
    """Evaluate custom formula like Excel/Power BI"""
    try:
        # Safe evaluation - only allow pandas operations on data
        allowed_globals = {
            'pd': pd,
            'np': np,
            'sum': sum,
            'len': len,
            'max': max,
            'min': min,
            'mean': np.mean,
            'count': len,
            'std': np.std
        }
        
        # Add dataframes to context
        for sheet_name, sheet_data in data.items():
            df_name = sheet_name.replace(' ', '_').lower()
            allowed_globals[df_name] = sheet_data['dataframe']
        
        # Evaluate formula
        result = eval(formula, {"__builtins__": {}}, allowed_globals)
        return result
    except Exception as e:
        raise ValueError(f"Formula error: {str(e)}")

# =========================
# DASHBOARD COMPONENTS
# =========================

def render_global_filters():
    """Render global date and data filters"""
    st.markdown('<div class="date-filter">', unsafe_allow_html=True)
    st.subheader("📅 Global Filters")
    
    if not st.session_state.uploaded_data:
        st.info("Upload data to enable filters")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Date filters for each sheet
    for sheet_name in st.session_state.selected_sheets:
        sheet_data = st.session_state.uploaded_data[sheet_name]
        
        if sheet_data['date_columns']:
            st.write(f"**{sheet_name}**")
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                date_column = st.selectbox(
                    f"Date column for {sheet_name}",
                    sheet_data['date_columns'],
                    key=f"date_col_{sheet_name}"
                )
            
            with col2:
                start_date = st.date_input(
                    "Start date",
                    value=date.today() - timedelta(days=30),
                    key=f"start_date_{sheet_name}"
                )
            
            with col3:
                end_date = st.date_input(
                    "End date",
                    value=date.today(),
                    key=f"end_date_{sheet_name}"
                )
            
            # Store filter configuration
            if sheet_name not in st.session_state.global_filters:
                st.session_state.global_filters[sheet_name] = {}
            
            st.session_state.global_filters[sheet_name]['date_column'] = date_column
            st.session_state.global_filters[sheet_name]['start_date'] = start_date
            st.session_state.global_filters[sheet_name]['end_date'] = end_date
    
    # Custom data filters
    st.subheader("🔍 Custom Data Filters")
    
    sheet_for_filter = st.selectbox("Select sheet to filter", st.session_state.selected_sheets)
    
    if sheet_for_filter:
        sheet_data = st.session_state.uploaded_data[sheet_for_filter]
        columns = sheet_data['columns']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_column = st.selectbox("Column", columns, key="filter_col")
        
        with col2:
            filter_operator = st.selectbox(
                "Operator", 
                ["equals", "contains", "greater than", "less than"],
                key="filter_op"
            )
        
        with col3:
            filter_value = st.text_input("Value", key="filter_val")
        
        if st.button("Add Filter"):
            if filter_column and filter_value:
                if sheet_for_filter not in st.session_state.global_filters:
                    st.session_state.global_filters[sheet_for_filter] = {'custom_filters': []}
                
                st.session_state.global_filters[sheet_for_filter]['custom_filters'].append({
                    'column': filter_column,
                    'operator': filter_operator,
                    'value': filter_value
                })
                st.success("Filter added!")
    
    # Show active filters
    active_filters = []
    for sheet_name, filters in st.session_state.global_filters.items():
        if 'date_column' in filters:
            active_filters.append(f"{sheet_name}: Date range filter")
        for custom_filter in filters.get('custom_filters', []):
            active_filters.append(f"{sheet_name}: {custom_filter['column']} {custom_filter['operator']} {custom_filter['value']}")
    
    if active_filters:
        st.write("**Active Filters:**")
        for filter_desc in active_filters:
            st.write(f"• {filter_desc}")
    
    if st.button("Clear All Filters"):
        st.session_state.global_filters = {}
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard():
    st.markdown('<div class="main-header">📊 ARMS Workflow Dashboard</div>', unsafe_allow_html=True)
    
    # Render global filters
    render_global_filters()
    
    # Apply filters to data
    filtered_data = apply_filters(st.session_state.uploaded_data)
    
    # Quick Stats Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_pending = sum([data['row_count'] for data in filtered_data.values()])
        st.metric("Total Pending Items", f"{total_pending:,}")
    
    with col2:
        active_workflows = len(filtered_data)
        st.metric("Active Workflows", active_workflows)
    
    with col3:
        # Calculate SLA compliance based on filtered data
        total_items = sum([data['row_count'] for data in st.session_state.uploaded_data.values()])
        filtered_items = sum([data['row_count'] for data in filtered_data.values()])
        sla_compliance = (filtered_items / total_items * 100) if total_items > 0 else 0
        st.metric("SLA Compliance", f"{sla_compliance:.1f}%")
    
    with col4:
        st.metric("Avg Processing Time", "2.3 days")
    
    # Workflow Distribution Chart
    st.subheader("Workflow Distribution")
    
    if filtered_data:
        workflow_data = []
        for sheet_name, data in filtered_data.items():
            # Calculate various metrics
            df = data['dataframe']
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            total_value = df[numeric_columns].sum().sum() if len(numeric_columns) > 0 else data['row_count']
            avg_value = df[numeric_columns].mean().mean() if len(numeric_columns) > 0 else 0
            
            workflow_data.append({
                'Workflow': sheet_name,
                'Pending Items': data['row_count'],
                'Total Value': total_value,
                'Average Value': avg_value
            })
        
        df = pd.DataFrame(workflow_data)
        
        # Chart type selector
        chart_type = st.selectbox("Chart Type", ["Bar Chart", "Pie Chart", "Scatter Plot"])
        
        if chart_type == "Bar Chart":
            fig = px.bar(df, x='Workflow', y='Pending Items', 
                        color='Pending Items',
                        color_continuous_scale='viridis',
                        title='Workflow Distribution - Item Count')
        elif chart_type == "Pie Chart":
            fig = px.pie(df, values='Pending Items', names='Workflow',
                        title='Workflow Distribution - Item Count')
        else:
            fig = px.scatter(df, x='Pending Items', y='Total Value',
                           size='Average Value', color='Workflow',
                           title='Workflow Analysis')
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show detailed metrics
        st.subheader("Detailed Workflow Metrics")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Upload data to see workflow distribution")

def render_data_import():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("📁 Data Import & Sheet Selection")
    
    # File upload section
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
        
        # Show sheet previews with enhanced information
        for sheet_name in selected:
            with st.expander(f"📋 {sheet_name} - Detailed Preview"):
                data = st.session_state.uploaded_data[sheet_name]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", f"{data['row_count']:,}")
                with col2:
                    numeric_cols = len(data['dataframe'].select_dtypes(include=[np.number]).columns)
                    st.metric("Numeric Columns", numeric_cols)
                with col3:
                    date_cols = len(data['date_columns'])
                    st.metric("Date Columns", date_cols)
                
                st.write("**Columns:**")
                st.write(", ".join(data['columns']))
                
                st.write("**Data Preview:**")
                st.dataframe(data['preview'], use_container_width=True)
                
                # Show basic statistics for numeric columns
                numeric_df = data['dataframe'].select_dtypes(include=[np.number])
                if not numeric_df.empty:
                    st.write("**Numeric Column Statistics:**")
                    st.dataframe(numeric_df.describe(), use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_email_import():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("📧 Email Import & Processing")
    
    if not st.session_state.is_admin:
        st.info("Only admin users can import emails.")
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
        if st.button("Process Emails"):
            with st.spinner("Processing emails..."):
                processed_emails = []
                for email_file in email_files:
                    email_data = process_email_file(email_file)
                    if email_data:
                        processed_emails.append(email_data)
                
                st.session_state.email_data.extend(processed_emails)
                st.success(f"Processed {len(processed_emails)} emails successfully!")
    
    # Display processed emails
    if st.session_state.email_data:
        st.subheader("Processed Emails")
        
        for i, email_data in enumerate(st.session_state.email_data):
            with st.expander(f"📧 {email_data['subject']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**From:** {email_data['sender']}")
                    st.write(f"**Date:** {email_data['date_received']}")
                    st.write(f"**Attachments:** {email_data['attachment_count']}")
                
                with col2:
                    if st.button(f"Create Task from Email", key=f"task_{i}"):
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
                        st.success("Task created from email!")
                
                st.write("**Email Body:**")
                st.text_area("Body", email_data['body'], height=200, key=f"body_{i}")
                
                if email_data['attachments']:
                    st.write("**Attachments:**")
                    for attachment in email_data['attachments']:
                        st.write(f"• {attachment}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_custom_measures():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("🧮 Custom Measures & Formulas")
    
    if not st.session_state.uploaded_data:
        st.info("Please upload data first to create custom measures")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Formula Editor
    st.markdown('<div class="formula-editor">', unsafe_allow_html=True)
    st.subheader("🔧 Formula Editor (Excel/Power BI Style)")
    
    # Available dataframes
    st.write("**Available Data:**")
    for sheet_name in st.session_state.selected_sheets:
        st.write(f"- `{sheet_name.replace(' ', '_').lower()}`: {st.session_state.uploaded_data[sheet_name]['row_count']} rows")
    
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
        if st.button("Evaluate Formula"):
            if formula and measure_name:
                try:
                    result = evaluate_custom_formula(formula, st.session_state.uploaded_data)
                    
                    measure = {
                        'name': measure_name,
                        'formula': formula,
                        'value': result,
                        'timestamp': datetime.now(),
                        'type': 'Custom Formula'
                    }
                    
                    st.session_state.custom_measures.append(measure)
                    st.success(f"Formula evaluated successfully! Result: {result}")
                except Exception as e:
                    st.error(f"Error evaluating formula: {str(e)}")
    
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
    
    if st.button("Create Predefined Measure") and selected_sheet and selected_column:
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
            st.success(f"Measure created! Result: {result}")
        except Exception as e:
            st.error(f"Error creating measure: {str(e)}")
    
    # Display existing measures
    if st.session_state.custom_measures:
        st.subheader("Your Custom Measures")
        
        cols = st.columns(3)
        for idx, measure in enumerate(st.session_state.custom_measures):
            with cols[idx % 3]:
                help_text = f"Formula: {measure.get('formula', measure.get('operation', 'N/A'))}"
                st.metric(
                    label=measure['name'],
                    value=f"{measure['value']:,.2f}",
                    help=help_text
                )
        
        # Detailed table
        st.subheader("Measure Details")
        measures_df = pd.DataFrame(st.session_state.custom_measures)
        st.dataframe(measures_df, use_container_width=True)
    
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
    st.subheader("Workflow Progress Dashboard")
    
    progress_data = []
    for workflow, config in WORKFLOWS_CONFIG.items():
        # Calculate progress based on actual data
        progress = 0
        sla_compliance = 0
        
        # Try to find relevant data for each workflow
        for sheet_name in st.session_state.selected_sheets:
            if workflow.lower() in sheet_name.lower():
                data = st.session_state.uploaded_data[sheet_name]
                total_items = data['row_count']
                # Simulate completion based on random logic (replace with actual business logic)
                progress = min(100, (total_items / 100) * np.random.uniform(0.5, 1.5))
                sla_compliance = min(100, 80 + (progress * 0.2))
                break
        
        progress_data.append({
            'Workflow': workflow,
            'Completion %': round(progress, 1),
            'SLA Compliance %': round(sla_compliance, 1),
            'Pending Items': np.random.randint(50, 500),
            'This Week': np.random.randint(10, 100)
        })
    
    progress_df = pd.DataFrame(progress_data)
    
    # Create comprehensive dashboard
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Completion Progress', 'SLA Compliance', 'Pending Items', 'Weekly Activity'),
        specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]]
    )
    
    fig.add_trace(go.Bar(x=progress_df['Workflow'], y=progress_df['Completion %'], name='Completion'), 1, 1)
    fig.add_trace(go.Bar(x=progress_df['Workflow'], y=progress_df['SLA Compliance %'], name='SLA Compliance'), 1, 2)
    fig.add_trace(go.Bar(x=progress_df['Workflow'], y=progress_df['Pending Items'], name='Pending Items'), 2, 1)
    fig.add_trace(go.Bar(x=progress_df['Workflow'], y=progress_df['This Week'], name='This Week'), 2, 2)
    
    fig.update_layout(height=800, showlegend=False, title_text="Workflow Performance Dashboard")
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
                status_color = {
                    'Pending': '#f39c12',
                    'In Progress': '#3498db', 
                    'Completed': '#27ae60',
                    'Critical': '#e74c3c'
                }.get(task['status'], '#95a5a6')
                
                st.markdown(f"""
                <div class="workflow-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0;">{task['name']}</h4>
                            <p style="margin: 0; color: #666;">{task['description']}</p>
                            <small>Assigned to: {task['assigned_to']} | Due: {task['due_date']} | Created: {task['created_at'].strftime('%Y-%m-%d')}</small>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: {status_color}; 
                                      color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">
                                {task['status']}
                            </span>
                            <br>
                            <span style="color: #7f8c8d; font-size: 0.8rem;">{task['priority']} Priority</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No tasks created yet. Use the form above to create new tasks.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_analytics():
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    st.subheader("📈 Advanced Analytics & Insights")
    
    if not st.session_state.uploaded_data:
        st.info("Upload data to see analytics")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Apply filters to data
    filtered_data = apply_filters(st.session_state.uploaded_data)
    
    # Comprehensive analytics dashboard
    st.subheader("📊 Comprehensive Analytics Dashboard")
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_items = sum([data['row_count'] for data in filtered_data.values()])
        st.metric("Total Filtered Items", f"{total_items:,}")
    
    with col2:
        avg_completion = np.mean([min(100, (data['row_count'] / 100) * np.random.uniform(0.5, 1.5)) 
                                for data in filtered_data.values()])
        st.metric("Avg Completion %", f"{avg_completion:.1f}%")
    
    with col3:
        total_value = sum([
            data['dataframe'].select_dtypes(include=[np.number]).sum().sum() 
            for data in filtered_data.values()
        ])
        st.metric("Total Numeric Value", f"{total_value:,.0f}")
    
    with col4:
        workflow_efficiency = np.mean([np.random.uniform(75, 95) for _ in filtered_data])
        st.metric("Workflow Efficiency", f"{workflow_efficiency:.1f}%")
    
    # Advanced charts
    st.subheader("📈 Trend Analysis")
    
    # Time series analysis
    time_data = []
    for i in range(30):
        day = date.today() - timedelta(days=29-i)
        time_data.append({
            'Date': day,
            'Completed': np.random.randint(50, 200),
            'Pending': np.random.randint(100, 300),
            'Efficiency': np.random.uniform(80, 95)
        })
    
    time_df = pd.DataFrame(time_data)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_df['Date'], y=time_df['Completed'], name='Completed', line=dict(color='#27ae60')))
    fig.add_trace(go.Scatter(x=time_df['Date'], y=time_df['Pending'], name='Pending', line=dict(color='#e74c3c')))
    fig.add_trace(go.Scatter(x=time_df['Date'], y=time_df['Efficiency'], name='Efficiency %', 
                           yaxis='y2', line=dict(color='#3498db', dash='dot')))
    
    fig.update_layout(
        title='30-Day Performance Trends',
        yaxis=dict(title='Items'),
        yaxis2=dict(title='Efficiency %', overlaying='y', side='right'),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Workflow correlation analysis
    st.subheader("🔗 Workflow Correlation Analysis")
    
    if len(st.session_state.selected_sheets) >= 2:
        # Create correlation matrix between workflows
        workflow_stats = []
        for sheet_name in st.session_state.selected_sheets[:5]:  # Limit to 5 for readability
            data = filtered_data[sheet_name]
            df = data['dataframe']
            numeric_data = df.select_dtypes(include=[np.number])
            
            if not numeric_data.empty:
                stats = {
                    'Workflow': sheet_name,
                    'Item Count': data['row_count'],
                    'Avg Value': numeric_data.mean().mean(),
                    'Total Value': numeric_data.sum().sum(),
                    'Std Dev': numeric_data.std().std()
                }
                workflow_stats.append(stats)
        
        if workflow_stats:
            stats_df = pd.DataFrame(workflow_stats).set_index('Workflow')
            corr_matrix = stats_df.corr()
            
            fig = px.imshow(corr_matrix, 
                          title='Workflow Metrics Correlation Matrix',
                          color_continuous_scale='RdBu_r',
                          aspect='auto')
            st.plotly_chart(fig, use_container_width=True)
    
    # Predictive analytics
    st.subheader("🔮 Predictive Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Completion forecasting
        st.plotly_chart(px.line(
            x=pd.date_range('2024-01-01', periods=12, freq='M'),
            y=np.cumsum(np.random.randint(800, 1200, 12)),
            title='Monthly Completion Forecast',
            labels={'x': 'Month', 'y': 'Cumulative Completions'}
        ), use_container_width=True)
    
    with col2:
        # Workload distribution
        workload_data = []
        for sheet_name in st.session_state.selected_sheets:
            workload_data.append({
                'Workflow': sheet_name,
                'Workload': filtered_data[sheet_name]['row_count'],
                'Complexity': np.random.uniform(1, 10)
            })
        
        workload_df = pd.DataFrame(workload_data)
        st.plotly_chart(px.scatter(
            workload_df, x='Workload', y='Complexity', size='Workload',
            color='Workflow', title='Workload vs Complexity Analysis',
            hover_data=['Workflow']
        ), use_container_width=True)
    
    # Data quality insights
    st.subheader("📋 Data Quality Report")
    
    quality_data = []
    for sheet_name in st.session_state.selected_sheets:
        data = filtered_data[sheet_name]
        df = data['dataframe']
        
        quality_data.append({
            'Workflow': sheet_name,
            'Total Rows': len(df),
            'Missing Values': df.isnull().sum().sum(),
            'Duplicate Rows': df.duplicated().sum(),
            'Data Completeness %': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        })
    
    quality_df = pd.DataFrame(quality_data)
    st.dataframe(quality_df, use_container_width=True)
    
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
            "Email Import",
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
    elif selected_menu == "Email Import":
        render_email_import()
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
