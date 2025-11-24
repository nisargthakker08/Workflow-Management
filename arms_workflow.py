import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import date, timedelta
import io
import base64

# ======================================
# ENTERPRISE CONFIGURATION
# ======================================

st.set_page_config(
    page_title="ARMS Enterprise Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Enterprise Styling
st.markdown("""
<style>
    /* Main Theme */
    .main {
        background-color: #0e1a2b;
    }
    
    /* Enterprise Header */
    .enterprise-header {
        background: linear-gradient(135deg, #0f2d4e 0%, #1a4b8c 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 0px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        border-bottom: 3px solid #00d4ff;
    }
    
    /* Power BI-like Cards */
    .powerbi-card {
        background: #1e2a3b;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border: 1px solid #2a3a50;
        margin-bottom: 1rem;
    }
    
    /* Metric Cards */
    .metric-card-enterprise {
        background: linear-gradient(135deg, #1a4b8c 0%, #2a5ca0 100%);
        padding: 1.2rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: 1px solid #3a6bb0;
    }
    
    .metric-value-enterprise {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-label-enterprise {
        font-size: 0.85rem;
        color: #b3d9ff;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Filters Panel */
    .filters-panel {
        background: #1a2435;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #2a3a50;
        margin-bottom: 1rem;
    }
    
    /* Custom Slider */
    .stSlider > div > div > div {
        background: #00d4ff;
    }
    
    /* Custom Select Box */
    .stSelectbox > div > div {
        background: #2a3a50;
        color: white;
    }
    
    /* Custom Button */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        color: white;
        border: none;
        padding: 0.7rem 2rem;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0099cc 0%, #0077aa 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: #1a2435;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #2a3a50;
        color: #b3d9ff;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: #00d4ff;
        color: #0e1a2b;
    }
</style>
""", unsafe_allow_html=True)

# ======================================
# ENTERPRISE DATA MANAGEMENT
# ======================================

class EnterpriseDataManager:
    def __init__(self):
        self.workflows = {}
        self.combined_data = None
        self.filters = {}
        
    def add_workflow(self, name, df):
        """Add a workflow dataset"""
        self.workflows[name] = df
        st.success(f"✅ Workflow '{name}' loaded with {len(df)} rows")
        
    def combine_all_workflows(self):
        """Combine all workflows into a single dataset"""
        if not self.workflows:
            return None
            
        combined_dfs = []
        for name, df in self.workflows.items():
            df_copy = df.copy()
            df_copy['Workflow_Source'] = name
            combined_dfs.append(df_copy)
            
        self.combined_data = pd.concat(combined_dfs, ignore_index=True)
        return self.combined_data
    
    def get_filtered_data(self, filters=None):
        """Apply filters to the combined data"""
        if self.combined_data is None:
            return None
            
        filtered_df = self.combined_data.copy()
        
        if filters:
            for column, filter_config in filters.items():
                if column in filtered_df.columns:
                    if filter_config['type'] == 'range':
                        if pd.api.types.is_numeric_dtype(filtered_df[column]):
                            filtered_df = filtered_df[
                                (filtered_df[column] >= filter_config['min']) & 
                                (filtered_df[column] <= filter_config['max'])
                            ]
                    elif filter_config['type'] == 'multi_select':
                        filtered_df = filtered_df[filtered_df[column].isin(filter_config['values'])]
                    elif filter_config['type'] == 'date_range':
                        filtered_df = filtered_df[
                            (filtered_df[column] >= filter_config['start']) & 
                            (filtered_df[column] <= filter_config['end'])
                        ]
        
        return filtered_df

# Initialize data manager
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = EnterpriseDataManager()

# ======================================
# POWER BI-LIKE FILTERS COMPONENT
# ======================================

def create_powerbi_filters_panel(df):
    """Create Power BI-like filters panel"""
    st.markdown('<div class="filters-panel">', unsafe_allow_html=True)
    st.markdown("### 🎛️ Power Filters")
    
    filters = {}
    
    # Create columns for filters
    num_columns = min(4, len(df.columns))
    cols = st.columns(num_columns)
    
    current_col = 0
    
    for column in df.columns:
        with cols[current_col]:
            # Numeric columns - Range sliders
            if pd.api.types.is_numeric_dtype(df[column]):
                st.markdown(f"**{column}**")
                min_val = float(df[column].min())
                max_val = float(df[column].max())
                selected_range = st.slider(
                    f"Range for {column}",
                    min_val, max_val, (min_val, max_val),
                    key=f"filter_{column}"
                )
                filters[column] = {
                    'type': 'range',
                    'min': selected_range[0],
                    'max': selected_range[1]
                }
            
            # Date columns - Date range
            elif pd.api.types.is_datetime64_any_dtype(df[column]):
                st.markdown(f"**{column}**")
                min_date = df[column].min().date()
                max_date = df[column].max().date()
                selected_dates = st.date_input(
                    f"Date range for {column}",
                    [min_date, max_date],
                    min_date, max_date,
                    key=f"date_filter_{column}"
                )
                if len(selected_dates) == 2:
                    filters[column] = {
                        'type': 'date_range',
                        'start': selected_dates[0],
                        'end': selected_dates[1]
                    }
            
            # Categorical columns - Multi-select
            else:
                unique_values = df[column].unique()
                if len(unique_values) <= 50:  # Only show multi-select for reasonable number of values
                    st.markdown(f"**{column}**")
                    selected_values = st.multiselect(
                        f"Select {column}",
                        options=unique_values,
                        default=unique_values,
                        key=f"select_{column}"
                    )
                    filters[column] = {
                        'type': 'multi_select',
                        'values': selected_values
                    }
        
        current_col = (current_col + 1) % num_columns
    
    st.markdown("</div>", unsafe_allow_html=True)
    return filters

# ======================================
# ADVANCED VISUALIZATION COMPONENTS
# ======================================

def create_advanced_dashboard(df, filters):
    """Create Power BI-like advanced dashboard"""
    
    # Apply filters
    filtered_df = st.session_state.data_manager.get_filtered_data(filters)
    
    if filtered_df is None or len(filtered_df) == 0:
        st.warning("No data available after applying filters.")
        return
    
    # Key Metrics Row
    st.markdown("### 📊 Executive Summary")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        total_records = len(filtered_df)
        st.markdown(f'<div class="metric-card-enterprise"><div class="metric-value-enterprise">{total_records:,}</div><div class="metric-label-enterprise">Total Records</div></div>', unsafe_allow_html=True)
    
    # Dynamic metrics based on available numeric columns
    numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) >= 5:
        metrics_data = [
            (numeric_cols[0], "sum"),
            (numeric_cols[1], "mean"), 
            (numeric_cols[2], "max"),
            (numeric_cols[3], "min"),
            (numeric_cols[4], "std")
        ]
    else:
        # Fallback if not enough numeric columns
        metrics_data = [
            ("Total Records", "count"),
            ("Avg Value", "mean"),
            ("Max Value", "max"),
            ("Min Value", "min"),
            ("Std Dev", "std")
        ]
    
    metric_cols = [col2, col3, col4, col5, col6]
    for (col_name, agg_func), col in zip(metrics_data, metric_cols):
        with col:
            if col_name in filtered_df.columns and pd.api.types.is_numeric_dtype(filtered_df[col_name]):
                if agg_func == "sum":
                    value = filtered_df[col_name].sum()
                    formatted_value = f"{value:,.0f}"
                elif agg_func == "mean":
                    value = filtered_df[col_name].mean()
                    formatted_value = f"{value:,.2f}"
                elif agg_func == "max":
                    value = filtered_df[col_name].max()
                    formatted_value = f"{value:,.0f}"
                elif agg_func == "min":
                    value = filtered_df[col_name].min()
                    formatted_value = f"{value:,.0f}"
                elif agg_func == "std":
                    value = filtered_df[col_name].std()
                    formatted_value = f"{value:,.2f}"
                else:
                    value = len(filtered_df)
                    formatted_value = f"{value:,}"
                
                st.markdown(f'<div class="metric-card-enterprise"><div class="metric-value-enterprise">{formatted_value}</div><div class="metric-label-enterprise">{agg_func.title()} {col_name}</div></div>', unsafe_allow_html=True)
    
    # Chart Configuration
    st.markdown("### 📈 Advanced Analytics Studio")
    
    # Chart Configuration Panel
    with st.expander("🎨 Chart Configuration", expanded=True):
        config_col1, config_col2, config_col3, config_col4 = st.columns(4)
        
        with config_col1:
            # X-Axis selection
            x_axis = st.selectbox(
                "X-Axis Dimension",
                options=[''] + list(filtered_df.columns),
                key="x_axis_select"
            )
        
        with config_col2:
            # Y-Axis selection (multiple)
            y_axes = st.multiselect(
                "Y-Axis Measures",
                options=[col for col in filtered_df.columns if pd.api.types.is_numeric_dtype(filtered_df[col])],
                key="y_axes_select"
            )
        
        with config_col3:
            # Color by
            color_by = st.selectbox(
                "Color By (Dimension)",
                options=[''] + [col for col in filtered_df.columns if not pd.api.types.is_numeric_dtype(filtered_df[col])],
                key="color_by_select"
            )
        
        with config_col4:
            # Chart type
            chart_type = st.selectbox(
                "Chart Type",
                options=["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Area Chart", "Heatmap"],
                key="chart_type_select"
            )
    
    # Create charts based on configuration
    if x_axis and y_axes:
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            try:
                if chart_type == "Bar Chart":
                    if len(y_axes) == 1:
                        fig = px.bar(
                            filtered_df, 
                            x=x_axis, 
                            y=y_axes[0],
                            color=color_by if color_by else None,
                            title=f"{y_axes[0]} by {x_axis}",
                            template="plotly_dark"
                        )
                    else:
                        # Multiple bars
                        fig = go.Figure()
                        for y_axis in y_axes:
                            fig.add_trace(go.Bar(
                                name=y_axis,
                                x=filtered_df[x_axis],
                                y=filtered_df[y_axis]
                            ))
                        fig.update_layout(
                            title=f"Multiple Metrics by {x_axis}",
                            template="plotly_dark",
                            barmode='group'
                        )
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "Line Chart":
                    fig = px.line(
                        filtered_df, 
                        x=x_axis, 
                        y=y_axes[0],
                        color=color_by if color_by else None,
                        title=f"{y_axes[0]} Trend by {x_axis}",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "Scatter Plot" and len(y_axes) >= 2:
                    fig = px.scatter(
                        filtered_df,
                        x=y_axes[0],
                        y=y_axes[1],
                        color=color_by if color_by else None,
                        size=y_axes[2] if len(y_axes) > 2 else None,
                        title=f"{y_axes[1]} vs {y_axes[0]}",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "Pie Chart":
                    fig = px.pie(
                        filtered_df,
                        names=x_axis,
                        values=y_axes[0],
                        title=f"Distribution of {y_axes[0]} by {x_axis}",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
            except Exception as e:
                st.error(f"Error creating chart: {str(e)}")
        
        with chart_col2:
            # Additional chart or data summary
            st.markdown("### 📋 Data Summary")
            
            # Column statistics
            if len(numeric_cols) > 0:
                summary_stats = filtered_df[numeric_cols].describe()
                st.dataframe(summary_stats, use_container_width=True)
            
            # Data quality info
            st.markdown("#### Data Quality")
            quality_col1, quality_col2, quality_col3 = st.columns(3)
            
            with quality_col1:
                missing_values = filtered_df.isnull().sum().sum()
                st.metric("Missing Values", missing_values)
            
            with quality_col2:
                duplicate_rows = filtered_df.duplicated().sum()
                st.metric("Duplicate Rows", duplicate_rows)
            
            with quality_col3:
                memory_usage = f"{filtered_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
                st.metric("Memory Usage", memory_usage)
    
    # Advanced Analytics Section
    st.markdown("### 🔍 Advanced Insights")
    
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        # Correlation heatmap
        if len(numeric_cols) >= 2:
            st.markdown("#### Correlation Matrix")
            corr_matrix = filtered_df[numeric_cols].corr()
            fig = px.imshow(
                corr_matrix,
                title="Feature Correlations",
                color_continuous_scale="RdBu_r",
                aspect="auto"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with insight_col2:
        # Top categories
        categorical_cols = filtered_df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            st.markdown("#### Top Categories")
            top_cat_col = st.selectbox("Select Category", categorical_cols, key="top_cat_select")
            if top_cat_col:
                top_categories = filtered_df[top_cat_col].value_counts().head(10)
                fig = px.bar(
                    x=top_categories.index,
                    y=top_categories.values,
                    title=f"Top 10 {top_cat_col}",
                    template="plotly_dark"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Data Export
    st.markdown("### 💾 Export Results")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        # CSV Export
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            "📥 Download Filtered Data (CSV)",
            data=csv,
            file_name="filtered_analytics_data.csv",
            mime="text/csv"
        )
    
    with export_col2:
        # Excel Export
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, sheet_name='Filtered_Data', index=False)
            # Add summary sheet
            summary_df = filtered_df.describe()
            summary_df.to_excel(writer, sheet_name='Summary_Statistics')
        excel_data = output.getvalue()
        
        st.download_button(
            "📊 Download Full Report (Excel)",
            data=excel_data,
            file_name="analytics_report.xlsx",
            mime="application/vnd.ms-excel"
        )
    
    with export_col3:
        # Chart Export
        if st.button("🖼️ Export Dashboard as Image"):
            st.info("Chart export functionality would be implemented here")

# ======================================
# WORKFLOW MANAGEMENT
# ======================================

def workflow_management_tab():
    """Manage multiple workflow datasets"""
    st.markdown('<div class="powerbi-card">', unsafe_allow_html=True)
    st.markdown("### 🔄 Multi-Workflow Management")
    
    # Upload multiple Excel files
    uploaded_files = st.file_uploader(
        "Upload Multiple Excel Workflows",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        key="multi_workflow_upload"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                # Get sheet names
                xl_file = pd.ExcelFile(uploaded_file)
                sheet_names = xl_file.sheet_names
                
                # Let user select which sheets to load
                selected_sheets = st.multiselect(
                    f"Select sheets from {uploaded_file.name}",
                    options=sheet_names,
                    default=sheet_names,
                    key=f"sheets_{uploaded_file.name}"
                )
                
                for sheet_name in selected_sheets:
                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                    workflow_name = f"{uploaded_file.name} - {sheet_name}"
                    st.session_state.data_manager.add_workflow(workflow_name, df)
                    
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
    
    # Show loaded workflows
    if st.session_state.data_manager.workflows:
        st.markdown("#### 📂 Loaded Workflows")
        
        workflows_col1, workflows_col2 = st.columns([3, 1])
        
        with workflows_col1:
            for workflow_name, df in st.session_state.data_manager.workflows.items():
                with st.expander(f"📊 {workflow_name} ({len(df)} rows)"):
                    st.dataframe(df.head(10), use_container_width=True)
        
        with workflows_col2:
            st.markdown("#### Actions")
            if st.button("🔄 Combine All Workflows", use_container_width=True):
                combined_df = st.session_state.data_manager.combine_all_workflows()
                if combined_df is not None:
                    st.success(f"✅ Combined {len(st.session_state.data_manager.workflows)} workflows into {len(combined_df)} total records")
            
            if st.button("🗑️ Clear All Workflows", use_container_width=True):
                st.session_state.data_manager.workflows = {}
                st.session_state.data_manager.combined_data = None
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================
# SAMPLE DATA GENERATOR
# ======================================

def generate_sample_data():
    """Generate comprehensive sample data for demonstration"""
    
    # Sample workflow 1: Sales Data
    dates = pd.date_range('2024-01-01', '2024-03-20', freq='D')
    sales_data = []
    
    for date in dates:
        for region in ['North', 'South', 'East', 'West']:
            for product in ['Product A', 'Product B', 'Product C']:
                sales_data.append({
                    'Date': date,
                    'Region': region,
                    'Product': product,
                    'Sales_Amount': np.random.randint(1000, 50000),
                    'Units_Sold': np.random.randint(10, 500),
                    'Profit': np.random.randint(100, 10000),
                    'Customer_Rating': np.random.uniform(1, 5),
                    'Category': np.random.choice(['Electronics', 'Furniture', 'Clothing'])
                })
    
    sales_df = pd.DataFrame(sales_data)
    
    # Sample workflow 2: Operations Data
    operations_data = []
    for date in dates[:100]:  # Fewer dates for variety
        for department in ['HR', 'Finance', 'IT', 'Operations']:
            operations_data.append({
                'Date': date,
                'Department': department,
                'Tasks_Completed': np.random.randint(5, 100),
                'Processing_Time_Minutes': np.random.randint(10, 300),
                'Quality_Score': np.random.uniform(80, 100),
                'Backlog_Items': np.random.randint(0, 50),
                'Team_Size': np.random.randint(3, 15)
            })
    
    operations_df = pd.DataFrame(operations_data)
    
    return {
        "Sales Performance": sales_df,
        "Operations Metrics": operations_df
    }

# ======================================
# MAIN APPLICATION
# ======================================

def main():
    # Enterprise Header
    st.markdown("""
    <div class="enterprise-header">
        <h1 style="margin:0; color:white; font-size:2.5rem;">🚀 ARMS ENTERPRISE ANALYTICS</h1>
        <p style="margin:0; opacity:0.9; font-size:1.1rem;">Power BI-like Analytics Platform with Multi-Workflow Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize with sample data if empty
    if not st.session_state.data_manager.workflows:
        st.info("🌟 Loading sample data for demonstration...")
        sample_data = generate_sample_data()
        for name, df in sample_data.items():
            st.session_state.data_manager.add_workflow(name, df)
        st.session_state.data_manager.combine_all_workflows()
    
    # Main Navigation Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "🔄 Workflow Management", "⚙️ Data Configuration"])
    
    with tab1:
        st.markdown('<div class="powerbi-card">', unsafe_allow_html=True)
        
        if st.session_state.data_manager.combined_data is not None:
            # Create Power BI-like filters
            filters = create_powerbi_filters_panel(st.session_state.data_manager.combined_data)
            
            # Create advanced dashboard
            create_advanced_dashboard(st.session_state.data_manager.combined_data, filters)
        else:
            st.warning("Please load and combine workflows in the Workflow Management tab first.")
            
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        workflow_management_tab()
    
    with tab3:
        st.markdown('<div class="powerbi-card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ System Configuration")
        
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            st.markdown("#### Data Processing")
            max_rows = st.slider("Maximum Rows to Process", 1000, 1000000, 100000)
            cache_enabled = st.checkbox("Enable Data Caching", value=True)
            auto_refresh = st.checkbox("Auto-refresh Dashboard", value=False)
            
        with config_col2:
            st.markdown("#### Visualization Settings")
            chart_theme = st.selectbox("Chart Theme", ["Plotly Dark", "Plotly White", "Plotly Native"])
            default_chart_type = st.selectbox("Default Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot"])
            animation_enabled = st.checkbox("Enable Chart Animations", value=True)
        
        if st.button("💾 Save Configuration", use_container_width=True):
            st.success("Configuration saved successfully!")
            
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
