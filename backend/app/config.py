from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

DEFAULT_DATABASE_URL = f"sqlite:///{(BACKEND_DIR / 'trainer.db').as_posix()}"
DEFAULT_GROQ_MODEL = "qwen/qwen3.8-27b"

DEMO_USER_ID = 1
DEMO_USERNAME = "hero"
DEMO_DISPLAY_NAME = "Герой Академии"
