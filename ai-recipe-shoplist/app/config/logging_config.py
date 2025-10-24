"""
Centralized logging configuration for the AI Recipe Shoplist Crawler.
"""

import logging
import os
import sys
from typing import Optional


def setup_logging(
    level: Optional[str] = None,
    debug: Optional[bool] = None,
    format_string: Optional[str] = None,
    enable_file_logging: bool = False,
    log_file: str = "app.log"
) -> logging.Logger:
    """
    Configure application logging with environment-based settings.
    
    Args:
        level: Log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        debug: Debug mode override (True/False)
        format_string: Custom log format string
        enable_file_logging: Whether to enable file logging
        log_file: Log file path (only used if enable_file_logging=True)
    
    Returns:
        Configured logger instance
    """
    
    # Get configuration from environment or parameters
    debug_enabled = debug if debug is not None else os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    log_level = level or os.getenv("LOG_LEVEL", "info").upper()
    
    # Default format string
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Override to DEBUG if debug is enabled
    if debug_enabled:
        numeric_level = logging.DEBUG
    
    # Clear any existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)
    
    # Configure root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(numeric_level)
    
    # File handler (optional)
    if enable_file_logging:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Create file handler with append mode
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)
    
    # Configure third-party loggers to reduce noise
    configure_third_party_loggers(numeric_level)
    
    # Get application logger
    app_logger = logging.getLogger("ai_recipe_shoplist")
    app_logger.setLevel(numeric_level)
    
    # Log configuration info
    app_logger.info(f"Logging configured - Level: {logging.getLevelName(numeric_level)}, Debug: {debug_enabled}")
    
    if enable_file_logging:
        app_logger.info(f"File logging enabled - Log file: {log_file}")
    
    return app_logger


def configure_third_party_loggers(level: int = logging.WARNING) -> None:
    """
    Configure third-party library loggers to reduce noise.
    
    Args:
        level: Log level for third-party loggers
    """
    # Reduce httpx/requests verbosity
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Reduce OpenAI client verbosity
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("azure").setLevel(logging.WARNING)
    
    # Reduce FastAPI/Uvicorn noise in debug mode
    if level == logging.DEBUG:
        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("fastapi").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f"ai_recipe_shoplist.{name}")


def set_debug_mode(enabled: bool = True) -> None:
    """
    Enable or disable debug mode for all loggers.
    
    Args:
        enabled: Whether to enable debug mode
    """
    level = logging.DEBUG if enabled else logging.INFO
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    for handler in root_logger.handlers:
        handler.setLevel(level)
    
    # Update environment variable
    os.environ["DEBUG"] = "true" if enabled else "false"
    
    logger = get_logger(__name__)
    logger.info(f"Debug mode {'enabled' if enabled else 'disabled'}")


def log_function_call(func_name: str, args: dict = None, level: int = logging.DEBUG) -> None:
    """
    Log function call details.
    
    Args:
        func_name: Name of the function being called
        args: Function arguments to log
        level: Log level to use
    """
    logger = get_logger(__name__)
    
    if args:
        # Sanitize sensitive data
        safe_args = {}
        for key, value in args.items():
            if any(sensitive in key.lower() for sensitive in ['token', 'key', 'password', 'secret']):
                safe_args[key] = f"{'*' * min(8, len(str(value)))}"
            elif isinstance(value, str) and len(value) > 100:
                safe_args[key] = f"{value[:50]}...{value[-10:]}"
            else:
                safe_args[key] = value
        
        logger.log(level, f"Function call: {func_name}({safe_args})")
    else:
        logger.log(level, f"Function call: {func_name}()")


def log_api_request(provider: str, endpoint: str, payload_size: int = 0, 
                   duration: float = None, success: bool = True) -> None:
    """
    Log API request details.
    
    Args:
        provider: API provider name (OpenAI, Azure, GitHub, etc.)
        endpoint: API endpoint
        payload_size: Size of request payload in bytes
        duration: Request duration in seconds
        success: Whether the request was successful
    """
    logger = get_logger(__name__)
    
    status = "SUCCESS" if success else "FAILED"
    duration_str = f", Duration: {duration:.2f}s" if duration else ""
    
    logger.info(f"API Request [{provider}] {status} - {endpoint}, Payload: {payload_size} bytes{duration_str}")


# Environment-based configuration constants
DEBUG_ENABLED = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE_ENABLED = os.getenv("LOG_FILE_ENABLED", "false").lower() in ("true", "1", "yes")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/app.log")

# Initialize logging on import (can be overridden later)
if not logging.getLogger().handlers:
    setup_logging(
        level=LOG_LEVEL,
        debug=DEBUG_ENABLED,
        enable_file_logging=LOG_FILE_ENABLED,
        log_file=LOG_FILE_PATH
    )