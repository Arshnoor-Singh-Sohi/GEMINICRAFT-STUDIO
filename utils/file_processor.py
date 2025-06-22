import streamlit as st
import pandas as pd
import json
import io
import base64
import hashlib
from PIL import Image
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import os

class FileProcessor:
    """Advanced file processing utilities for GeminiCraft Studio"""
    
    def __init__(self):
        self.supported_formats = {
            'text': ['.txt', '.md', '.rtf'],
            'data': ['.csv', '.xlsx', '.xls', '.json'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            'document': ['.pdf', '.docx', '.doc'],
            'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.go', '.rs']
        }
        
        self.max_file_size = 50 * 1024 * 1024  # 50MB default
        
    def get_file_type(self, filename: str) -> str:
        """Determine file type category"""
        ext = os.path.splitext(filename.lower())[1]
        
        for category, extensions in self.supported_formats.items():
            if ext in extensions:
                return category
        
        return 'unknown'
    
    def validate_file(self, uploaded_file) -> Dict[str, Any]:
        """Validate uploaded file"""
        if uploaded_file is None:
            return {"valid": False, "error": "No file uploaded"}
        
        # Check file size
        if uploaded_file.size > self.max_file_size:
            return {
                "valid": False, 
                "error": f"File too large. Maximum size: {self.max_file_size / 1024 / 1024:.1f}MB"
            }
        
        # Check file type
        file_type = self.get_file_type(uploaded_file.name)
        if file_type == 'unknown':
            return {
                "valid": False,
                "error": f"Unsupported file type: {os.path.splitext(uploaded_file.name)[1]}"
            }
        
        return {
            "valid": True,
            "file_type": file_type,
            "filename": uploaded_file.name,
            "size": uploaded_file.size,
            "mime_type": uploaded_file.type
        }
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    def process_text_file(self, uploaded_file) -> Dict[str, Any]:
        """Process text files"""
        try:
            # Read content
            content = uploaded_file.read()
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
            text_content = None
            
            for encoding in encodings:
                try:
                    if isinstance(content, bytes):
                        text_content = content.decode(encoding)
                    else:
                        text_content = str(content)
                    break
                except UnicodeDecodeError:
                    continue
            
            if text_content is None:
                return {"success": False, "error": "Could not decode file content"}
            
            # Calculate statistics
            word_count = len(text_content.split())
            char_count = len(text_content)
            line_count = len(text_content.splitlines())
            
            return {
                "success": True,
                "content": text_content,
                "stats": {
                    "words": word_count,
                    "characters": char_count,
                    "lines": line_count
                },
                "file_hash": self.calculate_file_hash(content if isinstance(content, bytes) else content.encode())
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_image_file(self, uploaded_file) -> Dict[str, Any]:
        """Process image files"""
        try:
            # Read image
            image = Image.open(uploaded_file)
            
            # Get image info
            image_info = {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height
            }
            
            # Calculate file hash
            uploaded_file.seek(0)
            file_content = uploaded_file.read()
            file_hash = self.calculate_file_hash(file_content)
            
            # Convert to base64 for storage
            uploaded_file.seek(0)
            image_base64 = base64.b64encode(file_content).decode()
            
            return {
                "success": True,
                "image": image,
                "image_info": image_info,
                "image_base64": image_base64,
                "file_hash": file_hash
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_data_file(self, uploaded_file) -> Dict[str, Any]:
        """Process data files (CSV, Excel, JSON)"""
        try:
            file_ext = os.path.splitext(uploaded_file.name.lower())[1]
            
            if file_ext == '.csv':
                return self._process_csv(uploaded_file)
            elif file_ext in ['.xlsx', '.xls']:
                return self._process_excel(uploaded_file)
            elif file_ext == '.json':
                return self._process_json(uploaded_file)
            else:
                return {"success": False, "error": f"Unsupported data format: {file_ext}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _process_csv(self, uploaded_file) -> Dict[str, Any]:
        """Process CSV files"""
        try:
            # Try different delimiters and encodings
            delimiters = [',', ';', '\t', '|']
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            df = None
            used_delimiter = None
            used_encoding = None
            
            for encoding in encodings:
                for delimiter in delimiters:
                    try:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding=encoding)
                        
                        # Check if parsing was successful (more than 1 column usually indicates success)
                        if len(df.columns) > 1 or len(df) > 0:
                            used_delimiter = delimiter
                            used_encoding = encoding
                            break
                    except:
                        continue
                
                if df is not None:
                    break
            
            if df is None:
                return {"success": False, "error": "Could not parse CSV file"}
            
            # Calculate statistics
            stats = {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "data_types": dict(df.dtypes.astype(str)),
                "missing_values": dict(df.isnull().sum()),
                "delimiter_used": used_delimiter,
                "encoding_used": used_encoding
            }
            
            # Get sample data
            sample_data = df.head(10).to_dict('records')
            
            return {
                "success": True,
                "dataframe": df,
                "stats": stats,
                "sample_data": sample_data,
                "preview": df.head().to_html()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _process_excel(self, uploaded_file) -> Dict[str, Any]:
        """Process Excel files"""
        try:
            # Read all sheets
            xl_file = pd.ExcelFile(uploaded_file)
            sheets_data = {}
            
            for sheet_name in xl_file.sheet_names:
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                
                sheets_data[sheet_name] = {
                    "dataframe": df,
                    "stats": {
                        "rows": len(df),
                        "columns": len(df.columns),
                        "column_names": list(df.columns),
                        "data_types": dict(df.dtypes.astype(str)),
                        "missing_values": dict(df.isnull().sum())
                    },
                    "sample_data": df.head(10).to_dict('records'),
                    "preview": df.head().to_html()
                }
            
            # Use first sheet as primary
            primary_sheet = list(sheets_data.keys())[0]
            primary_data = sheets_data[primary_sheet]
            
            return {
                "success": True,
                "dataframe": primary_data["dataframe"],
                "stats": primary_data["stats"],
                "sample_data": primary_data["sample_data"],
                "preview": primary_data["preview"],
                "all_sheets": sheets_data,
                "sheet_names": xl_file.sheet_names
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _process_json(self, uploaded_file) -> Dict[str, Any]:
        """Process JSON files"""
        try:
            content = uploaded_file.read()
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            json_data = None
            
            for encoding in encodings:
                try:
                    if isinstance(content, bytes):
                        text_content = content.decode(encoding)
                    else:
                        text_content = str(content)
                    
                    json_data = json.loads(text_content)
                    break
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
            
            if json_data is None:
                return {"success": False, "error": "Could not parse JSON file"}
            
            # Try to convert to DataFrame if possible
            df = None
            try:
                if isinstance(json_data, list) and len(json_data) > 0:
                    df = pd.DataFrame(json_data)
                elif isinstance(json_data, dict):
                    # Try different approaches
                    if all(isinstance(v, (list, dict)) for v in json_data.values()):
                        df = pd.DataFrame(json_data)
                    else:
                        df = pd.DataFrame([json_data])
            except:
                pass
            
            result = {
                "success": True,
                "json_data": json_data,
                "data_type": type(json_data).__name__,
                "size": len(json_data) if hasattr(json_data, '__len__') else 1
            }
            
            if df is not None:
                result.update({
                    "dataframe": df,
                    "stats": {
                        "rows": len(df),
                        "columns": len(df.columns),
                        "column_names": list(df.columns),
                        "data_types": dict(df.dtypes.astype(str))
                    },
                    "preview": df.head().to_html()
                })
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_code_file(self, uploaded_file) -> Dict[str, Any]:
        """Process code files"""
        try:
            # Read content
            content = uploaded_file.read()
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
            code_content = None
            
            for encoding in encodings:
                try:
                    if isinstance(content, bytes):
                        code_content = content.decode(encoding)
                    else:
                        code_content = str(content)
                    break
                except UnicodeDecodeError:
                    continue
            
            if code_content is None:
                return {"success": False, "error": "Could not decode file content"}
            
            # Detect language from extension
            ext = os.path.splitext(uploaded_file.name.lower())[1]
            language_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.html': 'html',
                '.css': 'css',
                '.java': 'java',
                '.cpp': 'cpp',
                '.c': 'c',
                '.go': 'go',
                '.rs': 'rust'
            }
            
            language = language_map.get(ext, 'text')
            
            # Calculate statistics
            lines = code_content.splitlines()
            non_empty_lines = [line for line in lines if line.strip()]
            comment_indicators = ['#', '//', '/*', '*', '<!--']
            comment_lines = [line for line in lines if any(line.strip().startswith(indicator) for indicator in comment_indicators)]
            
            stats = {
                "total_lines": len(lines),
                "non_empty_lines": len(non_empty_lines),
                "comment_lines": len(comment_lines),
                "characters": len(code_content),
                "language": language
            }
            
            return {
                "success": True,
                "content": code_content,
                "language": language,
                "stats": stats,
                "file_hash": self.calculate_file_hash(content if isinstance(content, bytes) else content.encode())
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_file(self, uploaded_file) -> Dict[str, Any]:
        """Main file processing function"""
        # Validate file
        validation = self.validate_file(uploaded_file)
        if not validation["valid"]:
            return validation
        
        file_type = validation["file_type"]
        
        # Process based on file type
        if file_type == 'text':
            return self.process_text_file(uploaded_file)
        elif file_type == 'image':
            return self.process_image_file(uploaded_file)
        elif file_type == 'data':
            return self.process_data_file(uploaded_file)
        elif file_type == 'code':
            return self.process_code_file(uploaded_file)
        elif file_type == 'document':
            # For now, suggest conversion to text
            return {
                "success": False,
                "error": "Document processing not fully implemented. Please convert to text format."
            }
        else:
            return {"success": False, "error": f"Unsupported file type: {file_type}"}
    
    def create_download_link(self, content: str, filename: str, mime_type: str = "text/plain") -> str:
        """Create download link for content"""
        b64 = base64.b64encode(content.encode()).decode()
        return f'<a href="data:{mime_type};base64,{b64}" download="{filename}">Download {filename}</a>'
    
    def save_processed_data(self, data: Any, format: str = 'json') -> bytes:
        """Save processed data in specified format"""
        if format == 'json':
            if isinstance(data, pd.DataFrame):
                return data.to_json(orient='records', indent=2).encode()
            else:
                return json.dumps(data, indent=2, default=str).encode()
        
        elif format == 'csv' and isinstance(data, pd.DataFrame):
            return data.to_csv(index=False).encode()
        
        elif format == 'excel' and isinstance(data, pd.DataFrame):
            output = io.BytesIO()
            data.to_excel(output, index=False, engine='xlsxwriter')
            return output.getvalue()
        
        else:
            return str(data).encode()

# Utility functions for easy access
def get_file_processor() -> FileProcessor:
    """Get file processor instance"""
    if "file_processor" not in st.session_state:
        st.session_state.file_processor = FileProcessor()
    return st.session_state.file_processor

def process_uploaded_file(uploaded_file) -> Dict[str, Any]:
    """Process uploaded file - convenience function"""
    processor = get_file_processor()
    return processor.process_file(uploaded_file)

def display_file_info(file_info: Dict[str, Any]):
    """Display file information in Streamlit"""
    if file_info.get("success"):
        st.success("✅ File processed successfully!")
        
        # Display stats based on file type
        if "stats" in file_info:
            stats = file_info["stats"]
            
            if "words" in stats:  # Text file
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Words", f"{stats['words']:,}")
                with col2:
                    st.metric("Characters", f"{stats['characters']:,}")
                with col3:
                    st.metric("Lines", f"{stats['lines']:,}")
            
            elif "rows" in stats:  # Data file
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rows", f"{stats['rows']:,}")
                with col2:
                    st.metric("Columns", f"{stats['columns']:,}")
                
                if "column_names" in stats:
                    st.write("**Columns:**", ", ".join(stats["column_names"]))
            
            elif "total_lines" in stats:  # Code file
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Lines", stats['total_lines'])
                with col2:
                    st.metric("Code Lines", stats['non_empty_lines'])
                with col3:
                    st.metric("Language", stats['language'])
        
        # Display preview if available
        if "preview" in file_info:
            with st.expander("📋 Data Preview"):
                st.write(file_info["preview"], unsafe_allow_html=True)
        
        elif "content" in file_info and len(file_info["content"]) < 2000:
            with st.expander("📋 Content Preview"):
                st.text(file_info["content"][:1000] + "..." if len(file_info["content"]) > 1000 else file_info["content"])
    
    else:
        st.error(f"❌ Error processing file: {file_info.get('error', 'Unknown error')}")

def create_file_download_button(content: Union[str, bytes], filename: str, label: str = "Download", mime_type: str = "text/plain"):
    """Create a download button for file content"""
    if isinstance(content, str):
        content = content.encode()
    
    return st.download_button(
        label=label,
        data=content,
        file_name=filename,
        mime=mime_type
    )