"""In-memory store for AI-generated problem drafts awaiting the owner's review.

AI generation no longer writes to the bank directly. A generated problem lives
here — as a draft — between the (slow, streamed) generate step and the moment the
owner clicks **Create** on the review page, where it goes through the exact same
validated save path as a hand-authored problem. This is what makes generation
safe: nothing lands in the DB or ``content/`` until a human has seen every field.

Deliberately simple: a single-process, in-memory, FIFO-capped map. lootcode is a
home/LAN app served by one worker, so a module-level dict is sufficient and the
right amount of machinery. Not persisted — a draft that is never confirmed just
ages out (or is lost on restart), which only ever costs a re-generation, never a
corrupted bank. If lootcode ever runs multiple workers, this must move to a shared
store (DB/Redis) so a draft created in one worker is visible to the review request
in another.
"""
from __future__ import annotations

import time
import uuid
from collections import OrderedDict
from threading import Lock

# Plenty for an interactive review queue; oldest drafts evict past this.
_MAX_DRAFTS = 64

_store: "OrderedDict[str, dict]" = OrderedDict()
_lock = Lock()


def add(data: dict) -> str:
    """Stash a generated problem dict and return its short draft id."""
    did = uuid.uuid4().hex[:12]
    with _lock:
        _store[did] = {"data": data, "created": time.time()}
        _store.move_to_end(did)
        while len(_store) > _MAX_DRAFTS:
            _store.popitem(last=False)  # evict the oldest
    return did


def get(did: str) -> dict | None:
    """The draft's problem dict, or None if it is unknown/expired."""
    with _lock:
        entry = _store.get(did)
        return entry["data"] if entry else None


def pop(did: str) -> dict | None:
    """Remove and return a draft (called once it has been saved or discarded)."""
    with _lock:
        entry = _store.pop(did, None)
        return entry["data"] if entry else None


def items() -> list[tuple[str, dict]]:
    """(draft_id, data) for every pending draft, oldest first (creation order)."""
    with _lock:
        return [(did, entry["data"]) for did, entry in _store.items()]
