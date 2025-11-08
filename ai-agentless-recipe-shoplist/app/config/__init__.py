"""Configuration modules for the AI Recipe Shoplist Crawler."""

from .logging_config import (
    LOG_LEVEL,
    get_logger,
    log_api_request,
    log_function_call,
    set_debug_mode,
    setup_logging,
)
from .store_config import (
    DEFAULT_REGION,
    DEFAULT_STORES,
    REGIONAL_STORES,
    STORE_CONFIGS,
    StoreConfig,
    StoreRegion,
    get_active_stores,
    get_all_store_ids,
    get_store_config,
    get_store_display_names,
    get_stores_by_region,
    validate_store_id,
)

__all__ = [
    # Logging configuration
    "LOG_LEVEL",
    "get_logger",
    "log_api_request",
    "log_function_call",
    "set_debug_mode",
    "setup_logging",
    # Store configuration
    "DEFAULT_REGION",
    "DEFAULT_STORES",
    "REGIONAL_STORES",
    "STORE_CONFIGS",
    "StoreConfig",
    "StoreRegion",
    "get_active_stores",
    "get_all_store_ids",
    "get_store_config",
    "get_store_display_names",
    "get_stores_by_region",
    "validate_store_id",
]