import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Import database utilities
try:
    from utils.database import get_database_manager, track_tool_usage
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    st.warning("Database utilities not available. Usage tracking disabled.")

# Configure page
st.set_page_config(
    page_title="GeminiCraft Studio",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for responsive design and dark mode support
def load_css():
    st.markdown("""
    <style>
    /* CSS Custom Properties for Theme Support */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --success-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        
        /* Light Mode Colors */
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --text-muted: #94a3b8;
        --border-color: #e2e8f0;
        --shadow-light: rgba(0, 0, 0, 0.05);
        --shadow-medium: rgba(0, 0, 0, 0.1);
        --shadow-heavy: rgba(0, 0, 0, 0.15);
    }

    /* Dark Mode Colors */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --border-color: #475569;
            --shadow-light: rgba(0, 0, 0, 0.2);
            --shadow-medium: rgba(0, 0, 0, 0.3);
            --shadow-heavy: rgba(0, 0, 0, 0.4);
        }
    }

    /* Streamlit Dark Mode Override */
    .stApp[data-theme="dark"] {
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary: #334155;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --border-color: #475569;
        --shadow-light: rgba(0, 0, 0, 0.2);
        --shadow-medium: rgba(0, 0, 0, 0.3);
        --shadow-heavy: rgba(0, 0, 0, 0.4);
    }

    /* Base Styles */
    .stApp {
        background: var(--bg-secondary);
        color: var(--text-primary);
        transition: all 0.3s ease;
    }

    /* Enhanced Main Header */
    .main-header {
        background: var(--primary-gradient);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2.5rem;
        text-align: center;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px var(--shadow-medium);
        backdrop-filter: blur(10px);
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        pointer-events: none;
    }

    .main-header h1 {
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    .main-header p {
        font-size: clamp(1rem, 2.5vw, 1.3rem);
        margin: 0.5rem 0;
        opacity: 0.95;
    }

    /* Enhanced Feature Cards */
    .feature-card {
        background: var(--bg-primary);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        margin: 1rem 0;
        box-shadow: 0 8px 32px var(--shadow-light);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--primary-gradient);
        transition: width 0.3s ease;
    }

    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px var(--shadow-medium);
        border-color: transparent;
    }

    .feature-card:hover::before {
        width: 100%;
        opacity: 0.1;
    }

    .feature-card h3 {
        color: var(--text-primary);
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .feature-card p {
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    .feature-card ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .feature-card li {
        color: var(--text-muted);
        padding: 0.3rem 0;
        position: relative;
        padding-left: 1.5rem;
        font-size: 0.9rem;
    }

    .feature-card li::before {
        content: '✨';
        position: absolute;
        left: 0;
        top: 0.3rem;
    }

    /* Enhanced Sidebar */
    .css-1d391kg, .css-1adrfps {
        background: var(--bg-primary);
        border-right: 1px solid var(--border-color);
    }

    .sidebar-info {
        background: var(--bg-tertiary);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 16px var(--shadow-light);
    }

    .sidebar-info h4 {
        color: var(--text-primary);
        margin-bottom: 1rem;
        font-weight: 600;
    }

    .sidebar-info p {
        color: var(--text-secondary);
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }

    /* Enhanced Metric Cards */
    .metric-card {
        background: var(--accent-gradient);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.8rem 0;
        box-shadow: 0 8px 24px rgba(79, 172, 254, 0.3);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(79, 172, 254, 0.4);
    }

    /* Enhanced Buttons */
    .stButton > button {
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        width: 100%;
        margin: 0.3rem 0;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        filter: brightness(110%);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Primary Button Variant */
    .stButton > button[kind="primary"] {
        background: var(--secondary-gradient);
        box-shadow: 0 4px 16px rgba(240, 147, 251, 0.3);
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 24px rgba(240, 147, 251, 0.4);
    }

    /* Enhanced Metrics */
    .stMetric {
        background: var(--bg-primary);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 16px var(--shadow-light);
        transition: all 0.3s ease;
    }

    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--shadow-medium);
    }

    .stMetric [data-testid="metric-container"] {
        background: transparent;
        border: none;
        padding: 0;
    }

    /* Quick Start Section */
    .quick-start {
        background: var(--bg-primary);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: 0 8px 32px var(--shadow-light);
        margin-top: 2rem;
    }

    /* Loading Animation */
    @keyframes shimmer {
        0% { background-position: -200px 0; }
        100% { background-position: calc(200px + 100%) 0; }
    }

    .loading-shimmer {
        background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-tertiary) 50%, var(--bg-secondary) 75%);
        background-size: 200px 100%;
        animation: shimmer 1.5s infinite;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
            margin-bottom: 1.5rem;
            border-radius: 16px;
        }

        .feature-card {
            padding: 1.5rem;
            margin: 0.8rem 0;
        }

        .feature-card h3 {
            font-size: 1.2rem;
        }

        .stButton > button {
            padding: 0.7rem 1rem;
            font-size: 0.9rem;
        }

        .sidebar-info {
            padding: 1rem;
        }
    }

    @media (max-width: 480px) {
        .main-header {
            padding: 1.5rem 0.8rem;
        }

        .feature-card {
            padding: 1.2rem;
        }

        .stButton > button {
            padding: 0.6rem 0.8rem;
            font-size: 0.85rem;
        }
    }

    /* Dark mode specific enhancements */
    @media (prefers-color-scheme: dark) {
        .feature-card {
            backdrop-filter: blur(20px);
            border-color: rgba(255, 255, 255, 0.1);
        }

        .main-header {
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }

        .stButton > button {
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
        }
    }

    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }

    /* Focus states for accessibility */
    .stButton > button:focus {
        outline: 2px solid rgba(102, 126, 234, 0.5);
        outline-offset: 2px;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .feature-card {
        animation: fadeInUp 0.6s ease-out forwards;
    }

    .feature-card:nth-child(2) { animation-delay: 0.1s; }
    .feature-card:nth-child(3) { animation-delay: 0.2s; }
    .feature-card:nth-child(4) { animation-delay: 0.3s; }
    .feature-card:nth-child(5) { animation-delay: 0.4s; }
    .feature-card:nth-child(6) { animation-delay: 0.5s; }
    </style>
    """, unsafe_allow_html=True)

def main():
    load_css()
    
    # Enhanced main header with better structure
    st.markdown("""
    <div class="main-header">
        <h1>🚀 GeminiCraft Studio</h1>
        <p>Your AI-Powered Creative Workspace</p>
        <p><em>Harness the power of Google's Gemini AI for creative and analytical tasks</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced sidebar
    with st.sidebar:
        st.markdown("## 🎯 AI Tools")
        
        # Navigation with enhanced styling
        if st.button("💬 Smart Chat Assistant", use_container_width=True):
            if DB_AVAILABLE:
                track_tool_usage("smart_chat", "page_visit")
            st.session_state.page = "chat"
        
        if st.button("👁️ Vision & Image Analysis", use_container_width=True):
            if DB_AVAILABLE:
                track_tool_usage("vision_analysis", "page_visit")
            st.session_state.page = "vision"
        
        if st.button("📄 Document Intelligence", use_container_width=True):
            if DB_AVAILABLE:
                track_tool_usage("document_intelligence", "page_visit")
            st.session_state.page = "document"
        
        if st.button("💻 Code Assistant", use_container_width=True):
            if DB_AVAILABLE:
                track_tool_usage("code_assistant", "page_visit")
            st.session_state.page = "code"
        
        if st.button("✍️ Creative Writer", use_container_width=True):
            if DB_AVAILABLE:
                track_tool_usage("creative_writer", "page_visit")
            st.session_state.page = "writer"
        
        if st.button("📊 Data Analyst", use_container_width=True):
            if DB_AVAILABLE:
                track_tool_usage("data_analyst", "page_visit")
            st.session_state.page = "data"
        
        st.markdown("---")
        
        # Enhanced info panel
        st.markdown("""
        <div class="sidebar-info">
            <h4>🔧 Studio Info</h4>
            <p><strong>Model:</strong> Gemini 1.5 Pro</p>
            <p><strong>Features:</strong> 6+ AI Tools</p>
            <p><strong>Status:</strong> Online ✅</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced usage stats
        st.markdown("### 📈 Session Stats")
        
        if DB_AVAILABLE:
            try:
                db = get_database_manager()
                stats = db.get_usage_statistics()
                
                total_queries = stats.get("total_actions", 0)
                tools_used = len(stats.get("tool_usage", {}))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Queries", f"{total_queries}", f"+{total_queries}")
                with col2:
                    st.metric("Tools Used", f"{tools_used}", f"+{tools_used}")
                
                # Show top tool if available
                if stats.get("tool_usage"):
                    top_tool = max(stats["tool_usage"].items(), key=lambda x: x[1])
                    st.caption(f"🔥 Most used: {top_tool[0].replace('_', ' ').title()}")
                    
            except Exception as e:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Queries", "0", "0")
                with col2:
                    st.metric("Tools Used", "0", "0")
                st.caption("⚠️ Stats unavailable")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Queries", "0", "0")
            with col2:
                st.metric("Tools Used", "0", "0")
    
    # Main content area
    if "page" not in st.session_state:
        st.session_state.page = "home"
    
    # Enhanced home page
    if st.session_state.page == "home":
        # Responsive grid layout
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h3>💬 Smart Chat</h3>
                <p>Intelligent conversations with advanced context understanding and natural language processing capabilities.</p>
                <ul>
                    <li>Natural language processing</li>
                    <li>Context-aware responses</li>
                    <li>Multi-turn conversations</li>
                    <li>Real-time interactions</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h3>👁️ Vision Analysis</h3>
                <p>Advanced image and visual content analysis with state-of-the-art computer vision technology.</p>
                <ul>
                    <li>Object detection & recognition</li>
                    <li>Scene understanding</li>
                    <li>Text extraction (OCR)</li>
                    <li>Image content analysis</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h3>📄 Document AI</h3>
                <p>Intelligent document processing and analysis with comprehensive understanding capabilities.</p>
                <ul>
                    <li>PDF analysis & processing</li>
                    <li>Content summarization</li>
                    <li>Q&A on documents</li>
                    <li>Information extraction</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.markdown("""
            <div class="feature-card">
                <h3>💻 Code Assistant</h3>
                <p>AI-powered coding companion that helps with development tasks and code optimization.</p>
                <ul>
                    <li>Code generation & completion</li>
                    <li>Bug detection & fixing</li>
                    <li>Code explanation & docs</li>
                    <li>Best practices guidance</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown("""
            <div class="feature-card">
                <h3>✍️ Creative Writer</h3>
                <p>AI-enhanced creative writing tools for content creation and storytelling excellence.</p>
                <ul>
                    <li>Story & content generation</li>
                    <li>Creative ideation support</li>
                    <li>Style adaptation & editing</li>
                    <li>Writing enhancement</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown("""
            <div class="feature-card">
                <h3>📊 Data Analyst</h3>
                <p>Intelligent data analysis and visualization with comprehensive statistical insights.</p>
                <ul>
                    <li>Data insights & patterns</li>
                    <li>Chart & graph generation</li>
                    <li>Statistical analysis</li>
                    <li>Predictive modeling</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced quick start section
        st.markdown("---")
        st.markdown("## 🚀 Quick Start")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            **Get started with GeminiCraft Studio in just a few steps:**
            
            1. **Choose Your Tool** - Select an AI tool from the sidebar that matches your needs
            2. **Upload & Input** - Upload files or enter your query with detailed instructions  
            3. **AI Magic** - Let our advanced Gemini AI process and analyze your request
            4. **Export Results** - Save, download, or share your AI-generated results
            
            Experience the future of AI-powered productivity today!
            """)
        
        with col2:
            if st.button("🎯 Try Smart Chat", type="primary", use_container_width=True, key="try_chat_home"):
                if DB_AVAILABLE:
                    track_tool_usage("smart_chat", "page_visit")
                st.session_state.page = "chat"
                st.rerun()
    
    # Load other pages (keeping original logic intact)
    elif st.session_state.page == "chat":
        try:
            from pages.smart_chat import load_chat_page
            load_chat_page()
        except ImportError as e:
            st.error(f"Error loading Smart Chat: {e}")
            if st.button("🏠 Back to Home"):
                st.session_state.page = "home"
                st.rerun()
    
    elif st.session_state.page == "vision":
        try:
            from pages.vision_analysis import load_vision_page
            load_vision_page()
        except ImportError as e:
            st.error(f"Error loading Vision Analysis: {e}")
            if st.button("🏠 Back to Home"):
                st.session_state.page = "home"
                st.rerun()
    
    elif st.session_state.page == "document":
        try:
            from pages.document_intelligence import load_document_intelligence_page
            load_document_intelligence_page()
        except ImportError as e:
            st.error(f"Error loading Document Intelligence: {e}")
            if st.button("🏠 Back to Home"):
                st.session_state.page = "home"
                st.rerun()
    
    elif st.session_state.page == "code":
        try:
            from pages.code_assistant import load_code_assistant_page
            load_code_assistant_page()
        except ImportError as e:
            st.error(f"Error loading Code Assistant: {e}")
            if st.button("🏠 Back to Home"):
                st.session_state.page = "home"
                st.rerun()
    
    elif st.session_state.page == "writer":
        try:
            from pages.creative_writer import load_creative_writer_page
            load_creative_writer_page()
        except ImportError as e:
            st.error(f"Error loading Creative Writer: {e}")
            if st.button("🏠 Back to Home"):
                st.session_state.page = "home"
                st.rerun()
    
    elif st.session_state.page == "data":
        try:
            from pages.data_analyst import load_data_analyst_page
            load_data_analyst_page()
        except ImportError as e:
            st.error(f"Error loading Data Analyst: {e}")
            if st.button("🏠 Back to Home"):
                st.session_state.page = "home"
                st.rerun()

if __name__ == "__main__":
    main()