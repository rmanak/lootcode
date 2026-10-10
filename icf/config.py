"""ICF settings. Read from the environment; every one has a working default.

Deliberately separate from ``app.config``: this package is optional, and a
setting for a feature that may not be installed has no business in core's
settings object. The only thing shared with core is the executor's limits
plumbing (``app.executor.base.Limits``), because the sandbox is shared.
"""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


class IcfSettings:
    #: Problem definitions on disk (see icf/docs/problem-format.md).
    PROBLEMS_DIR = Path(os.environ.get("ICF_PROBLEMS_DIR", BASE_DIR / "problems"))

    #: ICF keeps its own database rather than adding tables to lootcode.db, so
    #: deleting this folder leaves nothing behind. It still holds user data
    #: (attempts, submitted code) — back it up with its -wal/-shm siblings.
    DB_PATH = os.environ.get("ICF_DB", str(BASE_DIR / "data" / "icf.db"))

    #: Assessment clock. Per-problem `time_cap_minutes` overrides it.
    DEFAULT_TIME_CAP_MINUTES = _int("ICF_TIME_CAP_MINUTES", 90)

    #: Per *case*, not per run: an ICF suite is many small cases.
    CASE_TIME_LIMIT_MS = _int("ICF_CASE_TIME_LIMIT_MS", 4_000)
    MEMORY_LIMIT_MB = _int("ICF_MEMORY_LIMIT_MB", 512)
    MAX_OUTPUT_KB = _int("ICF_MAX_OUTPUT_KB", 64)

    #: Hard ceiling on one sandbox run's wall clock, whatever the case count
    #: says. A submit is a synchronous request holding a threadpool worker, so
    #: an unbounded suite is an availability problem as much as a slow one.
    MAX_RUN_SECONDS = _int("ICF_MAX_RUN_SECONDS", 120)

    #: Ceiling on a stored submission, mirroring the core run API.
    MAX_CODE_CHARS = 256 * 1024
    #: Captured stdout kept per case (the sandbox applies its own run-wide cap).
    MAX_STORED_STDOUT = 4_000

    @property
    def DATABASE_URL(self) -> str:  # noqa: N802 - mirrors app.config's spelling
        return f"sqlite:///{self.DB_PATH}"


settings = IcfSettings()
