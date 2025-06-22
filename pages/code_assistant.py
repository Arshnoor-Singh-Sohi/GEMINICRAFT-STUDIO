import streamlit as st
import google.generativeai as genai
import os
import re
import ast
import json
from datetime import datetime
from typing import List, Dict, Optional

# Import database utilities
try:
    from utils.database import track_tool_usage
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class CodeAssistant:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro")
        self.supported_languages = [
            "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", 
            "TypeScript", "PHP", "Ruby", "Swift", "Kotlin", "SQL", "HTML/CSS"
        ]
    
    def generate_code(self, description: str, language: str, style: str = "clean") -> str:
        """Generate code based on description"""
        prompt = f"""
        Generate {language} code for the following requirement:
        {description}
        
        Style: {style}
        Requirements:
        - Write clean, well-commented code
        - Follow best practices for {language}
        - Include error handling where appropriate
        - Add docstrings/comments for functions
        - Make it production-ready
        
        Return only the code without explanations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating code: {str(e)}"
    
    def debug_code(self, code: str, error_message: str = "", language: str = "Python") -> str:
        """Debug and fix code issues"""
        prompt = f"""
        Debug this {language} code and fix any issues:
        
        Code:
        ```{language.lower()}
        {code}
        ```
        
        Error message (if any): {error_message}
        
        Please:
        1. Identify the issues
        2. Provide the corrected code
        3. Explain what was wrong and how you fixed it
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error debugging code: {str(e)}"
    
    def explain_code(self, code: str, language: str = "Python") -> str:
        """Explain how code works"""
        prompt = f"""
        Explain this {language} code in detail:
        
        ```{language.lower()}
        {code}
        ```
        
        Please explain:
        - What the code does overall
        - How each major section works
        - Any algorithms or patterns used
        - Potential improvements or optimizations
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error explaining code: {str(e)}"
    
    def optimize_code(self, code: str, language: str = "Python") -> str:
        """Optimize code for performance"""
        prompt = f"""
        Optimize this {language} code for better performance, readability, and maintainability:
        
        ```{language.lower()}
        {code}
        ```
        
        Please provide:
        1. Optimized version of the code
        2. Explanation of optimizations made
        3. Performance improvements expected
        4. Best practices applied
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error optimizing code: {str(e)}"
    
    def review_code(self, code: str, language: str = "Python") -> str:
        """Perform code review"""
        prompt = f"""
        Perform a comprehensive code review for this {language} code:
        
        ```{language.lower()}
        {code}
        ```
        
        Review criteria:
        - Code quality and readability
        - Security vulnerabilities
        - Performance issues
        - Best practices adherence
        - Potential bugs
        - Maintainability
        - Documentation quality
        
        Provide specific suggestions for improvement.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error reviewing code: {str(e)}"
    
    def generate_tests(self, code: str, language: str = "Python") -> str:
        """Generate unit tests for code"""
        prompt = f"""
        Generate comprehensive unit tests for this {language} code:
        
        ```{language.lower()}
        {code}
        ```
        
        Requirements:
        - Cover all major functions/methods
        - Include edge cases and error conditions
        - Use appropriate testing framework for {language}
        - Add test descriptions and comments
        - Aim for high code coverage
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating tests: {str(e)}"

def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks from text"""
    code_pattern = r'```(\w+)?\n(.*?)\n```'
    matches = re.findall(code_pattern, text, re.DOTALL)
    
    code_blocks = []
    for i, match in enumerate(matches):
        language = match[0] if match[0] else "text"
        code = match[1].strip()
        code_blocks.append({
            "id": i,
            "language": language,
            "code": code
        })
    
    return code_blocks

def load_code_assistant_page():
    st.markdown("# 💻 Code Assistant")
    st.markdown("*Your AI-powered programming companion for code generation, debugging, and optimization*")
    
    # Initialize session state
    if "code_assistant" not in st.session_state:
        st.session_state.code_assistant = CodeAssistant()
    if "code_history" not in st.session_state:
        st.session_state.code_history = []
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### 🎛️ Code Controls")
        
        # Language selection
        language = st.selectbox(
            "🔤 Programming Language:",
            st.session_state.code_assistant.supported_languages,
            index=0
        )
        
        # Code style
        code_style = st.selectbox(
            "🎨 Code Style:",
            ["Clean", "Compact", "Verbose", "Enterprise", "Beginner-friendly"]
        )
        
        # Operation type
        operation = st.selectbox(
            "⚙️ Operation:",
            [
                "Generate Code",
                "Debug Code", 
                "Explain Code",
                "Optimize Code",
                "Code Review",
                "Generate Tests"
            ]
        )
        
        st.markdown("---")
        
        # Quick templates
        st.markdown("### ⚡ Quick Templates")
        templates = {
            "Web Scraper": "Create a web scraper that extracts data from a website",
            "API Client": "Build a REST API client with error handling",
            "Data Processor": "Create a data processing pipeline for CSV files",
            "Authentication": "Implement user authentication system",
            "Database CRUD": "Create database CRUD operations",
            "File Manager": "Build a file management utility"
        }
        
        for template_name, template_desc in templates.items():
            if st.button(f"📝 {template_name}", use_container_width=True):
                st.session_state.template_prompt = template_desc
        
        st.markdown("---")
        
        # History management
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.code_history = []
            st.rerun()
        
        if st.session_state.code_history:
            if st.button("💾 Export History", use_container_width=True):
                history_data = {
                    "timestamp": datetime.now().isoformat(),
                    "language": language,
                    "operations": st.session_state.code_history
                }
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(history_data, indent=2),
                    file_name=f"code_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Input")
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Text Description", "Code Upload", "Code Paste"]
        )
        
        user_input = ""
        uploaded_code = ""
        
        if input_method == "Text Description":
            user_input = st.text_area(
                f"Describe what you want to {operation.lower()}:",
                placeholder="e.g., Create a function that sorts a list of dictionaries by a specific key...",
                height=150,
                key="code_description"
            )
            
            # Check for template prompt
            if "template_prompt" in st.session_state:
                st.text_area(
                    "Template loaded:",
                    value=st.session_state.template_prompt,
                    height=50,
                    disabled=True
                )
                user_input = st.session_state.template_prompt
                del st.session_state.template_prompt
        
        elif input_method == "Code Upload":
            uploaded_file = st.file_uploader(
                "Upload code file",
                type=["py", "js", "java", "cpp", "cs", "go", "rs", "ts", "php", "rb", "swift", "kt", "sql", "html", "css"]
            )
            if uploaded_file:
                uploaded_code = str(uploaded_file.read(), "utf-8")
                st.code(uploaded_code[:500] + "..." if len(uploaded_code) > 500 else uploaded_code)
        
        elif input_method == "Code Paste":
            uploaded_code = st.text_area(
                "Paste your code here:",
                placeholder="Paste your code for debugging, explanation, or optimization...",
                height=200
            )
        
        # Error message for debugging
        error_message = ""
        if operation == "Debug Code":
            error_message = st.text_area(
                "Error message (optional):",
                placeholder="Paste any error messages you're getting...",
                height=100
            )
        
        # Process button
        if st.button("🚀 Process Code", type="primary", use_container_width=True):
            if (operation == "Generate Code" and user_input) or (operation != "Generate Code" and uploaded_code):
                # Track usage
                if DB_AVAILABLE:
                    track_tool_usage("code_assistant", f"operation_{operation.lower().replace(' ', '_')}")
                
                with st.spinner(f"🔄 {operation}..."):
                    
                    result = ""
                    if operation == "Generate Code":
                        result = st.session_state.code_assistant.generate_code(
                            user_input, language, code_style.lower()
                        )
                    elif operation == "Debug Code":
                        result = st.session_state.code_assistant.debug_code(
                            uploaded_code, error_message, language
                        )
                    elif operation == "Explain Code":
                        result = st.session_state.code_assistant.explain_code(
                            uploaded_code, language
                        )
                    elif operation == "Optimize Code":
                        result = st.session_state.code_assistant.optimize_code(
                            uploaded_code, language
                        )
                    elif operation == "Code Review":
                        result = st.session_state.code_assistant.review_code(
                            uploaded_code, language
                        )
                    elif operation == "Generate Tests":
                        result = st.session_state.code_assistant.generate_tests(
                            uploaded_code, language
                        )
                    
                    # Store result in session state for display in col2
                    st.session_state.current_result = result
                    
                    # Save to history
                    history_record = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "operation": operation,
                        "language": language,
                        "input": user_input if user_input else uploaded_code[:200] + "...",
                        "result": result
                    }
                    st.session_state.code_history.append(history_record)
                    
                    st.rerun()
            else:
                st.error("Please provide input for the selected operation.")
    
    with col2:
        st.markdown("### 📤 Output")
        
        if "current_result" in st.session_state:
            result = st.session_state.current_result
            
            # Extract and display code blocks
            code_blocks = extract_code_blocks(result)
            
            if code_blocks:
                st.markdown("**🎯 Generated Code:**")
                for block in code_blocks:
                    st.code(block["code"], language=block["language"])
                    
                    # Action buttons for each code block
                    col_copy, col_download = st.columns(2)
                    with col_copy:
                        if st.button(f"📋 Copy", key=f"copy_{block['id']}"):
                            st.success("Code copied!")
                    with col_download:
                        file_extension = {
                            "python": "py", "javascript": "js", "java": "java",
                            "cpp": "cpp", "csharp": "cs", "go": "go",
                            "rust": "rs", "typescript": "ts", "php": "php",
                            "ruby": "rb", "swift": "swift", "kotlin": "kt",
                            "sql": "sql", "html": "html", "css": "css"
                        }.get(block["language"].lower(), "txt")
                        
                        st.download_button(
                            label="💾 Download",
                            data=block["code"],
                            file_name=f"generated_code_{block['id']}.{file_extension}",
                            mime="text/plain",
                            key=f"download_{block['id']}"
                        )
            
            # Display full response
            st.markdown("**📋 Full Response:**")
            st.write(result)
            
            # Overall action buttons
            col_copy_all, col_save_all = st.columns(2)
            with col_copy_all:
                if st.button("📋 Copy All", use_container_width=True):
                    st.success("Full response copied!")
            
            with col_save_all:
                st.download_button(
                    label="💾 Save Response",
                    data=result,
                    file_name=f"code_assistant_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        
        else:
            st.info("👈 Enter your code requirements and click 'Process Code' to get started")
            
            # Example prompts
            st.markdown("**💡 Example prompts:**")
            examples = {
                "Generate Code": [
                    "Create a binary search algorithm",
                    "Build a REST API with Flask",
                    "Implement a LRU cache",
                    "Create a web scraper for news articles"
                ],
                "Debug Code": [
                    "Fix runtime errors in sorting function",
                    "Resolve memory leaks in C++ code",
                    "Debug authentication issues",
                    "Fix SQL query performance problems"
                ],
                "Explain Code": [
                    "Complex algorithm implementation",
                    "Design pattern usage",
                    "Database query optimization",
                    "API endpoint functionality"
                ]
            }
            
            if operation in examples:
                for example in examples[operation]:
                    st.markdown(f"• *{example}*")
    
    # Code History
    if st.session_state.code_history:
        st.markdown("---")
        st.markdown("## 📚 Code History")
        
        for i, record in enumerate(reversed(st.session_state.code_history[-5:])):  # Show last 5
            with st.expander(f"💻 {record['operation']} ({record['language']}) - {record['timestamp']}"):
                st.markdown(f"**Input:** {record['input']}")
                st.markdown(f"**Result:**")
                
                # Extract and display code blocks from history
                history_blocks = extract_code_blocks(record['result'])
                if history_blocks:
                    for block in history_blocks:
                        st.code(block["code"], language=block["language"])
                else:
                    st.write(record['result'])

# This would be called from the main app
if __name__ == "__main__":
    load_code_assistant_page()