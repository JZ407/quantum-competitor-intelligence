"""Application configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# LLM — supports OpenAI-compatible APIs (DeepSeek, Anthropic via proxy, etc.)
LLM_API_KEY = os.path.expandvars(os.getenv("LLM_API_KEY", ""))
LLM_BASE_URL = os.path.expandvars(os.getenv("LLM_BASE_URL", "https://api.deepseek.com"))
LLM_MODEL = os.path.expandvars(os.getenv("LLM_MODEL", "deepseek-chat"))

# Data sources
HISTORICAL_DB_PATH = os.getenv(
    "HISTORICAL_DB_PATH",
    "D:/Claude_code/liangke_historical/historical_final.db"
)

# Platform database
DEFAULT_PLATFORM_DB = str(Path(__file__).parent.parent / "data" / "dataprojection.db")
PLATFORM_DB_PATH = os.getenv("PLATFORM_DB_PATH", DEFAULT_PLATFORM_DB)

# Limits
MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "10"))
QUERY_TIMEOUT = int(os.getenv("QUERY_TIMEOUT", "30"))
MAX_RESULT_ROWS = int(os.getenv("MAX_RESULT_ROWS", "200"))
