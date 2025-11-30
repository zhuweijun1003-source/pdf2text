"""
Logging and Error Handling Module
Centralized logging configuration and error handling utilities
"""
import sys
from pathlib import Path
from loguru import logger
from config import Config
import traceback
from typing import Optional, Callable, Any
from functools import wraps


def setup_logging():
    """Setup application logging with loguru"""
    try:
        # Remove default handler
        logger.remove()
        
        # Console handler with color
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level=Config.LOG_LEVEL,
            colorize=True
        )
        
        # File handler
        if Config.ENABLE_LOGGING:
            log_path = Path(Config.LOG_FILE)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.add(
                Config.LOG_FILE,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
                level=Config.LOG_LEVEL,
                rotation="10 MB",
                retention="7 days",
                compression="zip"
            )
        
        logger.info("Logging system initialized")
        
    except Exception as e:
        print(f"Error setting up logging: {e}")


def handle_exceptions(default_return=None, log_error=True):
    """
    Decorator for exception handling
    
    Args:
        default_return: Default return value on exception
        log_error: Whether to log the error
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {e}")
                    logger.debug(traceback.format_exc())
                return default_return
        return wrapper
    return decorator


class AppError(Exception):
    """Base application error class"""
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class PDFProcessingError(AppError):
    """PDF processing related errors"""
    pass


class APIError(AppError):
    """API related errors"""
    pass


class ValidationError(AppError):
    """Validation related errors"""
    pass


class FileError(AppError):
    """File operation related errors"""
    pass


def validate_file_size(file_size_bytes: int, max_size_mb: Optional[int] = None) -> bool:
    """
    Validate file size
    
    Args:
        file_size_bytes: File size in bytes
        max_size_mb: Maximum allowed size in MB
        
    Returns:
        True if valid
        
    Raises:
        ValidationError if file too large
    """
    max_size_mb = max_size_mb or Config.MAX_FILE_SIZE_MB
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size_bytes > max_size_bytes:
        raise ValidationError(
            f"File size exceeds maximum allowed size of {max_size_mb}MB",
            f"File size: {file_size_bytes / 1024 / 1024:.2f}MB"
        )
    
    return True


def validate_file_format(file_path: str, allowed_formats: Optional[list] = None) -> bool:
    """
    Validate file format
    
    Args:
        file_path: Path to file
        allowed_formats: List of allowed extensions
        
    Returns:
        True if valid
        
    Raises:
        ValidationError if format not allowed
    """
    allowed_formats = allowed_formats or Config.SUPPORTED_FORMATS
    file_obj = Path(file_path)
    
    if file_obj.suffix.lower() not in allowed_formats:
        raise ValidationError(
            f"File format not supported: {file_obj.suffix}",
            f"Allowed formats: {', '.join(allowed_formats)}"
        )
    
    return True


class ProgressTracker:
    """Track and report progress for long-running operations"""
    
    def __init__(self, total_steps: int, callback=None):
        """
        Initialize progress tracker
        
        Args:
            total_steps: Total number of steps
            callback: Optional callback function(current, total)
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.callback = callback
        self.messages = []
    
    def update(self, step: Optional[int] = None, message: Optional[str] = None):
        """
        Update progress
        
        Args:
            step: Current step number (if None, increments by 1)
            message: Optional progress message
        """
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
        
        if message:
            self.messages.append(message)
            logger.info(f"Progress: {self.get_percentage():.1f}% - {message}")
        
        if self.callback:
            self.callback(self.current_step, self.total_steps)
    
    def get_percentage(self) -> float:
        """Get current progress percentage"""
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100
    
    def is_complete(self) -> bool:
        """Check if progress is complete"""
        return self.current_step >= self.total_steps
    
    def reset(self):
        """Reset progress"""
        self.current_step = 0
        self.messages = []


# Initialize logging when module is imported
setup_logging()
