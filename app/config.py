"""Runtime configuration, read from environment (.env is loaded if present)."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


class Settings:
    APP_NAME = "lootcode"

    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = _int("PORT", 8000)

    DB_PATH = os.environ.get("LOOTCODE_DB", str(BASE_DIR / "lootcode.db"))
    DATABASE_URL = f"sqlite:///{DB_PATH}"

    CONTENT_DIR = BASE_DIR / "content" / "problems"
    # Curated, system-defined problem lists (e.g. "Blind 73"). See docs/collections.md.
    COLLECTIONS_DIR = BASE_DIR / "content" / "collections"
    TEMPLATES_DIR = APP_DIR / "templates"
    STATIC_DIR = APP_DIR / "static"

    # Executor
    EXECUTOR_BACKEND = os.environ.get("EXECUTOR_BACKEND", "subprocess")
    EXEC_TIME_LIMIT_MS = _int("EXEC_TIME_LIMIT_MS", 10_000)
    EXEC_MEMORY_LIMIT_MB = _int("EXEC_MEMORY_LIMIT_MB", 512)
    EXEC_MAX_OUTPUT_KB = _int("EXEC_MAX_OUTPUT_KB", 64)
    DOCKER_IMAGE = os.environ.get("EXEC_DOCKER_IMAGE", "lootcode-runner")

    # AI problem generation (optional)
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

    @property
    def ai_enabled(self) -> bool:
        return bool(self.ANTHROPIC_API_KEY)


settings = Settings()
