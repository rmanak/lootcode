"""Shared types and limits for the code executor backends."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Limits:
    time_limit_ms: int = 10_000
    memory_limit_mb: int = 512
    max_output_kb: int = 64
    import_budget_s: float = 5.0


@dataclass
class TestSpec:
    """A single test the harness should run (no `expected` — comparison is
    done by the caller so hidden expectations never enter the sandbox)."""

    name: str
    input: dict


@dataclass
class Outcome:
    """Result of running the user's function for one test."""

    status: str          # ok | timeout | error
    returned: object = None
    has_return: bool = False
    time_ms: float | None = None
    error: str | None = None
    stdout: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Outcome":
        return cls(
            status=d.get("status", "error"),
            returned=d.get("returned"),
            has_return="returned" in d,
            time_ms=d.get("time_ms"),
            error=d.get("error"),
            stdout=d.get("stdout", ""),
        )
