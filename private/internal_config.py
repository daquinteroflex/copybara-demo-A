"""Internal configuration - PRIVATE - DO NOT SYNC."""

# This file contains internal configurations that should never be synced
# to the public repository (copybara-demo-B)

INTERNAL_API_KEY = "secret-key-12345"
INTERNAL_DB_HOST = "internal.database.local"
INTERNAL_FEATURE_FLAGS = {
    "enable_debug_mode": True,
    "internal_monitoring": True,
    "admin_panel_access": True,
}

def get_internal_config():
    """Return internal configuration dictionary."""
    return {
        "api_key": INTERNAL_API_KEY,
        "db_host": INTERNAL_DB_HOST,
        "flags": INTERNAL_FEATURE_FLAGS,
    }
