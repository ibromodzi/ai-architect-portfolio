# finsight_agent/config.py
# Central configuration for FinSight v1.0.
# All constants that appear in more than one file live here.

# Model
MODEL = "gemini-2.5-flash"

# Application identity
APP_NAME = "finsight_agent"
USER_ID = "finsight_user"
SESSION_ID = "finsight_session_001"

# Persistence
DB_URL = "sqlite+aiosqlite:///./finsight.db"

# Export
PDF_OUTPUT_DIR = "."