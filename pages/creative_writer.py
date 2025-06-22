import streamlit as st
import google.generativeai as genai
import os
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

class CreativeWriter:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro")
        self.content_types = [
            "Short Story", "Blog Post", "Marketing Copy", "Technical Article", 
            "Social Media Post", "Email", "Product Description", "Press Release",
            "Creative Fiction", "Poetry", "Song Lyrics", "Script/Screenplay"
        ]
        self.writing_styles = [
            "Professional", "Casual", "Persuasive", "Academic", "Creative", 
            "Humorous", "Dramatic", "Informative", "Inspiring", "Technical"
        ]
        self.tones = [
            "Friendly", "Formal", "Enthusiastic", "Confident", "Empathetic",
            "Authoritative", "Conversational", "Urgent", "Calm", "Playful"
        ]
    
    def generate_content(
        self, 
        content_type: str, 
        topic: str, 
        style: str, 
        tone: str, 
        word_count: int,
        additional_requirements: str = ""
    ) -> str:
        """Generate creative content based on parameters"""
        
        prompt = f"""
        Create a {content_type.lower()} on the topic: "{topic}"
        
        Requirements:
        - Writing style: {style}
        - Tone: {tone}
        - Target word count: {word_count} words
        - Content type: {content_type}
        
        Additional requirements: {additional_requirements}
        
        Guidelines:
        - Make it engaging and well-structured
        - Use appropriate formatting for the content type
        - Include a compelling opening and strong conclusion
        - Ensure the content matches the specified style and tone
        - Make it original and creative
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating content: {str(e)}"
    
    def improve_content(self, content: str, improvement_type: str) -> str:
        """Improve existing content"""
        
        improvement_prompts = {
            "Grammar & Style": "Improve the grammar, style, and readability of this content while maintaining its original meaning and tone.",
            "Make More Engaging": "Rewrite this content to make it more engaging, compelling, and interesting to read.",
            "Shorten": "Condense this content to make it more concise while keeping all key points.",
            "Expand": "Expand this content with more details, examples, and elaboration.",
            "Change Tone": "Rewrite this content with a more professional and polished tone.",
            "Add SEO": "Optimize this content for search engines by adding relevant keywords naturally."
        }
        
        prompt = f"""
        {improvement_prompts.get(improvement_type, 'Improve this content:')}
        
        Original content:
        {content}
        
        Please provide the improved version.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error improving content: {str(e)}"
    
    def generate_ideas(self, topic: str, content_type: str, count: int = 10) -> str:
        """Generate content ideas"""
        
        prompt = f"""
        Generate {count} creative and engaging ideas for {content_type.lower()} content about "{topic}".
        
        For each idea, provide:
        1. A catchy title/headline
        2. A brief description of the content
        3. Key points to cover
        
        Make the ideas diverse, unique, and engaging.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating ideas: {str(e)}"
    
    def create_outline(self, topic: str, content_type: str, target_length: str) -> str:
        """Create content outline"""
        
        prompt = f"""
        Create a detailed outline for a {content_type.lower()} about "{topic}".
        Target length: {target_length}
        
        Include:
        - Introduction/hook
        - Main sections with subsections
        - Key points for each section
        - Conclusion
        - Suggested word count for each section
        
        Make it comprehensive and well-structured.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error creating outline: {str(e)}"
    
    def analyze_content(self, content: str) -> str:
        """Analyze content for readability, tone, and effectiveness"""
        
        prompt = f"""
        Analyze this content and provide insights on:
        
        1. Readability level and clarity
        2. Tone and style assessment
        3. Strengths and weaknesses
        4. Target audience suitability
        5. Engagement potential
        6. Suggestions for improvement
        7. Overall effectiveness rating (1-10)
        
        Content to analyze:
        {content}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error analyzing content: {str(e)}"

def load_creative_writer_page():
    st.markdown("# ✍️ Creative Writer")
    st.markdown("*AI-powered creative writing assistant for compelling content creation*")
    
    # Initialize session state
    if "creative_writer" not in st.session_state:
        st.session_state.creative_writer = CreativeWriter()
    if "writing_history" not in st.session_state:
        st.session_state.writing_history = []
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### 🎛️ Writing Controls")
        
        # Content type selection
        content_type = st.selectbox(
            "📝 Content Type:",
            st.session_state.creative_writer.content_types
        )
        
        # Writing style
        writing_style = st.selectbox(
            "🎨 Writing Style:",
            st.session_state.creative_writer.writing_styles
        )
        
        # Tone
        tone = st.selectbox(
            "🎭 Tone:",
            st.session_state.creative_writer.tones
        )
        
        # Word count
        word_count = st.slider(
            "📏 Target Word Count:",
            min_value=50,
            max_value=5000,
            value=500,
            step=50
        )
        
        # Operation type
        operation = st.selectbox(
            "⚙️ Operation:",
            [
                "Generate Content",
                "Improve Content",
                "Generate Ideas", 
                "Create Outline",
                "Analyze Content"
            ]
        )
        
        st.markdown("---")
        
        # Quick templates
        st.markdown("### ⚡ Content Templates")
        templates = {
            "Product Launch": {
                "type": "Marketing Copy",
                "topic": "New product launch announcement",
                "style": "Persuasive",
                "tone": "Enthusiastic"
            },
            "Company Blog": {
                "type": "Blog Post", 
                "topic": "Industry trends and insights",
                "style": "Professional",
                "tone": "Informative"
            },
            "Social Media": {
                "type": "Social Media Post",
                "topic": "Engaging social media content",
                "style": "Casual",
                "tone": "Friendly"
            },
            "Technical Guide": {
                "type": "Technical Article",
                "topic": "How-to guide for developers",
                "style": "Technical",
                "tone": "Authoritative"
            }
        }
        
        for template_name, template_data in templates.items():
            if st.button(f"📋 {template_name}", use_container_width=True):
                st.session_state.template_data = template_data
        
        st.markdown("---")
        
        # History management
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.writing_history = []
            st.rerun()
        
        if st.session_state.writing_history:
            if st.button("💾 Export History", use_container_width=True):
                history_data = {
                    "timestamp": datetime.now().isoformat(),
                    "writings": st.session_state.writing_history
                }
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(history_data, indent=2),
                    file_name=f"writing_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Input")
        
        # Check for template data
        if "template_data" in st.session_state:
            template = st.session_state.template_data
            st.info(f"Template loaded: {template['type']} - {template['style']} style")
            content_type = template['type']
            writing_style = template['style'] 
            tone = template['tone']
            del st.session_state.template_data
        
        # Topic input
        topic = st.text_area(
            "🎯 Topic/Subject:",
            placeholder="Enter your topic, keywords, or main subject...",
            height=100,
            key="writing_topic"
        )
        
        # Content for improvement/analysis
        existing_content = ""
        if operation in ["Improve Content", "Analyze Content"]:
            existing_content = st.text_area(
                "📄 Existing Content:",
                placeholder="Paste the content you want to improve or analyze...",
                height=200,
                key="existing_content"
            )
        
        # Additional requirements
        if operation == "Generate Content":
            additional_reqs = st.text_area(
                "📋 Additional Requirements (optional):",
                placeholder="e.g., Include specific keywords, target audience, call-to-action, etc.",
                height=80
            )
        
        # Improvement type for content improvement
        improvement_type = ""
        if operation == "Improve Content":
            improvement_type = st.selectbox(
                "🔧 Improvement Type:",
                [
                    "Grammar & Style",
                    "Make More Engaging", 
                    "Shorten",
                    "Expand",
                    "Change Tone",
                    "Add SEO"
                ]
            )
        
        # Ideas count
        ideas_count = 10
        if operation == "Generate Ideas":
            ideas_count = st.slider(
                "💡 Number of Ideas:",
                min_value=5,
                max_value=20,
                value=10
            )
        
        # Process button
        if st.button("🚀 Create Content", type="primary", use_container_width=True):
            # Validate inputs
            if operation in ["Generate Content", "Generate Ideas", "Create Outline"] and not topic:
                st.error("Please enter a topic.")
            elif operation in ["Improve Content", "Analyze Content"] and not existing_content:
                st.error("Please provide content to improve or analyze.")
            else:
                # Track usage
                if DB_AVAILABLE:
                    track_tool_usage("creative_writer", f"operation_{operation.lower().replace(' ', '_')}")
                
                with st.spinner(f"✨ {operation}..."):
                    
                    result = ""
                    if operation == "Generate Content":
                        result = st.session_state.creative_writer.generate_content(
                            content_type, topic, writing_style, tone, word_count, 
                            additional_reqs if 'additional_reqs' in locals() else ""
                        )
                    elif operation == "Improve Content":
                        result = st.session_state.creative_writer.improve_content(
                            existing_content, improvement_type
                        )
                    elif operation == "Generate Ideas":
                        result = st.session_state.creative_writer.generate_ideas(
                            topic, content_type, ideas_count
                        )
                    elif operation == "Create Outline":
                        target_length = f"{word_count} words"
                        result = st.session_state.creative_writer.create_outline(
                            topic, content_type, target_length
                        )
                    elif operation == "Analyze Content":
                        result = st.session_state.creative_writer.analyze_content(
                            existing_content
                        )
                    
                    # Store result
                    st.session_state.current_writing_result = result
                    
                    # Save to history
                    history_record = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "operation": operation,
                        "content_type": content_type,
                        "style": writing_style,
                        "tone": tone,
                        "topic": topic,
                        "word_count": word_count,
                        "result": result
                    }
                    st.session_state.writing_history.append(history_record)
                    
                    st.rerun()
    
    with col2:
        st.markdown("### 📤 Output")
        
        if "current_writing_result" in st.session_state:
            result = st.session_state.current_writing_result
            
            # Display result
            st.markdown("**✨ Generated Content:**")
            st.write(result)
            
            # Word count analysis
            word_count_actual = len(result.split())
            st.caption(f"📊 Word count: {word_count_actual} words")
            
            # Action buttons
            col_copy, col_save, col_improve = st.columns(3)
            
            with col_copy:
                if st.button("📋 Copy", use_container_width=True):
                    st.success("Content copied!")
            
            with col_save:
                file_extension = "md" if operation in ["Generate Content", "Improve Content"] else "txt"
                st.download_button(
                    label="💾 Save",
                    data=result,
                    file_name=f"creative_writing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col_improve:
                if st.button("🔧 Improve", use_container_width=True):
                    st.session_state.improve_content = result
                    st.info("Content loaded for improvement!")
            
            # Content metrics
            if operation in ["Generate Content", "Improve Content"]:
                st.markdown("---")
                st.markdown("**📈 Content Metrics:**")
                
                sentences = len([s for s in result.split('.') if s.strip()])
                paragraphs = len([p for p in result.split('\n\n') if p.strip()])
                
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                with metric_col1:
                    st.metric("Words", word_count_actual)
                with metric_col2:
                    st.metric("Sentences", sentences)
                with metric_col3:
                    st.metric("Paragraphs", paragraphs)
        
        else:
            st.info("👈 Enter your requirements and click 'Create Content' to get started")
            
            # Example content ideas
            st.markdown("**💡 Content Ideas:**")
            content_examples = {
                "Blog Post": [
                    "Industry trends and predictions",
                    "How-to guides and tutorials",
                    "Case studies and success stories",
                    "Expert interviews and insights"
                ],
                "Marketing Copy": [
                    "Product launch announcements",
                    "Email marketing campaigns", 
                    "Landing page copy",
                    "Social media advertisements"
                ],
                "Technical Article": [
                    "API documentation",
                    "Software tutorials",
                    "Best practices guides",
                    "Technology comparisons"
                ]
            }
            
            if content_type in content_examples:
                for example in content_examples[content_type]:
                    st.markdown(f"• *{example}*")
    
    # Quick Actions
    st.markdown("---")
    st.markdown("## ⚡ Quick Actions")
    
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    
    with quick_col1:
        if st.button("📝 Blog Post Generator", use_container_width=True):
            st.session_state.quick_action = {
                "operation": "Generate Content",
                "content_type": "Blog Post",
                "style": "Professional",
                "tone": "Informative"
            }
    
    with quick_col2:
        if st.button("📱 Social Media Post", use_container_width=True):
            st.session_state.quick_action = {
                "operation": "Generate Content", 
                "content_type": "Social Media Post",
                "style": "Casual",
                "tone": "Engaging"
            }
    
    with quick_col3:
        if st.button("✉️ Email Template", use_container_width=True):
            st.session_state.quick_action = {
                "operation": "Generate Content",
                "content_type": "Email",
                "style": "Professional",
                "tone": "Friendly"
            }
    
    with quick_col4:
        if st.button("💡 Content Ideas", use_container_width=True):
            st.session_state.quick_action = {
                "operation": "Generate Ideas",
                "content_type": "Blog Post",
                "count": 10
            }
    
    # Writing History
    if st.session_state.writing_history:
        st.markdown("---")
        st.markdown("## 📚 Writing History")
        
        for i, record in enumerate(reversed(st.session_state.writing_history[-5:])):  # Show last 5
            with st.expander(f"✍️ {record['operation']} - {record['content_type']} - {record['timestamp']}"):
                st.markdown(f"**Topic:** {record['topic']}")
                st.markdown(f"**Style:** {record['style']} | **Tone:** {record['tone']} | **Words:** {record['word_count']}")
                st.markdown(f"**Content:**")
                st.write(record['result'][:500] + "..." if len(record['result']) > 500 else record['result'])
                
                # Quick actions for history items
                hist_col1, hist_col2 = st.columns(2)
                with hist_col1:
                    if st.button(f"📋 Copy", key=f"hist_copy_{i}"):
                        st.success("Copied!")
                with hist_col2:
                    st.download_button(
                        label="💾 Download",
                        data=record['result'],
                        file_name=f"content_{i}.md",
                        mime="text/markdown",
                        key=f"hist_download_{i}"
                    )

# This would be called from the main app
if __name__ == "__main__":
    load_creative_writer_page()