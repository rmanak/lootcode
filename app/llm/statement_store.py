"""In-memory store for problem *statements* awaiting the second generation step.

The admin "Generate with AI" flow is two steps: a problem **statement** first
(either written by the model from an idea, or pasted in by the owner), then the
full problem (contract + canonical + tests + hints) generated *from* that
statement. Between those steps the statement lives here — keyed by a short id —
so the statement-review page can render it (and cache the duplicate-check result
against it) without shuttling the whole text through the URL.

Same shape and rationale as :mod:`app.llm.draft_store`: a single-process,
in-memory, FIFO-capped map, which is the right amount of machinery for a
home/LAN app served by one worker. Not persisted — an abandoned statement just
ages out, costing at most a re-generation. If lootcode ever runs multiple
workers this must move to a shared store.
"""
from __future__ import annotations

import time
import uuid
from collections import OrderedDict
from threading import Lock

_MAX_STATEMENTS = 32

_store: "OrderedDict[str, dict]" = OrderedDict()
_lock = Lock()


def add(statement: str) -> str:
    """Stash a problem statement and return its short id."""
    sid = uuid.uuid4().hex[:12]
    with _lock:
        _store[sid] = {"statement": statement, "check": None, "created": time.time()}
        _store.move_to_end(sid)
        while len(_store) > _MAX_STATEMENTS:
            _store.popitem(last=False)  # evict the oldest
    return sid


def get(sid: str) -> dict | None:
    """The stored entry ``{statement, check, created}``, or None if unknown/expired."""
    with _lock:
        return _store.get(sid)


def set_statement(sid: str, statement: str) -> None:
    """Replace the statement text (an edit on the review page); invalidate the cached
    duplicate check so it is recomputed against the new text."""
    with _lock:
        entry = _store.get(sid)
        if entry is not None:
            entry["statement"] = statement
            entry["check"] = None


def set_check(sid: str, check: dict) -> None:
    """Cache the duplicate-check result (title/slug + similar problems) for the
    entry's current statement, so a re-render doesn't re-hit the LLM."""
    with _lock:
        entry = _store.get(sid)
        if entry is not None:
            entry["check"] = check


def pop(sid: str) -> dict | None:
    """Remove and return an entry (once the full problem has been generated)."""
    with _lock:
        return _store.pop(sid, None)
