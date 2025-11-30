"""
Configuration module for PDF2Text application
Loads environment variables and application settings
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # API Settings
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
    DEEPSEEK_MODEL = 'deepseek-chat'
    
    # File Processing Settings
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 50))
    SUPPORTED_FORMATS = ['.pdf']
    CHUNK_SIZE = 1000  # Characters per chunk for API processing
    
    # Retry Settings
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    TIMEOUT = 30  # seconds
    
    # Logging Settings
    ENABLE_LOGGING = os.getenv('ENABLE_LOGGING', 'true').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/app.log'
    
    # Output Settings
    OUTPUT_DIR = Path('outputs')
    TEMP_DIR = Path('temp')
    
    # UI Settings
    THEME = 'light'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY is not set. Please configure it in .env file")
        
        # Create necessary directories
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.TEMP_DIR.mkdir(exist_ok=True)
        Path('logs').mkdir(exist_ok=True)
        
        return True
