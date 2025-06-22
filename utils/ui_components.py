import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import List, Dict, Optional, Any, Callable
import json

class UIComponents:
    """Reusable UI components for GeminiCraft Studio"""
    
    @staticmethod
    def display_header(title: str, subtitle: str = "", icon: str = "🚀"):
        """Display styled page header"""
        st.markdown(f"""
        <div class="main-header">
            <h1>{icon} {title}</h1>
            {f'<p><em>{subtitle}</em></p>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def display_feature_card(title: str, description: str, features: List[str], icon: str = "🔧"):
        """Display feature card"""
        features_html = "".join([f"<li>{feature}</li>" for feature in features])
        
        st.markdown(f"""
        <div class="feature-card">
            <h3>{icon} {title}</h3>
            <p>{description}</p>
            <ul>
                {features_html}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def display_metric_card(title: str, value: str, change: str = "", color: str = "primary"):
        """Display metric card with styling"""
        color_class = f"metric-card-{color}"
        change_html = f'<p class="metric-change">{change}</p>' if change else ''
        
        st.markdown(f"""
        <div class="metric-card {color_class}">
            <h4>{title}</h4>
            <h2>{value}</h2>
            {change_html}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def display_info_panel(title: str, content: Dict[str, Any], icon: str = "ℹ️"):
        """Display styled information panel"""
        content_html = ""
        for key, value in content.items():
            content_html += f"<p><strong>{key}:</strong> {value}</p>"
        
        st.markdown(f"""
        <div class="sidebar-info">
            <h4>{icon} {title}</h4>
            {content_html}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def display_status_indicator(status: str, message: str = ""):
        """Display status indicator"""
        status_config = {
            "online": {"color": "#28a745", "icon": "✅", "text": "Online"},
            "offline": {"color": "#dc3545", "icon": "❌", "text": "Offline"}, 
            "processing": {"color": "#ffc107", "icon": "⏳", "text": "Processing"},
            "error": {"color": "#dc3545", "icon": "🚨", "text": "Error"},
            "success": {"color": "#28a745", "icon": "✅", "text": "Success"}
        }
        
        config = status_config.get(status, status_config["offline"])
        display_text = message or config["text"]
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 0.5rem; border-radius: 5px; background-color: {config['color']}20; border-left: 4px solid {config['color']};">
            <span style="margin-right: 0.5rem; font-size: 1.2em;">{config['icon']}</span>
            <span style="color: {config['color']}; font-weight: bold;">{display_text}</span>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_progress_bar(progress: float, title: str = "", show_percentage: bool = True):
        """Create animated progress bar"""
        percentage = int(progress * 100)
        percentage_text = f"{percentage}%" if show_percentage else ""
        
        st.markdown(f"""
        <div class="progress-container">
            {f'<p class="progress-title">{title}</p>' if title else ''}
            <div class="progress-bar">
                <div class="progress-fill" style="width: {percentage}%;"></div>
                <span class="progress-text">{percentage_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def display_code_block(code: str, language: str = "python", title: str = ""):
        """Display styled code block with copy functionality"""
        if title:
            st.markdown(f"**{title}**")
        
        st.code(code, language=language)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("📋 Copy", key=f"copy_{hash(code)}"):
                st.success("Copied!")
    
    @staticmethod
    def create_action_buttons(buttons: List[Dict[str, Any]], columns: int = 3):
        """Create grid of action buttons"""
        cols = st.columns(columns)
        
        for i, button in enumerate(buttons):
            col = cols[i % columns]
            with col:
                icon = button.get("icon", "🔧")
                label = button.get("label", "Button")
                key = button.get("key", f"btn_{i}")
                callback = button.get("callback")
                disabled = button.get("disabled", False)
                
                if st.button(f"{icon} {label}", key=key, disabled=disabled, use_container_width=True):
                    if callback:
                        callback()
                    return button
        return None
    
    @staticmethod
    def display_chat_message(message: Dict[str, Any], show_timestamp: bool = True):
        """Display chat message with styling"""
        role = message.get("role", "user")
        content = message.get("content", "")
        timestamp = message.get("timestamp", "")
        metadata = message.get("metadata", {})
        
        avatar = "🧑‍💻" if role == "user" else "🤖"
        
        with st.chat_message(role, avatar=avatar):
            st.write(content)
            
            if show_timestamp and timestamp:
                st.caption(f"⏰ {timestamp}")
            
            # Action buttons for messages
            if role == "assistant":
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("📋", key=f"copy_msg_{hash(content)}", help="Copy message"):
                        st.success("Copied!")
                with col2:
                    if st.button("🔄", key=f"regen_msg_{hash(content)}", help="Regenerate"):
                        return "regenerate"
                with col3:
                    pass  # Reserved for future actions
        
        return None
    
    @staticmethod
    def create_file_uploader_enhanced(
        label: str,
        accepted_types: List[str],
        max_size_mb: int = 10,
        multiple: bool = False,
        help_text: str = ""
    ):
        """Enhanced file uploader with validation"""
        st.markdown(f"### 📁 {label}")
        
        uploaded_files = st.file_uploader(
            f"Choose files ({', '.join(accepted_types)})",
            type=accepted_types,
            accept_multiple_files=multiple,
            help=help_text or f"Maximum file size: {max_size_mb}MB"
        )
        
        if uploaded_files:
            files = uploaded_files if multiple else [uploaded_files]
            
            for file in files:
                if file.size > max_size_mb * 1024 * 1024:
                    st.error(f"❌ {file.name} is too large (max {max_size_mb}MB)")
                else:
                    st.success(f"✅ {file.name} ({file.size:,} bytes)")
        
        return uploaded_files
    
    @staticmethod
    def display_data_table(
        data: List[Dict[str, Any]], 
        title: str = "Data Table",
        searchable: bool = True,
        sortable: bool = True,
        max_rows: int = 100
    ):
        """Display enhanced data table"""
        if not data:
            st.info("No data to display")
            return
        
        st.markdown(f"### 📊 {title}")
        
        # Search functionality
        if searchable and len(data) > 10:
            search_term = st.text_input("🔍 Search:", placeholder="Enter search term...")
            if search_term:
                data = [
                    row for row in data 
                    if any(search_term.lower() in str(value).lower() for value in row.values())
                ]
        
        # Display table
        if len(data) > max_rows:
            st.warning(f"Showing first {max_rows} rows of {len(data)} total rows")
            data = data[:max_rows]
        
        st.dataframe(data, use_container_width=True)
        
        # Export options
        if st.button("📥 Export Data"):
            json_data = json.dumps(data, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"{title.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    @staticmethod
    def create_settings_panel(settings: Dict[str, Any], title: str = "Settings"):
        """Create settings panel with various input types"""
        st.markdown(f"### ⚙️ {title}")
        
        updated_settings = {}
        
        with st.expander("Configure Settings", expanded=False):
            for key, config in settings.items():
                setting_type = config.get("type", "text")
                label = config.get("label", key.title())
                value = config.get("value")
                options = config.get("options", [])
                help_text = config.get("help", "")
                
                if setting_type == "text":
                    updated_settings[key] = st.text_input(label, value=value, help=help_text)
                
                elif setting_type == "number":
                    min_val = config.get("min", 0)
                    max_val = config.get("max", 100)
                    updated_settings[key] = st.number_input(label, min_value=min_val, max_value=max_val, value=value, help=help_text)
                
                elif setting_type == "slider":
                    min_val = config.get("min", 0)
                    max_val = config.get("max", 100)
                    step = config.get("step", 1)
                    updated_settings[key] = st.slider(label, min_value=min_val, max_value=max_val, value=value, step=step, help=help_text)
                
                elif setting_type == "selectbox":
                    index = options.index(value) if value in options else 0
                    updated_settings[key] = st.selectbox(label, options=options, index=index, help=help_text)
                
                elif setting_type == "checkbox":
                    updated_settings[key] = st.checkbox(label, value=value, help=help_text)
                
                elif setting_type == "multiselect":
                    updated_settings[key] = st.multiselect(label, options=options, default=value, help=help_text)
        
        return updated_settings
    
    @staticmethod
    def display_timeline(events: List[Dict[str, Any]], title: str = "Timeline"):
        """Display timeline of events"""
        st.markdown(f"### 📅 {title}")
        
        for i, event in enumerate(events):
            timestamp = event.get("timestamp", "")
            title = event.get("title", "Event")
            description = event.get("description", "")
            event_type = event.get("type", "info")
            
            # Color coding by type
            color_map = {
                "success": "#28a745",
                "error": "#dc3545", 
                "warning": "#ffc107",
                "info": "#17a2b8"
            }
            color = color_map.get(event_type, "#17a2b8")
            
            st.markdown(f"""
            <div style="border-left: 4px solid {color}; padding-left: 1rem; margin: 1rem 0;">
                <p style="margin: 0; color: {color}; font-weight: bold;">{timestamp}</p>
                <h5 style="margin: 0.5rem 0;">{title}</h5>
                <p style="margin: 0; color: #666;">{description}</p>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def create_usage_chart(data: Dict[str, int], title: str = "Usage Statistics"):
        """Create usage statistics chart"""
        if not data:
            st.info("No usage data available")
            return
        
        st.markdown(f"### 📈 {title}")
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=list(data.keys()),
            values=list(data.values()),
            hole=0.3,
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            title=title,
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display table
        usage_data = [{"Tool": k, "Usage Count": v} for k, v in data.items()]
        st.dataframe(usage_data, use_container_width=True)
    
    @staticmethod
    def display_alert(message: str, alert_type: str = "info", dismissible: bool = True):
        """Display styled alert"""
        alert_config = {
            "info": {"color": "#17a2b8", "icon": "ℹ️", "bg": "#d1ecf1"},
            "success": {"color": "#28a745", "icon": "✅", "bg": "#d4edda"},
            "warning": {"color": "#ffc107", "icon": "⚠️", "bg": "#fff3cd"},
            "error": {"color": "#dc3545", "icon": "🚨", "bg": "#f8d7da"}
        }
        
        config = alert_config.get(alert_type, alert_config["info"])
        
        st.markdown(f"""
        <div style="
            padding: 1rem;
            border-radius: 0.375rem;
            background-color: {config['bg']};
            border: 1px solid {config['color']}40;
            margin: 1rem 0;
        ">
            <div style="display: flex; align-items: center;">
                <span style="margin-right: 0.5rem; font-size: 1.2em;">{config['icon']}</span>
                <span style="color: {config['color']}; font-weight: 500;">{message}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_tabs_enhanced(tabs: List[Dict[str, Any]]):
        """Create enhanced tabs with content"""
        tab_names = [tab["name"] for tab in tabs]
        tab_objects = st.tabs(tab_names)
        
        for i, (tab, tab_data) in enumerate(zip(tab_objects, tabs)):
            with tab:
                if "content" in tab_data:
                    if callable(tab_data["content"]):
                        tab_data["content"]()
                    else:
                        st.write(tab_data["content"])
                
                if "components" in tab_data:
                    for component in tab_data["components"]:
                        component()
    
    @staticmethod
    def display_loading_spinner(message: str = "Processing..."):
        """Display loading spinner with message"""
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; padding: 2rem;">
            <div class="loading-spinner"></div>
            <span style="margin-left: 1rem; font-weight: 500;">{message}</span>
        </div>
        """, unsafe_allow_html=True)

# Convenience functions for common UI patterns
def show_success(message: str):
    """Show success message"""
    UIComponents.display_alert(message, "success")

def show_error(message: str):
    """Show error message"""
    UIComponents.display_alert(message, "error")

def show_warning(message: str):
    """Show warning message"""
    UIComponents.display_alert(message, "warning")

def show_info(message: str):
    """Show info message"""
    UIComponents.display_alert(message, "info")

def create_two_column_layout(left_content: Callable, right_content: Callable, ratio: List[int] = [1, 1]):
    """Create two-column layout with content functions"""
    col1, col2 = st.columns(ratio)
    
    with col1:
        left_content()
    
    with col2:
        right_content()

def create_three_column_layout(left_content: Callable, center_content: Callable, right_content: Callable, ratio: List[int] = [1, 1, 1]):
    """Create three-column layout with content functions"""
    col1, col2, col3 = st.columns(ratio)
    
    with col1:
        left_content()
    
    with col2:
        center_content()
    
    with col3:
        right_content()

def display_tool_metrics(metrics: Dict[str, Any]):
    """Display tool-specific metrics"""
    cols = st.columns(len(metrics))
    
    for i, (key, value) in enumerate(metrics.items()):
        with cols[i]:
            st.metric(
                label=key.replace("_", " ").title(),
                value=value,
                delta=None
            )