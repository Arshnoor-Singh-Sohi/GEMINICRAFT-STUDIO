import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import io
from datetime import datetime
from typing import List, Dict, Optional, Any

# Import database utilities
try:
    from utils.database import track_tool_usage
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class DataAnalyst:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro")
    
    def analyze_dataset(self, df: pd.DataFrame, analysis_type: str) -> str:
        """Analyze dataset with AI insights"""
        
        # Prepare dataset summary
        summary = self._get_dataset_summary(df)
        
        prompts = {
            "Overview": f"""
            Analyze this dataset and provide a comprehensive overview:
            
            {summary}
            
            Please provide:
            1. Dataset description and structure analysis
            2. Data quality assessment
            3. Key patterns and trends observed
            4. Potential insights and findings
            5. Recommendations for further analysis
            """,
            
            "Statistical Analysis": f"""
            Perform statistical analysis on this dataset:
            
            {summary}
            
            Please provide:
            1. Descriptive statistics interpretation
            2. Distribution analysis
            3. Correlation insights
            4. Outlier detection
            5. Statistical significance tests suggestions
            """,
            
            "Business Insights": f"""
            Generate business insights from this dataset:
            
            {summary}
            
            Please provide:
            1. Key business metrics and KPIs
            2. Performance indicators
            3. Growth opportunities
            4. Risk factors
            5. Actionable recommendations
            """,
            
            "Trend Analysis": f"""
            Analyze trends in this dataset:
            
            {summary}
            
            Please provide:
            1. Time-based trends (if applicable)
            2. Seasonal patterns
            3. Growth/decline analysis
            4. Forecasting insights
            5. Trend implications
            """,
            
            "Data Quality": f"""
            Assess data quality for this dataset:
            
            {summary}
            
            Please provide:
            1. Completeness analysis
            2. Accuracy assessment
            3. Consistency evaluation
            4. Data cleaning recommendations
            5. Quality improvement suggestions
            """
        }
        
        prompt = prompts.get(analysis_type, prompts["Overview"])
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error analyzing dataset: {str(e)}"
    
    def suggest_visualizations(self, df: pd.DataFrame) -> str:
        """Suggest appropriate visualizations for the dataset"""
        
        summary = self._get_dataset_summary(df)
        
        prompt = f"""
        Based on this dataset structure, suggest the most appropriate data visualizations:
        
        {summary}
        
        For each suggestion, provide:
        1. Chart type (bar, line, scatter, heatmap, etc.)
        2. Variables to use (x-axis, y-axis, color, size)
        3. Purpose and insights it would reveal
        4. Target audience suitability
        
        Prioritize visualizations that would be most insightful for this data.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error suggesting visualizations: {str(e)}"
    
    def generate_report(self, df: pd.DataFrame, report_type: str) -> str:
        """Generate comprehensive data report"""
        
        summary = self._get_dataset_summary(df)
        
        report_prompts = {
            "Executive Summary": f"""
            Create an executive summary report for this dataset:
            
            {summary}
            
            Include:
            - Key findings summary
            - Critical metrics
            - Strategic recommendations
            - Next steps
            - Executive-level insights
            """,
            
            "Technical Report": f"""
            Create a technical data analysis report:
            
            {summary}
            
            Include:
            - Methodology explanation
            - Statistical analysis details
            - Data processing steps
            - Technical findings
            - Limitations and assumptions
            """,
            
            "Business Report": f"""
            Create a business-focused report:
            
            {summary}
            
            Include:
            - Business impact analysis
            - Performance metrics
            - Market insights
            - ROI implications
            - Strategic recommendations
            """
        }
        
        prompt = report_prompts.get(report_type, report_prompts["Executive Summary"])
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def _get_dataset_summary(self, df: pd.DataFrame) -> str:
        """Generate comprehensive dataset summary"""
        
        summary = f"""
        Dataset Summary:
        - Shape: {df.shape[0]} rows, {df.shape[1]} columns
        - Columns: {list(df.columns)}
        - Data types: {dict(df.dtypes)}
        - Missing values: {dict(df.isnull().sum())}
        
        Sample data (first 5 rows):
        {df.head().to_string()}
        
        Descriptive statistics:
        {df.describe().to_string() if len(df.select_dtypes(include='number').columns) > 0 else 'No numerical columns for statistics'}
        
        Unique values per column:
        {dict(df.nunique())}
        """
        
        return summary

def create_visualization(df: pd.DataFrame, chart_type: str, x_col: str, y_col: str = None, color_col: str = None):
    """Create visualizations based on parameters"""
    
    try:
        if chart_type == "Bar Chart":
            if y_col:
                fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} by {x_col}")
            else:
                value_counts = df[x_col].value_counts()
                fig = px.bar(x=value_counts.index, y=value_counts.values, title=f"Distribution of {x_col}")
        
        elif chart_type == "Line Chart":
            fig = px.line(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} over {x_col}")
        
        elif chart_type == "Scatter Plot":
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} vs {x_col}")
        
        elif chart_type == "Histogram":
            fig = px.histogram(df, x=x_col, color=color_col, title=f"Distribution of {x_col}")
        
        elif chart_type == "Box Plot":
            fig = px.box(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} distribution by {x_col}")
        
        elif chart_type == "Correlation Heatmap":
            numeric_df = df.select_dtypes(include='number')
            if len(numeric_df.columns) > 1:
                corr_matrix = numeric_df.corr()
                fig = px.imshow(corr_matrix, title="Correlation Heatmap", aspect="auto")
            else:
                return None
        
        else:
            return None
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating visualization: {e}")
        return None

def load_data_analyst_page():
    st.markdown("# 📊 Data Analyst")
    st.markdown("*AI-powered data analysis and visualization platform*")
    
    # Initialize session state
    if "data_analyst" not in st.session_state:
        st.session_state.data_analyst = DataAnalyst()
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    if "current_dataset" not in st.session_state:
        st.session_state.current_dataset = None
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### 🎛️ Analysis Controls")
        
        # Analysis type
        analysis_type = st.selectbox(
            "🔍 Analysis Type:",
            [
                "Overview",
                "Statistical Analysis", 
                "Business Insights",
                "Trend Analysis",
                "Data Quality",
                "Visualization Suggestions"
            ]
        )
        
        # Report type
        report_type = st.selectbox(
            "📋 Report Type:",
            ["Executive Summary", "Technical Report", "Business Report"]
        )
        
        st.markdown("---")
        
        # Sample datasets
        st.markdown("### 📂 Sample Datasets")
        if st.button("📈 Sales Data", use_container_width=True):
            # Generate sample sales data
            sample_data = {
                'Date': pd.date_range('2023-01-01', periods=100, freq='D'),
                'Sales': [100 + i*2 + (i%10)*5 for i in range(100)],
                'Region': ['North', 'South', 'East', 'West'] * 25,
                'Product': ['A', 'B', 'C'] * 33 + ['A'],
                'Revenue': [s * 1.2 for s in [100 + i*2 + (i%10)*5 for i in range(100)]]
            }
            st.session_state.current_dataset = pd.DataFrame(sample_data)
            st.success("Sample sales data loaded!")
        
        if st.button("👥 Customer Data", use_container_width=True):
            # Generate sample customer data
            sample_data = {
                'Customer_ID': range(1, 151),
                'Age': [25 + (i%40) for i in range(150)],
                'Gender': ['Male', 'Female'] * 75,
                'City': ['NYC', 'LA', 'Chicago', 'Houston', 'Phoenix'] * 30,
                'Purchase_Amount': [50 + (i%200) for i in range(150)],
                'Satisfaction': [1 + (i%5) for i in range(150)]
            }
            st.session_state.current_dataset = pd.DataFrame(sample_data)
            st.success("Sample customer data loaded!")
        
        st.markdown("---")
        
        # History management
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.analysis_history = []
            st.rerun()
        
        if st.session_state.analysis_history:
            if st.button("💾 Export History", use_container_width=True):
                history_data = {
                    "timestamp": datetime.now().isoformat(),
                    "analyses": st.session_state.analysis_history
                }
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(history_data, indent=2),
                    file_name=f"analysis_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📂 Data Input")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload your dataset",
            type=["csv", "xlsx", "json"],
            help="Supported formats: CSV, Excel, JSON"
        )
        
        if uploaded_file:
            try:
                # Load dataset based on file type
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.json'):
                    df = pd.read_json(uploaded_file)
                
                st.session_state.current_dataset = df
                st.success(f"Dataset loaded! Shape: {df.shape}")
                
            except Exception as e:
                st.error(f"Error loading file: {e}")
        
        # Display current dataset info
        if st.session_state.current_dataset is not None:
            df = st.session_state.current_dataset
            
            st.markdown("### 📋 Dataset Overview")
            st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
            st.write(f"**Columns:** {', '.join(df.columns)}")
            
            # Show data preview
            st.markdown("**Data Preview:**")
            st.dataframe(df.head(), use_container_width=True)
            
            # Basic statistics
            if len(df.select_dtypes(include='number').columns) > 0:
                with st.expander("📊 Basic Statistics"):
                    st.dataframe(df.describe(), use_container_width=True)
            
            # Data types and missing values
            with st.expander("🔍 Data Info"):
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.write("**Data Types:**")
                    st.write(df.dtypes)
                with col_info2:
                    st.write("**Missing Values:**")
                    st.write(df.isnull().sum())
    
    with col2:
        st.markdown("### 🧠 AI Analysis")
        
        if st.session_state.current_dataset is not None:
            df = st.session_state.current_dataset
            
            # Analysis button
            if st.button("🚀 Analyze Dataset", type="primary", use_container_width=True):
                # Track usage
                if DB_AVAILABLE:
                    track_tool_usage("data_analyst", f"analysis_{analysis_type.lower().replace(' ', '_')}")
                
                with st.spinner(f"🔍 Performing {analysis_type}..."):
                    
                    if analysis_type == "Visualization Suggestions":
                        result = st.session_state.data_analyst.suggest_visualizations(df)
                    else:
                        result = st.session_state.data_analyst.analyze_dataset(df, analysis_type)
                    
                    st.session_state.current_analysis = result
                    
                    # Save to history
                    history_record = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "analysis_type": analysis_type,
                        "dataset_shape": df.shape,
                        "columns": list(df.columns),
                        "result": result
                    }
                    st.session_state.analysis_history.append(history_record)
                    
                    st.rerun()
            
            # Generate report button
            if st.button("📋 Generate Report", use_container_width=True):
                with st.spinner(f"📝 Generating {report_type}..."):
                    report = st.session_state.data_analyst.generate_report(df, report_type)
                    st.session_state.current_report = report
                    st.rerun()
            
            # Display analysis results
            if "current_analysis" in st.session_state:
                st.markdown("**🎯 Analysis Results:**")
                st.write(st.session_state.current_analysis)
                
                # Action buttons
                col_copy, col_save = st.columns(2)
                with col_copy:
                    if st.button("📋 Copy Analysis"):
                        st.success("Analysis copied!")
                
                with col_save:
                    st.download_button(
                        label="💾 Save Analysis",
                        data=st.session_state.current_analysis,
                        file_name=f"data_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
            
            # Display report
            if "current_report" in st.session_state:
                st.markdown("---")
                st.markdown("**📋 Generated Report:**")
                st.write(st.session_state.current_report)
                
                st.download_button(
                    label="💾 Save Report",
                    data=st.session_state.current_report,
                    file_name=f"data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
        
        else:
            st.info("👈 Upload a dataset or select a sample to begin analysis")
            
            # Analysis capabilities
            st.markdown("**🎯 Analysis Capabilities:**")
            capabilities = [
                "📈 **Statistical Analysis:** Descriptive stats, correlations, distributions",
                "💼 **Business Insights:** KPIs, performance metrics, recommendations", 
                "📊 **Trend Analysis:** Time-series patterns, forecasting insights",
                "🔍 **Data Quality:** Completeness, accuracy, cleaning suggestions",
                "📋 **Report Generation:** Executive, technical, and business reports",
                "📉 **Visualization Suggestions:** Chart recommendations for your data"
            ]
            for capability in capabilities:
                st.markdown(f"• {capability}")
    
    # Data Visualization Section
    if st.session_state.current_dataset is not None:
        st.markdown("---")
        st.markdown("## 📊 Data Visualization")
        
        df = st.session_state.current_dataset
        
        viz_col1, viz_col2, viz_col3 = st.columns([1, 1, 1])
        
        with viz_col1:
            chart_type = st.selectbox(
                "📈 Chart Type:",
                ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram", "Box Plot", "Correlation Heatmap"]
            )
        
        with viz_col2:
            x_column = st.selectbox(
                "📊 X-axis:",
                df.columns,
                index=0
            )
        
        with viz_col3:
            y_columns = [None] + list(df.columns)
            y_column = st.selectbox(
                "📈 Y-axis:",
                y_columns,
                index=1 if len(y_columns) > 1 else 0
            )
        
        # Color column (optional)
        color_columns = [None] + list(df.select_dtypes(include=['object', 'category']).columns)
        color_column = st.selectbox(
            "🎨 Color by (optional):",
            color_columns
        )
        
        # Create visualization
        if st.button("📊 Create Visualization", use_container_width=True):
            # Track usage
            if DB_AVAILABLE:
                track_tool_usage("data_analyst", f"visualization_{chart_type.lower().replace(' ', '_')}")
            
            fig = create_visualization(df, chart_type, x_column, y_column, color_column)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                # Save chart
                chart_html = fig.to_html()
                st.download_button(
                    label="💾 Save Chart",
                    data=chart_html,
                    file_name=f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
            else:
                st.error("Could not create visualization with the selected parameters.")
    
    # Analysis History
    if st.session_state.analysis_history:
        st.markdown("---")
        st.markdown("## 📚 Analysis History")
        
        for i, record in enumerate(reversed(st.session_state.analysis_history[-5:])):  # Show last 5
            with st.expander(f"📊 {record['analysis_type']} - {record['timestamp']}"):
                # Safe access to dataset_shape
                if 'dataset_shape' in record:
                    st.markdown(f"**Dataset:** {record['dataset_shape'][0]} rows × {record['dataset_shape'][1]} columns")
                if 'columns' in record:
                    st.markdown(f"**Columns:** {', '.join(record['columns'])}")
                st.markdown(f"**Analysis:**")
                st.write(record['result'][:1000] + "..." if len(record['result']) > 1000 else record['result'])
                
                # Quick actions
                hist_col1, hist_col2 = st.columns(2)
                with hist_col1:
                    if st.button(f"📋 Copy", key=f"hist_copy_{i}"):
                        st.success("Copied!")
                with hist_col2:
                    st.download_button(
                        label="💾 Download",
                        data=record['result'],
                        file_name=f"analysis_{i}.md",
                        mime="text/markdown",
                        key=f"hist_download_{i}"
                    )

# This would be called from the main app
if __name__ == "__main__":
    load_data_analyst_page()