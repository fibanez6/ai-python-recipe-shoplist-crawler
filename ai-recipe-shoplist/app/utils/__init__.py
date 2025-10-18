"""Utility modules for the AI Recipe Shoplist Crawler."""

from .logging_config import (
    setup_logging,
    get_logger,
    set_debug_mode,
    log_function_call,
    log_api_request,
    DEBUG_ENABLED,
    LOG_LEVEL
)

from .ai_helpers import (
    clean_json_response,
    safe_json_parse,
    extract_json_from_text,
    normalize_ai_response,
    validate_ingredient_data,
    validate_recipe_data,
    format_ai_prompt,
    RECIPE_EXTRACTION_PROMPT,
    INGREDIENT_NORMALIZATION_PROMPT,
    PRODUCT_MATCHING_PROMPT,
    ALTERNATIVES_PROMPT
)

__all__ = [
    # Logging utilities
    "setup_logging",
    "get_logger", 
    "set_debug_mode",
    "log_function_call",
    "log_api_request",
    "DEBUG_ENABLED",
    "LOG_LEVEL",
    
    # AI utilities
    "clean_json_response",
    "safe_json_parse",
    "extract_json_from_text",
    "normalize_ai_response",
    "validate_ingredient_data",
    "validate_recipe_data",
    "format_ai_prompt",
    "RECIPE_EXTRACTION_PROMPT",
    "INGREDIENT_NORMALIZATION_PROMPT", 
    "PRODUCT_MATCHING_PROMPT",
    "ALTERNATIVES_PROMPT"
]