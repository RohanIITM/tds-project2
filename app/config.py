# app/config.py
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file in project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configuration variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HARD_TIMEOUT_SECONDS = int(os.getenv("HARD_TIMEOUT_SECONDS", "170"))  # ~<3 min headroom
MAX_IMAGE_BYTES = int(os.getenv("MAX_IMAGE_BYTES", "100000"))  # 100 kB
MAX_RESP_BYTES = int(os.getenv("MAX_RESP_BYTES", "800000"))  # safety cap
USER_AGENT = os.getenv("USER_AGENT", "DataAnalystAgent/0.1 (+https://example.com)")
