import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
import json
from typing import List, Dict

# Import database utilities
try:
    from utils.database import track_tool_usage
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class SmartChatAssistant:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro")
        self.conversation_history = []
    
    def get_response(self, message: str, context: List[Dict] = None) -> str:
        """Get response from Gemini with conversation context"""
        try:
            # Build conversation context
            full_prompt = self._build_conversation_context(message, context)
            
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _build_conversation_context(self, current_message: str, context: List[Dict] = None) -> str:
        """Build conversation context for better responses"""
        if not context:
            return current_message
        
        context_text = "Previous conversation:\n"
        for msg in context[-5:]:  # Last 5 messages for context
            context_text += f"{msg['role']}: {msg['content']}\n"
        
        context_text += f"\nCurrent question: {current_message}"
        return context_text

def load_chat_page():
    st.markdown("# 💬 Smart Chat Assistant")
    st.markdown("*Powered by Gemini 1.5 Pro - Your intelligent conversation partner*")
    
    # Initialize session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_assistant" not in st.session_state:
        st.session_state.chat_assistant = SmartChatAssistant()
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### 🎛️ Chat Controls")
        
        # Chat settings
        temperature = st.slider("🌡️ Creativity Level", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.slider("📝 Response Length", 100, 2000, 1000, 100)
        
        st.markdown("---")
        
        # Conversation management
        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat_btn"):
            st.session_state.chat_messages = []
            st.rerun()
        
        if st.button("💾 Export Chat", use_container_width=True, key="export_chat_btn"):
            if st.session_state.chat_messages:
                chat_data = {
                    "timestamp": datetime.now().isoformat(),
                    "messages": st.session_state.chat_messages
                }
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(chat_data, indent=2),
                    file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key="download_chat_json"
                )
        
        # Quick prompts
        st.markdown("### ⚡ Quick Prompts")
        quick_prompts = [
            "Explain quantum computing",
            "Write a creative story",
            "Help me debug code",
            "Analyze this data",
            "Brainstorm ideas"
        ]
        
        for i, prompt in enumerate(quick_prompts):
            if st.button(f"💡 {prompt}", use_container_width=True, key=f"quick_{i}"):
                st.session_state.pending_message = prompt
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat display area
        chat_container = st.container()
        
        with chat_container:
            if st.session_state.chat_messages:
                for i, message in enumerate(st.session_state.chat_messages):
                    if message["role"] == "user":
                        with st.chat_message("user", avatar="🧑‍💻"):
                            st.write(message["content"])
                            st.caption(message.get("timestamp", ""))
                    else:
                        with st.chat_message("assistant", avatar="🤖"):
                            st.write(message["content"])
                            st.caption(message.get("timestamp", ""))
            else:
                st.info("👋 Welcome! Start a conversation by typing a message below.")
                
                # Sample conversation starters
                st.markdown("**💡 Try asking:**")
                examples = [
                    "What are the latest trends in AI?",
                    "Help me write a professional email",
                    "Explain machine learning in simple terms",
                    "Create a marketing strategy for my startup"
                ]
                for example in examples:
                    st.markdown(f"• *{example}*")
        
        # Input area
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area(
                "💭 Type your message:", 
                placeholder="Ask anything... I'm here to help!",
                height=100,
                key="chat_input"
            )
            
            submitted = st.form_submit_button("🚀 Send", use_container_width=True)
        
        # Voice button outside form
        if st.button("🎤 Voice Input", disabled=True, help="Coming soon!", use_container_width=True):
            pass
    
    with col2:
        # Chat statistics
        st.markdown("### 📊 Chat Stats")
        st.metric("Messages", len(st.session_state.chat_messages))
        st.metric("Words", sum(len(msg["content"].split()) for msg in st.session_state.chat_messages))
        
        if st.session_state.chat_messages:
            avg_response_length = sum(
                len(msg["content"]) for msg in st.session_state.chat_messages 
                if msg["role"] == "assistant"
            ) / len([msg for msg in st.session_state.chat_messages if msg["role"] == "assistant"])
            st.metric("Avg Response", f"{avg_response_length:.0f} chars")
        
        # AI personality selector
        st.markdown("### 🎭 AI Personality")
        personality = st.selectbox(
            "Choose AI style:",
            ["Professional", "Creative", "Technical", "Friendly", "Academic"],
            key="ai_personality"
        )
    
    # Handle form submission or quick prompts
    message_to_process = None
    if submitted and user_input.strip():
        message_to_process = user_input
    elif "pending_message" in st.session_state:
        message_to_process = st.session_state.pending_message
        del st.session_state.pending_message
    
    if message_to_process:
        # Add user message
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_messages.append({
            "role": "user",
            "content": message_to_process,
            "timestamp": timestamp
        })
        
        # Get AI response
        with st.spinner("🤔 Thinking..."):
            # Track usage
            if DB_AVAILABLE:
                track_tool_usage("smart_chat", "message_sent")
            
            # Add personality context
            personality_context = {
                "Professional": "Respond in a professional, business-appropriate tone.",
                "Creative": "Be creative, imaginative, and think outside the box.",
                "Technical": "Provide technical, detailed, and precise explanations.",
                "Friendly": "Be warm, conversational, and approachable.",
                "Academic": "Use scholarly language and provide well-researched responses."
            }
            
            enhanced_message = f"{personality_context.get(personality, '')} {message_to_process}"
            
            response = st.session_state.chat_assistant.get_response(
                enhanced_message,
                st.session_state.chat_messages[:-1]  # Exclude the just-added user message
            )
        
        # Add AI response
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        st.rerun()

# This would be called from the main app
if __name__ == "__main__":
    load_chat_page()