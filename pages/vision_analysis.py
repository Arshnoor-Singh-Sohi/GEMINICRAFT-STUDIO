import streamlit as st
import google.generativeai as genai
import os
from PIL import Image, ImageEnhance
import io
import base64
from datetime import datetime
import json

# Import database utilities
try:
    from utils.database import track_tool_usage
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class VisionAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro")
    
    def analyze_image(self, image, prompt="Analyze this image in detail"):
        """Analyze image with custom prompt"""
        try:
            # Convert PIL image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Prepare the content
            response = self.model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
    
    def extract_text(self, image):
        """Extract text from image (OCR)"""
        prompt = "Extract all text from this image. Provide the text exactly as it appears, maintaining formatting and structure."
        return self.analyze_image(image, prompt)
    
    def identify_objects(self, image):
        """Identify objects in the image"""
        prompt = "Identify and list all objects, people, animals, and items visible in this image. Provide detailed descriptions of their positions and characteristics."
        return self.analyze_image(image, prompt)
    
    def analyze_composition(self, image):
        """Analyze artistic composition"""
        prompt = "Analyze this image's artistic composition including: lighting, color palette, composition rules (rule of thirds, leading lines, etc.), mood, and visual appeal. Provide professional photography insights."
        return self.analyze_image(image, prompt)
    
    def generate_caption(self, image):
        """Generate descriptive caption"""
        prompt = "Generate a detailed, engaging caption for this image suitable for social media. Make it descriptive but concise."
        return self.analyze_image(image, prompt)

def load_vision_page():
    st.markdown("# 👁️ Vision & Image Analysis")
    st.markdown("*Advanced AI-powered image understanding and analysis*")
    
    # Initialize session state
    if "vision_analyzer" not in st.session_state:
        st.session_state.vision_analyzer = VisionAnalyzer()
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### 🎛️ Vision Controls")
        
        # Analysis type
        analysis_type = st.selectbox(
            "🔍 Analysis Type:",
            [
                "General Analysis",
                "Text Extraction (OCR)",
                "Object Detection",
                "Artistic Composition",
                "Caption Generation",
                "Custom Analysis",
                "Chat with Image"
            ]
        )
        
        # Image enhancement options
        st.markdown("### 🖼️ Image Enhancement")
        enhance_image = st.checkbox("Enable enhancements")
        
        if enhance_image:
            brightness = st.slider("☀️ Brightness", 0.5, 2.0, 1.0, 0.1)
            contrast = st.slider("🌓 Contrast", 0.5, 2.0, 1.0, 0.1)
            sharpness = st.slider("🔍 Sharpness", 0.5, 2.0, 1.0, 0.1)
        
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
                    file_name=f"vision_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 Upload Image")
        
        # Multiple upload options
        upload_option = st.radio(
            "Choose upload method:",
            ["File Upload", "Camera Capture", "URL"]
        )
        
        uploaded_image = None
        
        if upload_option == "File Upload":
            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=["jpg", "jpeg", "png", "bmp", "gif", "webp"],
                accept_multiple_files=False
            )
            if uploaded_file:
                uploaded_image = Image.open(uploaded_file)
        
        elif upload_option == "Camera Capture":
            camera_image = st.camera_input("Take a picture")
            if camera_image:
                uploaded_image = Image.open(camera_image)
        
        elif upload_option == "URL":
            image_url = st.text_input("Enter image URL:")
            if image_url and st.button("Load Image"):
                try:
                    import requests
                    response = requests.get(image_url)
                    uploaded_image = Image.open(io.BytesIO(response.content))
                except Exception as e:
                    st.error(f"Error loading image: {e}")
        
        # Display and enhance image
        if uploaded_image:
            # Apply enhancements if enabled
            display_image = uploaded_image.copy()
            if enhance_image:
                enhancer = ImageEnhance.Brightness(display_image)
                display_image = enhancer.enhance(brightness)
                
                enhancer = ImageEnhance.Contrast(display_image)
                display_image = enhancer.enhance(contrast)
                
                enhancer = ImageEnhance.Sharpness(display_image)
                display_image = enhancer.enhance(sharpness)
            
            st.image(display_image, caption="Uploaded Image", use_column_width=True)
            
            # Image info
            st.markdown("**📋 Image Info:**")
            st.write(f"• **Size:** {uploaded_image.size[0]} x {uploaded_image.size[1]} pixels")
            st.write(f"• **Mode:** {uploaded_image.mode}")
            st.write(f"• **Format:** {getattr(uploaded_image, 'format', 'Unknown')}")
    
    with col2:
        st.markdown("### 🔍 Analysis Results")
        
        if uploaded_image:
            # Custom prompt for custom analysis
            if analysis_type == "Custom Analysis":
                custom_prompt = st.text_area(
                    "Enter your analysis prompt:",
                    placeholder="Describe what you want to analyze about this image...",
                    height=100
                )
            else:
                custom_prompt = None
            
            # Analyze button (not shown for chat mode)
            if analysis_type != "Chat with Image" and st.button("🚀 Analyze Image", type="primary", use_container_width=True):
                # Track usage
                if DB_AVAILABLE:
                    track_tool_usage("vision_analysis", f"analysis_{analysis_type.lower().replace(' ', '_')}")
                
                with st.spinner("🔍 Analyzing image..."):
                    # Choose analysis method
                    if analysis_type == "General Analysis":
                        result = st.session_state.vision_analyzer.analyze_image(
                            display_image if enhance_image else uploaded_image
                        )
                    elif analysis_type == "Text Extraction (OCR)":
                        result = st.session_state.vision_analyzer.extract_text(
                            display_image if enhance_image else uploaded_image
                        )
                    elif analysis_type == "Object Detection":
                        result = st.session_state.vision_analyzer.identify_objects(
                            display_image if enhance_image else uploaded_image
                        )
                    elif analysis_type == "Artistic Composition":
                        result = st.session_state.vision_analyzer.analyze_composition(
                            display_image if enhance_image else uploaded_image
                        )
                    elif analysis_type == "Caption Generation":
                        result = st.session_state.vision_analyzer.generate_caption(
                            display_image if enhance_image else uploaded_image
                        )
                    elif analysis_type == "Custom Analysis" and custom_prompt:
                        result = st.session_state.vision_analyzer.analyze_image(
                            display_image if enhance_image else uploaded_image,
                            custom_prompt
                        )
                    else:
                        result = "Please provide a custom prompt for analysis."
                
                # Display result
                st.markdown("**🎯 Analysis Result:**")
                st.write(result)
                
                # Save to history
                analysis_record = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "analysis_type": analysis_type,
                    "custom_prompt": custom_prompt,
                    "result": result,
                    "image_size": uploaded_image.size,
                    "enhanced": enhance_image
                }
                st.session_state.analysis_history.append(analysis_record)
                
                # Action buttons
                col_copy, col_save = st.columns(2)
                with col_copy:
                    if st.button("📋 Copy Result"):
                        st.success("Result copied!")
                
                with col_save:
                    st.download_button(
                        label="💾 Save Analysis",
                        data=json.dumps(analysis_record, indent=2),
                        file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        else:
            st.info("👆 Upload an image to start analysis")
            
            # Example analyses
            st.markdown("**🌟 What you can analyze:**")
            examples = [
                "📝 **Text Extraction:** Extract text from documents, signs, handwriting",
                "🎯 **Object Detection:** Identify people, objects, animals, landmarks",
                "🎨 **Artistic Analysis:** Composition, lighting, color theory insights",
                "📱 **Social Media:** Generate engaging captions and descriptions",
                "🔍 **Custom Analysis:** Ask specific questions about any image"
            ]
            for example in examples:
                st.markdown(f"• {example}")
    
    # Analysis History
    if st.session_state.analysis_history:
        st.markdown("---")
        st.markdown("## 📚 Analysis History")
        
        for i, record in enumerate(reversed(st.session_state.analysis_history[-5:])):  # Show last 5
            with st.expander(f"📊 {record['analysis_type']} - {record['timestamp']}"):
                if record.get('custom_prompt'):
                    st.markdown(f"**Prompt:** {record['custom_prompt']}")
                st.markdown(f"**Result:**\n{record['result']}")
                st.caption(f"Image: {record['image_size'][0]}x{record['image_size'][1]} | Enhanced: {record['enhanced']}")

# This would be called from the main app
if __name__ == "__main__":
    load_vision_page()