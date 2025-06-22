import google.generativeai as genai
import os
import streamlit as st
import time
from typing import Optional, List, Dict, Any
import json
from datetime import datetime

class GeminiClient:
    """Enhanced Gemini AI client with advanced features"""
    
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds
        
        # Response cache
        if "response_cache" not in st.session_state:
            st.session_state.response_cache = {}
    
    def _rate_limit(self):
        """Implement basic rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _get_cache_key(self, prompt: str, **kwargs) -> str:
        """Generate cache key for response caching"""
        cache_data = {"prompt": prompt, **kwargs}
        return str(hash(json.dumps(cache_data, sort_keys=True)))
    
    def generate_content(
        self, 
        prompt: str, 
        use_cache: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate content with caching and rate limiting"""
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(prompt, temperature=temperature, max_tokens=max_tokens)
            if cache_key in st.session_state.response_cache:
                return st.session_state.response_cache[cache_key]
        
        # Rate limiting
        self._rate_limit()
        
        try:
            # Configure generation settings
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                **kwargs
            )
            
            result = response.text
            
            # Cache the response
            if use_cache:
                st.session_state.response_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            error_msg = f"Error generating content: {str(e)}"
            st.error(error_msg)
            return error_msg
    
    def analyze_image(
        self, 
        image, 
        prompt: str = "Analyze this image",
        use_cache: bool = False  # Images typically shouldn't be cached
    ) -> str:
        """Analyze image with Gemini Vision"""
        self._rate_limit()
        
        try:
            response = self.model.generate_content([prompt, image])
            return response.text
            
        except Exception as e:
            error_msg = f"Error analyzing image: {str(e)}"
            st.error(error_msg)
            return error_msg
    
    def clear_cache(self):
        """Clear response cache"""
        st.session_state.response_cache = {}
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(st.session_state.response_cache),
            "model_name": self.model_name,
            "last_request": datetime.fromtimestamp(self.last_request_time).isoformat() if self.last_request_time > 0 else "Never"
        }

class ConversationManager:
    """Manage conversation history and context"""
    
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        if "conversations" not in st.session_state:
            st.session_state.conversations = {}
    
    def add_message(self, conversation_id: str, role: str, content: str, metadata: Dict = None):
        """Add message to conversation"""
        if conversation_id not in st.session_state.conversations:
            st.session_state.conversations[conversation_id] = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        st.session_state.conversations[conversation_id].append(message)
        
        # Limit history size
        if len(st.session_state.conversations[conversation_id]) > self.max_history:
            st.session_state.conversations[conversation_id] = \
                st.session_state.conversations[conversation_id][-self.max_history:]
    
    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """Get conversation history"""
        return st.session_state.conversations.get(conversation_id, [])
    
    def get_conversation_context(self, conversation_id: str, max_messages: int = 10) -> str:
        """Get formatted conversation context"""
        messages = self.get_conversation(conversation_id)[-max_messages:]
        
        context = ""
        for msg in messages:
            context += f"{msg['role'].title()}: {msg['content']}\n"
        
        return context
    
    def clear_conversation(self, conversation_id: str):
        """Clear specific conversation"""
        if conversation_id in st.session_state.conversations:
            del st.session_state.conversations[conversation_id]
    
    def export_conversation(self, conversation_id: str) -> str:
        """Export conversation as JSON"""
        conversation = self.get_conversation(conversation_id)
        export_data = {
            "conversation_id": conversation_id,
            "exported_at": datetime.now().isoformat(),
            "message_count": len(conversation),
            "messages": conversation
        }
        return json.dumps(export_data, indent=2)

class FileProcessor:
    """Process various file types for AI analysis"""
    
    @staticmethod
    def process_text_file(file) -> str:
        """Process text file"""
        try:
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            return content
        except Exception as e:
            return f"Error reading file: {e}"
    
    @staticmethod
    def process_pdf(file) -> str:
        """Process PDF file (placeholder - would need PyPDF2 or similar)"""
        try:
            # This would require additional dependencies
            return "PDF processing not implemented yet. Please convert to text file."
        except Exception as e:
            return f"Error processing PDF: {e}"
    
    @staticmethod
    def get_file_info(file) -> Dict[str, Any]:
        """Get file information"""
        return {
            "name": file.name,
            "size": file.size,
            "type": file.type,
            "timestamp": datetime.now().isoformat()
        }

# Custom exceptions
class GeminiError(Exception):
    """Custom exception for Gemini-related errors"""
    pass

class RateLimitError(GeminiError):
    """Exception for rate limiting issues"""
    pass

# Utility functions
def format_response(text: str, max_length: int = None) -> str:
    """Format AI response text"""
    if max_length and len(text) > max_length:
        return text[:max_length] + "..."
    return text

def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks from text"""
    import re
    
    code_pattern = r'```(\w+)?\n(.*?)\n```'
    matches = re.findall(code_pattern, text, re.DOTALL)
    
    code_blocks = []
    for match in matches:
        language = match[0] if match[0] else "text"
        code = match[1]
        code_blocks.append({"language": language, "code": code})
    
    return code_blocks

def validate_api_key() -> bool:
    """Validate if API key is properly set"""
    api_key = os.getenv("GOOGLE_API_KEY")
    return api_key is not None and len(api_key) > 10