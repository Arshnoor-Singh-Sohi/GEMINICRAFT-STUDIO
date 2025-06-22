import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # App Settings
    APP_NAME = os.getenv("APP_NAME", "GeminiCraft Studio")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # Model Settings
    DEFAULT_MODEL = "gemini-1.5-pro"
    MAX_TOKENS = 2048
    TEMPERATURE = 0.7
    
    # File Settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.jpg', '.png', '.jpeg']
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/conversations.db")
    
    # UI Settings
    THEME = "light"
    PAGE_ICON = "🚀"
    LAYOUT = "wide"