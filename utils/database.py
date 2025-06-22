import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
import streamlit as st

class DatabaseManager:
    """Manage SQLite database for GeminiCraft Studio"""
    
    def __init__(self, db_path: str = "data/geminicraft.db"):
        self.db_path = db_path
        self.ensure_database_exists()
        self.init_tables()
    
    def ensure_database_exists(self):
        """Ensure database directory and file exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_tables(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Conversations table for chat history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Analysis history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    input_data TEXT,
                    result TEXT NOT NULL,
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    preference_key TEXT NOT NULL,
                    preference_value TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, preference_key)
                )
            """)
            
            # File uploads tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_uploads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER,
                    tool_name TEXT NOT NULL,
                    file_hash TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Usage statistics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def get_session_id(self) -> str:
        """Get or create session ID"""
        if "session_id" not in st.session_state:
            st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return st.session_state.session_id
    
    # Conversation Management
    def save_conversation_message(
        self,
        tool_name: str,
        message_type: str,
        content: str,
        metadata: Dict = None
    ):
        """Save conversation message to database"""
        session_id = self.get_session_id()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (session_id, tool_name, message_type, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                tool_name,
                message_type,
                content,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
    
    def get_conversation_history(
        self,
        tool_name: str,
        limit: int = 50
    ) -> List[Dict]:
        """Get conversation history for a tool"""
        session_id = self.get_session_id()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT message_type, content, metadata, timestamp
                FROM conversations
                WHERE session_id = ? AND tool_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, tool_name, limit))
            
            rows = cursor.fetchall()
            
            conversations = []
            for row in rows:
                conversations.append({
                    "message_type": row[0],
                    "content": row[1],
                    "metadata": json.loads(row[2]) if row[2] else {},
                    "timestamp": row[3]
                })
            
            return list(reversed(conversations))  # Return in chronological order
    
    def clear_conversation_history(self, tool_name: str = None):
        """Clear conversation history"""
        session_id = self.get_session_id()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if tool_name:
                cursor.execute("""
                    DELETE FROM conversations
                    WHERE session_id = ? AND tool_name = ?
                """, (session_id, tool_name))
            else:
                cursor.execute("""
                    DELETE FROM conversations
                    WHERE session_id = ?
                """, (session_id,))
            conn.commit()
    
    # Analysis History Management
    def save_analysis_result(
        self,
        tool_name: str,
        analysis_type: str,
        input_data: str,
        result: str,
        metadata: Dict = None
    ):
        """Save analysis result to database"""
        session_id = self.get_session_id()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analysis_history (session_id, tool_name, analysis_type, input_data, result, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                tool_name,
                analysis_type,
                input_data,
                result,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
    
    def get_analysis_history(
        self,
        tool_name: str = None,
        limit: int = 20
    ) -> List[Dict]:
        """Get analysis history"""
        session_id = self.get_session_id()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if tool_name:
                cursor.execute("""
                    SELECT tool_name, analysis_type, input_data, result, metadata, timestamp
                    FROM analysis_history
                    WHERE session_id = ? AND tool_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (session_id, tool_name, limit))
            else:
                cursor.execute("""
                    SELECT tool_name, analysis_type, input_data, result, metadata, timestamp
                    FROM analysis_history
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (session_id, limit))
            
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    "tool_name": row[0],
                    "analysis_type": row[1],
                    "input_data": row[2],
                    "result": row[3],
                    "metadata": json.loads(row[4]) if row[4] else {},
                    "timestamp": row[5]
                })
            
            return history
    
    # User Preferences Management
    def save_user_preference(self, key: str, value: Any):
        """Save user preference"""
        session_id = self.get_session_id()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences (session_id, preference_key, preference_value)
                VALUES (?, ?, ?)
            """, (session_id, key, json.dumps(value)))
            conn.commit()
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        session_id = self.get_session_id()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT preference_value
                FROM user_preferences
                WHERE session_id = ? AND preference_key = ?
            """, (session_id, key))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return default
    
    def get_all_user_preferences(self) -> Dict:
        """Get all user preferences"""
        session_id = self.get_session_id()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT preference_key, preference_value
                FROM user_preferences
                WHERE session_id = ?
            """, (session_id,))
            
            rows = cursor.fetchall()
            preferences = {}
            for row in rows:
                preferences[row[0]] = json.loads(row[1])
            
            return preferences
    
    # File Upload Tracking
    def track_file_upload(
        self,
        filename: str,
        file_type: str,
        file_size: int,
        tool_name: str,
        file_hash: str = None
    ):
        """Track file upload"""
        session_id = self.get_session_id()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO file_uploads (session_id, filename, file_type, file_size, tool_name, file_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, filename, file_type, file_size, tool_name, file_hash))
            conn.commit()
    
    def get_file_upload_history(self, tool_name: str = None) -> List[Dict]:
        """Get file upload history"""
        session_id = self.get_session_id()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if tool_name:
                cursor.execute("""
                    SELECT filename, file_type, file_size, tool_name, file_hash, timestamp
                    FROM file_uploads
                    WHERE session_id = ? AND tool_name = ?
                    ORDER BY timestamp DESC
                """, (session_id, tool_name))
            else:
                cursor.execute("""
                    SELECT filename, file_type, file_size, tool_name, file_hash, timestamp
                    FROM file_uploads
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                """, (session_id,))
            
            rows = cursor.fetchall()
            
            uploads = []
            for row in rows:
                uploads.append({
                    "filename": row[0],
                    "file_type": row[1],
                    "file_size": row[2],
                    "tool_name": row[3],
                    "file_hash": row[4],
                    "timestamp": row[5]
                })
            
            return uploads
    
    # Usage Statistics
    def track_usage(self, tool_name: str, action_type: str):
        """Track tool usage"""
        session_id = self.get_session_id()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usage_stats (session_id, tool_name, action_type)
                VALUES (?, ?, ?)
            """, (session_id, tool_name, action_type))
            conn.commit()
    
    def get_usage_statistics(self) -> Dict:
        """Get usage statistics for current session"""
        session_id = self.get_session_id()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tool usage counts
            cursor.execute("""
                SELECT tool_name, COUNT(*) as usage_count
                FROM usage_stats
                WHERE session_id = ?
                GROUP BY tool_name
                ORDER BY usage_count DESC
            """, (session_id,))
            
            tool_usage = dict(cursor.fetchall())
            
            # Action type counts
            cursor.execute("""
                SELECT action_type, COUNT(*) as action_count
                FROM usage_stats
                WHERE session_id = ?
                GROUP BY action_type
                ORDER BY action_count DESC
            """, (session_id,))
            
            action_usage = dict(cursor.fetchall())
            
            # Total usage
            cursor.execute("""
                SELECT COUNT(*) as total_actions
                FROM usage_stats
                WHERE session_id = ?
            """, (session_id,))
            
            total_actions = cursor.fetchone()[0]
            
            return {
                "tool_usage": tool_usage,
                "action_usage": action_usage,
                "total_actions": total_actions,
                "session_id": session_id
            }
    
    # Data Export/Import
    def export_session_data(self) -> Dict:
        """Export all session data"""
        session_id = self.get_session_id()
        
        export_data = {
            "session_id": session_id,
            "export_timestamp": datetime.now().isoformat(),
            "conversations": {},
            "analysis_history": {},
            "preferences": self.get_all_user_preferences(),
            "file_uploads": self.get_file_upload_history(),
            "usage_statistics": self.get_usage_statistics()
        }
        
        # Export conversations by tool
        tools = ["smart_chat", "vision_analysis", "document_intelligence", 
                "code_assistant", "creative_writer", "data_analyst"]
        
        for tool in tools:
            export_data["conversations"][tool] = self.get_conversation_history(tool)
            export_data["analysis_history"][tool] = self.get_analysis_history(tool)
        
        return export_data
    
    def clear_all_session_data(self):
        """Clear all data for current session"""
        session_id = self.get_session_id()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            tables = ["conversations", "analysis_history", "user_preferences", 
                     "file_uploads", "usage_stats"]
            
            for table in tables:
                cursor.execute(f"""
                    DELETE FROM {table}
                    WHERE session_id = ?
                """, (session_id,))
            
            conn.commit()
    
    # Database Maintenance
    def get_database_info(self) -> Dict:
        """Get database information"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table sizes
            table_info = {}
            tables = ["conversations", "analysis_history", "user_preferences", 
                     "file_uploads", "usage_stats"]
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                table_info[table] = cursor.fetchone()[0]
            
            # Database file size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            return {
                "database_path": self.db_path,
                "database_size_bytes": db_size,
                "table_counts": table_info,
                "last_modified": datetime.fromtimestamp(os.path.getmtime(self.db_path)).isoformat() if os.path.exists(self.db_path) else None
            }
    
    def vacuum_database(self):
        """Optimize database"""
        with self.get_connection() as conn:
            conn.execute("VACUUM")
            conn.commit()

# Singleton instance
_db_manager = None

def get_database_manager() -> DatabaseManager:
    """Get singleton database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

# Convenience functions for easy usage
def save_chat_message(tool_name: str, message_type: str, content: str, metadata: Dict = None):
    """Save chat message"""
    db = get_database_manager()
    db.save_conversation_message(tool_name, message_type, content, metadata)

def get_chat_history(tool_name: str, limit: int = 50) -> List[Dict]:
    """Get chat history"""
    db = get_database_manager()
    return db.get_conversation_history(tool_name, limit)

def save_analysis(tool_name: str, analysis_type: str, input_data: str, result: str, metadata: Dict = None):
    """Save analysis result"""
    db = get_database_manager()
    db.save_analysis_result(tool_name, analysis_type, input_data, result, metadata)

def track_tool_usage(tool_name: str, action_type: str):
    """Track tool usage"""
    db = get_database_manager()
    db.track_usage(tool_name, action_type)

def get_user_pref(key: str, default: Any = None) -> Any:
    """Get user preference"""
    db = get_database_manager()
    return db.get_user_preference(key, default)

def set_user_pref(key: str, value: Any):
    """Set user preference"""
    db = get_database_manager()
    db.save_user_preference(key, value)