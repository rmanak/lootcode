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
    # Optional "extended" problem set: extra problems kept out of git (see
    # .gitignore) and seeded alongside CONTENT_DIR when present. Absent on a fresh
    # clone, so those problems — and any collection references to them — drop
    # cleanly. See docs/extended-problems.md.
    EXTENDED_CONTENT_DIR = BASE_DIR / "content" / "problems-extended"
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

    # On-the-fly "Get More Help with AI" hints on the problem page (optional).
    # Points at any OpenAI-compatible chat endpoint — llama.cpp's ``llama-server``
    # (default ``http://localhost:8080``) or a cloud provider that speaks the
    # OpenAI API. Falls back to the same env vars the bulk hint generator
    # (app/llm/hint_generator.py) already uses, so an existing local Qwen setup
    # works out of the box.
    LLM_HELP_URL = os.environ.get(
        "LLM_HELP_URL", os.environ.get("LLM_SERVER_URL", "http://localhost:8080"))
    LLM_HELP_API_KEY = os.environ.get(
        "LLM_HELP_API_KEY", os.environ.get("LLM_API_KEY", "sk-no-key-required"))
    LLM_HELP_MODEL = os.environ.get(
        "LLM_HELP_MODEL", os.environ.get("LLM_MODEL", "local-model"))

    # Which backend admin "Generate with AI" prefers: "auto" (Claude if a key is
    # set, else the OpenAI-compatible endpoint), or force "anthropic" / "openai".
    # A forced-but-unavailable choice falls back to whatever is reachable.
    LLM_GEN_BACKEND = os.environ.get("LLM_GEN_BACKEND", "auto").strip().lower()

    # Set once at startup by a health probe (see app/main.py lifespan). The problem
    # page enables the "Get More Help with AI" button only when this is True.
    llm_help_available: bool = False

    @property
    def ai_enabled(self) -> bool:
        return bool(self.ANTHROPIC_API_KEY)

    @property
    def generation_enabled(self) -> bool:
        """Whether admin "Generate with AI" can run: either the Claude API is
        configured (preferred) or a reachable OpenAI-compatible endpoint was found
        at startup (the same one the "Get More Help with AI" button uses)."""
        return self.ai_enabled or self.llm_help_available

    @property
    def content_dirs(self) -> list[Path]:
        """Problem roots to seed from, in order: the committed default set then
        the optional extended set. Missing dirs are skipped by content.load_all."""
        return [self.CONTENT_DIR, self.EXTENDED_CONTENT_DIR]


settings = Settings()
