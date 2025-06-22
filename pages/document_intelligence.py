import streamlit as st
import google.generativeai as genai
import os
import json
import io
from datetime import datetime
from typing import List, Dict, Optional
import base64

# Import database utilities
try:
    from utils.database import track_tool_usage
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class DocumentIntelligence:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro")
        self.supported_formats = [".txt", ".pdf", ".docx", ".md"]
    
    def analyze_document(self, content: str, analysis_type: str) -> str:
        """Analyze document content"""
        
        prompts = {
            "Summary": f"""
            Provide a comprehensive summary of this document:
            
            {content}
            
            Include:
            - Main topics and themes
            - Key points and arguments
            - Important details and facts
            - Overall structure and organization
            - Target audience and purpose
            """,
            
            "Key Points": f"""
            Extract and list the key points from this document:
            
            {content}
            
            Format as:
            - Bullet points for easy reading
            - Prioritize by importance
            - Include supporting details where relevant
            - Group related points together
            """,
            
            "Q&A Generation": f"""
            Generate comprehensive Q&A pairs based on this document:
            
            {content}
            
            Create:
            - 10-15 relevant questions and answers
            - Mix of factual, analytical, and conceptual questions
            - Questions that test understanding of key concepts
            - Answers that are complete and accurate
            """,
            
            "Critical Analysis": f"""
            Provide a critical analysis of this document:
            
            {content}
            
            Analyze:
            - Strengths and weaknesses of arguments
            - Evidence quality and credibility
            - Logical consistency and flow
            - Potential biases or gaps
            - Overall effectiveness and impact
            """,
            
            "Citation Format": f"""
            Generate proper citations for this document content:
            
            {content}
            
            Provide citations in multiple formats:
            - APA style
            - MLA style  
            - Chicago style
            - IEEE style (if applicable)
            - Include guidance on reference formatting
            """
        }
        
        prompt = prompts.get(analysis_type, prompts["Summary"])
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error analyzing document: {str(e)}"
    
    def answer_question(self, content: str, question: str) -> str:
        """Answer specific questions about the document"""
        
        prompt = f"""
        Based on this document content, answer the following question accurately and comprehensively:
        
        Document:
        {content}
        
        Question: {question}
        
        Instructions:
        - Provide a direct and complete answer
        - Use specific information from the document
        - Quote relevant passages when helpful
        - If the answer isn't in the document, clearly state that
        - Explain your reasoning
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error answering question: {str(e)}"
    
    def extract_entities(self, content: str) -> str:
        """Extract key entities from document"""
        
        prompt = f"""
        Extract and categorize key entities from this document:
        
        {content}
        
        Categories to extract:
        - People (names, roles, titles)
        - Organizations (companies, institutions)
        - Locations (cities, countries, addresses)
        - Dates and times
        - Numbers and statistics
        - Technical terms and concepts
        - Products and services
        - Events and processes
        
        Format the results clearly with categories and bullet points.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error extracting entities: {str(e)}"
    
    def compare_documents(self, doc1: str, doc2: str) -> str:
        """Compare two documents"""
        
        prompt = f"""
        Compare and contrast these two documents:
        
        Document 1:
        {doc1}
        
        Document 2:
        {doc2}
        
        Provide analysis on:
        - Similarities in content and themes
        - Key differences and contrasts
        - Complementary information
        - Conflicting viewpoints
        - Relative strengths and weaknesses
        - Synthesis and integration opportunities
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error comparing documents: {str(e)}"
    
    def translate_document(self, content: str, target_language: str) -> str:
        """Translate document to target language"""
        
        prompt = f"""
        Translate this document to {target_language}, maintaining the original structure, tone, and meaning:
        
        {content}
        
        Requirements:
        - Preserve formatting and structure
        - Maintain professional tone
        - Ensure cultural appropriateness
        - Keep technical terms accurate
        - Provide natural, fluent translation
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error translating document: {str(e)}"

def process_uploaded_file(uploaded_file) -> str:
    """Process uploaded file and extract text content"""
    
    try:
        if uploaded_file.type == "text/plain":
            return str(uploaded_file.read(), "utf-8")
        
        elif uploaded_file.type == "application/pdf":
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
                
                if len(text_content.strip()) < 10:
                    return "PDF appears to be empty or contains only images. Please use a text-based PDF."
                
                return text_content
            except ImportError:
                return "PDF processing requires PyPDF2. Please install: pip install PyPDF2"
            except Exception as e:
                return f"Error processing PDF: {str(e)}"
        
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            try:
                from docx import Document
                doc = Document(uploaded_file)
                text_content = ""
                for paragraph in doc.paragraphs:
                    text_content += paragraph.text + "\n"
                
                if len(text_content.strip()) < 10:
                    return "DOCX appears to be empty or contains only images. Please check the document content."
                
                return text_content
            except ImportError:
                return "DOCX processing requires python-docx. Please install: pip install python-docx"
            except Exception as e:
                return f"Error processing DOCX: {str(e)}"
        
        else:
            # Try to read as text
            content = uploaded_file.read()
            if isinstance(content, bytes):
                return content.decode('utf-8')
            return str(content)
    
    except Exception as e:
        return f"Error processing file: {str(e)}"

def load_document_intelligence_page():
    st.markdown("# 📄 Document Intelligence")
    st.markdown("*AI-powered document analysis, Q&A, and processing platform*")
    
    # Initialize session state
    if "doc_intelligence" not in st.session_state:
        st.session_state.doc_intelligence = DocumentIntelligence()
    if "document_history" not in st.session_state:
        st.session_state.document_history = []
    if "current_document" not in st.session_state:
        st.session_state.current_document = None
    if "document_content" not in st.session_state:
        st.session_state.document_content = ""
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### 🎛️ Document Controls")
        
        # Analysis type
        analysis_type = st.selectbox(
            "🔍 Analysis Type:",
            [
                "Summary",
                "Key Points",
                "Q&A Generation", 
                "Critical Analysis",
                "Entity Extraction",
                "Citation Format",
                "Document Q&A",
                "Translation"
            ]
        )
        
        # Language for translation
        if analysis_type == "Translation":
            target_language = st.selectbox(
                "🌍 Target Language:",
                [
                    "Spanish", "French", "German", "Italian", "Portuguese",
                    "Chinese", "Japanese", "Korean", "Arabic", "Russian",
                    "Dutch", "Swedish", "Norwegian", "Finnish"
                ]
            )
        
        st.markdown("---")
        
        # Document comparison
        st.markdown("### 📊 Document Comparison")
        enable_comparison = st.checkbox("Compare two documents")
        
        st.markdown("---")
        
        # Quick templates
        st.markdown("### ⚡ Sample Documents")
        
        sample_docs = {
            "Research Paper": """
            Abstract: This study examines the impact of artificial intelligence on modern workplace productivity.
            
            Introduction: The integration of AI technologies in corporate environments has accelerated significantly in recent years...
            
            Methodology: We conducted a comprehensive analysis of 500 companies across various industries...
            
            Results: Our findings indicate a 35% increase in productivity among companies that implemented AI solutions...
            
            Conclusion: AI adoption presents significant opportunities for workplace enhancement while requiring careful consideration of ethical implications.
            """,
            
            "Business Report": """
            Executive Summary: Q3 2024 Financial Performance Report
            
            Key Highlights:
            - Revenue increased 15% year-over-year to $2.3M
            - Customer acquisition grew by 28%
            - Operating expenses reduced by 8%
            
            Market Analysis: The technology sector showed strong growth with emerging trends in cloud computing and AI...
            
            Recommendations: Continue investment in R&D, expand into international markets, focus on customer retention strategies.
            """,
            
            "Legal Document": """
            Service Agreement
            
            This agreement is entered into between Company A and Company B for the provision of consulting services...
            
            Terms and Conditions:
            1. Scope of work includes strategic planning and implementation
            2. Duration of contract is 12 months
            3. Payment terms are net 30 days
            
            Obligations: Both parties agree to maintain confidentiality and provide necessary resources...
            """
        }
        
        for doc_name, doc_content in sample_docs.items():
            if st.button(f"📄 {doc_name}", use_container_width=True):
                st.session_state.document_content = doc_content
                st.session_state.current_document = doc_name
                st.success(f"Loaded {doc_name}")
        
        st.markdown("---")
        
        # History management
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.document_history = []
            st.rerun()
        
        if st.session_state.document_history:
            if st.button("💾 Export History", use_container_width=True):
                history_data = {
                    "timestamp": datetime.now().isoformat(),
                    "analyses": st.session_state.document_history
                }
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(history_data, indent=2),
                    file_name=f"document_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📂 Document Input")
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["File Upload", "Text Input", "URL Input"]
        )
        
        if input_method == "File Upload":
            uploaded_file = st.file_uploader(
                "Upload document",
                type=["txt", "pdf", "docx", "md"],
                help="Supported formats: TXT, PDF, DOCX, MD"
            )
            
            if uploaded_file:
                content = process_uploaded_file(uploaded_file)
                st.session_state.document_content = content
                st.session_state.current_document = uploaded_file.name
                
                if len(content.strip()) > 20 and not content.startswith("Error") and not content.startswith("PDF processing") and not content.startswith("DOCX processing"):  # More reasonable minimum length
                    st.success(f"Document loaded: {len(content)} characters")
                elif content.startswith("Error") or content.startswith("PDF processing") or content.startswith("DOCX processing"):
                    st.error(content)
                else:
                    st.warning("Document seems too short or failed to load properly")
                    st.info("Try uploading a text file or check if the document contains readable text.")
        
        elif input_method == "Text Input":
            content = st.text_area(
                "Paste document content:",
                placeholder="Paste your document content here...",
                height=300,
                value=st.session_state.document_content
            )
            
            if content:
                st.session_state.document_content = content
                st.session_state.current_document = "Text Input"
        
        elif input_method == "URL Input":
            url = st.text_input("Enter document URL:")
            if url and st.button("Load from URL"):
                st.warning("URL loading not implemented. Please use file upload or text input.")
        
        # Document preview
        if st.session_state.document_content and not st.session_state.document_content.startswith("Error") and not st.session_state.document_content.startswith("PDF processing") and not st.session_state.document_content.startswith("DOCX processing"):
            st.markdown("### 👀 Document Preview")
            preview_length = min(500, len(st.session_state.document_content))
            st.text_area(
                f"First {preview_length} characters:",
                value=st.session_state.document_content[:preview_length],
                height=150,
                disabled=True
            )
            
            # Document stats
            word_count = len(st.session_state.document_content.split())
            char_count = len(st.session_state.document_content)
            
            stat_col1, stat_col2 = st.columns(2)
            with stat_col1:
                st.metric("Words", f"{word_count:,}")
            with stat_col2:
                st.metric("Characters", f"{char_count:,}")
        
        # Second document for comparison
        if enable_comparison:
            st.markdown("### 📄 Second Document")
            second_doc = st.text_area(
                "Paste second document for comparison:",
                placeholder="Paste the second document content here...",
                height=200,
                key="second_document"
            )
            st.session_state.second_document = second_doc
    
    with col2:
        st.markdown("### 🧠 AI Analysis")
        
        if st.session_state.document_content:
            
            # Q&A section for Document Q&A
            if analysis_type == "Document Q&A":
                question = st.text_input(
                    "Ask a question about the document:",
                    placeholder="What is the main topic of this document?"
                )
                
                if st.button("🤔 Ask Question", type="primary", use_container_width=True):
                    if question:
                        # Track usage
                        if DB_AVAILABLE:
                            track_tool_usage("document_intelligence", "question_asked")
                        
                        with st.spinner("🔍 Finding answer..."):
                            answer = st.session_state.doc_intelligence.answer_question(
                                st.session_state.document_content, question
                            )
                            st.session_state.current_answer = answer
                            
                            # Save Q&A to history
                            qa_record = {
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "document": st.session_state.current_document,
                                "question": question,
                                "answer": answer,
                                "type": "Q&A"
                            }
                            st.session_state.document_history.append(qa_record)
                            st.rerun()
                    else:
                        st.error("Please enter a question.")
            
            # Regular analysis
            else:
                if st.button("🚀 Analyze Document", type="primary", use_container_width=True):
                    # Track usage
                    if DB_AVAILABLE:
                        track_tool_usage("document_intelligence", f"analysis_{analysis_type.lower().replace(' ', '_')}")
                    
                    with st.spinner(f"🔍 Performing {analysis_type}..."):
                        
                        if analysis_type == "Translation":
                            result = st.session_state.doc_intelligence.translate_document(
                                st.session_state.document_content, target_language
                            )
                        elif analysis_type == "Entity Extraction":
                            result = st.session_state.doc_intelligence.extract_entities(
                                st.session_state.document_content
                            )
                        elif enable_comparison and st.session_state.get("second_document"):
                            result = st.session_state.doc_intelligence.compare_documents(
                                st.session_state.document_content,
                                st.session_state.second_document
                            )
                        else:
                            result = st.session_state.doc_intelligence.analyze_document(
                                st.session_state.document_content, analysis_type
                            )
                        
                        st.session_state.current_analysis = result
                        
                        # Save to history
                        history_record = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "document": st.session_state.current_document,
                            "analysis_type": analysis_type,
                            "word_count": len(st.session_state.document_content.split()),
                            "result": result
                        }
                        st.session_state.document_history.append(history_record)
                        
                        st.rerun()
            
            # Display results
            if "current_analysis" in st.session_state:
                st.markdown("**🎯 Analysis Results:**")
                st.write(st.session_state.current_analysis)
                
                # Action buttons
                col_copy, col_save = st.columns(2)
                with col_copy:
                    if st.button("📋 Copy Results"):
                        st.success("Results copied!")
                
                with col_save:
                    st.download_button(
                        label="💾 Save Analysis",
                        data=st.session_state.current_analysis,
                        file_name=f"document_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
            
            # Display Q&A answer
            if "current_answer" in st.session_state:
                st.markdown("**💬 Answer:**")
                st.write(st.session_state.current_answer)
                
                st.download_button(
                    label="💾 Save Q&A",
                    data=f"Q: {question if 'question' in locals() else 'Question'}\nA: {st.session_state.current_answer}",
                    file_name=f"document_qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
        
        else:
            st.info("👈 Upload or input a document to begin analysis")
            
            # Analysis capabilities
            st.markdown("**🎯 Analysis Capabilities:**")
            capabilities = [
                "📝 **Summarization:** Comprehensive document summaries",
                "🔑 **Key Points:** Extract main ideas and important details",
                "❓ **Q&A Generation:** Create study questions and answers",
                "🔍 **Critical Analysis:** Evaluate arguments and evidence",
                "🏷️ **Entity Extraction:** Identify people, places, organizations",
                "📚 **Citations:** Generate proper academic references",
                "💬 **Document Q&A:** Ask specific questions about content",
                "🌍 **Translation:** Convert to multiple languages"
            ]
            for capability in capabilities:
                st.markdown(f"• {capability}")
    
    # Quick Actions
    st.markdown("---")
    st.markdown("## ⚡ Quick Actions")
    
    if st.session_state.document_content and not st.session_state.document_content.startswith(("Error", "PDF processing", "DOCX processing")):
        quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
        
        with quick_col1:
            if st.button("📝 Quick Summary", use_container_width=True):
                with st.spinner("Generating summary..."):
                    summary = st.session_state.doc_intelligence.analyze_document(
                        st.session_state.document_content, "Summary"
                    )
                    st.write(summary)
        
        with quick_col2:
            if st.button("🔑 Key Points", use_container_width=True):
                with st.spinner("Extracting key points..."):
                    points = st.session_state.doc_intelligence.analyze_document(
                        st.session_state.document_content, "Key Points"
                    )
                    st.write(points)
        
        with quick_col3:
            if st.button("🏷️ Extract Entities", use_container_width=True):
                with st.spinner("Extracting entities..."):
                    entities = st.session_state.doc_intelligence.extract_entities(
                        st.session_state.document_content
                    )
                    st.write(entities)
        
        with quick_col4:
            if st.button("❓ Generate Q&A", use_container_width=True):
                with st.spinner("Generating Q&A..."):
                    qa = st.session_state.doc_intelligence.analyze_document(
                        st.session_state.document_content, "Q&A Generation"
                    )
                    st.write(qa)
    
    # Document History
    if st.session_state.document_history:
        st.markdown("---")
        st.markdown("## 📚 Document History")
        
        for i, record in enumerate(reversed(st.session_state.document_history[-5:])):  # Show last 5
            record_type = record.get("type", "Analysis")
            if record_type == "Q&A":
                with st.expander(f"💬 Q&A - {record['document']} - {record['timestamp']}"):
                    st.markdown(f"**Question:** {record['question']}")
                    st.markdown(f"**Answer:** {record['answer']}")
            else:
                with st.expander(f"📄 {record['analysis_type']} - {record['document']} - {record['timestamp']}"):
                    st.markdown(f"**Document:** {record['document']} ({record['word_count']} words)")
                    st.markdown(f"**Analysis:**")
                    st.write(record['result'][:800] + "..." if len(record['result']) > 800 else record['result'])
            
            # Quick actions for history items
            hist_col1, hist_col2 = st.columns(2)
            with hist_col1:
                if st.button(f"📋 Copy", key=f"hist_copy_{i}"):
                    st.success("Copied!")
            with hist_col2:
                content_to_save = record.get('result', '') or f"Q: {record.get('question', '')}\nA: {record.get('answer', '')}"
                st.download_button(
                    label="💾 Download",
                    data=content_to_save,
                    file_name=f"document_{i}.md",
                    mime="text/markdown",
                    key=f"hist_download_{i}"
                )

# This would be called from the main app
if __name__ == "__main__":
    load_document_intelligence_page()