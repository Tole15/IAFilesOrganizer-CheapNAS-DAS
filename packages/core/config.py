import os
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/index.db")
STORAGE_ROOT = os.getenv("STORAGE_ROOT", "./sample_storage")
DRY_RUN_DEFAULT = os.getenv("DRY_RUN_DEFAULT", "true").lower() == "true"
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
OPENAI_PLAN_MODEL = os.getenv("OPENAI_PLAN_MODEL", "gpt-4.1-mini")