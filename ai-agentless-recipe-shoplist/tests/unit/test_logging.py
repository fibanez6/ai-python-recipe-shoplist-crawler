#!/usr/bin/env python3
"""
Demo script showing how to use the centralized logging system.
Run this to test different logging levels and see the output.
"""

import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config.logging_config import (
    get_logger,
    log_api_request,
    log_function_call,
    set_debug_mode,
    setup_logging,
)


def demo_basic_logging():
    """Demonstrate basic logging functionality."""
    logger = get_logger(__name__)
    
    logger.debug("This is a DEBUG message - only shown when DEBUG=true")
    logger.info("This is an INFO message - general information")
    logger.warning("This is a WARNING message - something to pay attention to")
    logger.error("This is an ERROR message - something went wrong")
    
    print("\n" + "="*50)

def demo_function_logging():
    """Demonstrate function call logging."""
    logger = get_logger(__name__)
    
    # Log a simple function call
    log_function_call("my_function")
    
    # Log with arguments (sensitive data gets masked)
    log_function_call("authenticate", {
        "username": "john_doe",
        "password": "secret123",  # This will be masked
        "api_key": "sk-1234567890abcdef",  # This will be masked
        "timeout": 30
    })
    
    # Log with large data (gets truncated)
    big_data = "x" * 200
    log_function_call("process_data", {"large_content": big_data})
    
    print("\n" + "="*50)

def demo_api_logging():
    """Demonstrate API request logging."""
    logger = get_logger(__name__)
    
    # Successful API call
    log_api_request(
        provider="OpenAI",
        endpoint="/v1/chat/completions",
        payload_size=1024,
        duration=2.5,
        success=True
    )
    
    # Failed API call
    log_api_request(
        provider="GitHub",
        endpoint="/models/chat/completions",
        payload_size=512,
        duration=5.0,
        success=False
    )
    
    print("\n" + "="*50)

def demo_level_changes():
    """Demonstrate changing log levels dynamically."""
    logger = get_logger(__name__)
    
    logger.info("Current logging level demonstration:")
    
    logger.debug("Debug message - may not be visible")
    logger.info("Info message - should be visible")
    
    print("\nEnabling debug mode...")
    set_debug_mode(True)
    
    logger.debug("Debug message - now visible!")
    logger.info("Info message - still visible")
    
    print("\nDisabling debug mode...")
    set_debug_mode(False)
    
    logger.debug("Debug message - hidden again")
    logger.info("Info message - still visible")
    
    print("\n" + "="*50)

def main():
    """Run logging demonstrations."""
    print("AI Recipe Shoplist Crawler - Logging System Demo")
    print("=" * 60)
    
    # Setup logging with file output
    setup_logging(
        debug=True,
        enable_file_logging=True,
        log_file="logs/demo.log"
    )
    
    logger = get_logger(__name__)
    logger.info("Starting logging demo...")
    
    print("\n1. Basic Logging Levels:")
    print("-" * 30)
    demo_basic_logging()
    
    print("\n2. Function Call Logging:")
    print("-" * 30)
    demo_function_logging()
    
    print("\n3. API Request Logging:")
    print("-" * 30)
    demo_api_logging()
    
    print("\n4. Dynamic Level Changes:")
    print("-" * 30)
    demo_level_changes()
    
    logger.info("Logging demo completed!")
    print(f"\nCheck the log file: logs/demo.log")
    print("Console and file should contain the same messages.")
    
    # Show environment variables
    print(f"\nCurrent environment settings:")
    print(f"  DEBUG: {os.getenv('DEBUG', 'not set')}")
    print(f"  LOG_LEVEL: {os.getenv('LOG_LEVEL', 'not set')}")
    print(f"  LOG_FILE_ENABLED: {os.getenv('LOG_FILE_ENABLED', 'not set')}")

if __name__ == "__main__":
    main()