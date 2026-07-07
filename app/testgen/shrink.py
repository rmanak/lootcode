"""Generic input shrinker (delta-debugging).

Given an input that satisfies some predicate ``keep`` (e.g. "in-domain, the
canonical runs cleanly, and a provided wrong solution still diverges/crashes"),
greedily reduce it to a minimal input that still satisfies ``keep`` — so a hidden
case added from a fuzz catcher is a small, readable reproducer instead of the
sprawling expression the fuzzer happened to hit.

Reduction operators are structural and type-agnostic: drop a character/element,
collapse a balanced ``()`` group, shrink an int toward zero. The predicate does
all the semantic work, so the shrinker needs no problem knowledge.
"""
from __future__ import annotations

from typing import Any, Callable, Iterator


def _str_reductions(s: str) -> Iterator[str]:
    # Whole balanced-paren groups first (biggest wins), then chunks, then chars.
    for i, ch in enumerate(s):
        if ch == "(":
            depth = 0
            for j in range(i, len(s)):
                if s[j] == "(":
                    depth += 1
                elif s[j] == ")":
                    depth -= 1
                    if depth == 0:
                        yield s[:i] + s[j + 1:]      # drop the whole group
                        yield s[:i] + s[i + 1:j] + s[j + 1:]  # unwrap the group
                        break
    for size in (8, 4, 2, 1):
        for i in range(0, len(s), size):
            yield s[:i] + s[i + size:]


def _list_reductions(v: list) -> Iterator[list]:
    for i in range(len(v)):
        yield v[:i] + v[i + 1:]
    for i, x in enumerate(v):
        if isinstance(x, int) and not isinstance(x, bool) and x not in (0,):
            yield v[:i] + [0] + v[i + 1:]


def _reductions(v: Any) -> Iterator[Any]:
    if isinstance(v, str):
        yield from _str_reductions(v)
    elif isinstance(v, list):
        yield from _list_reductions(v)
    elif isinstance(v, int) and not isinstance(v, bool):
        if v not in (0, 1, -1):
            yield 0
            yield v // 2


def shrink(inp: dict, keep: Callable[[dict], bool], max_rounds: int = 40) -> dict:
    """Return a minimal input ``<= inp`` (structurally) still satisfying ``keep``.

    ``keep(inp)`` must already be True. Fixed-point greedy: repeatedly accept the
    first reduction that keeps the predicate true, until nothing reduces."""
    cur = dict(inp)
    for _ in range(max_rounds):
        improved = False
        for name in list(cur.keys()):
            for cand in _reductions(cur[name]):
                trial = dict(cur)
                trial[name] = cand
                if trial != cur and keep(trial):
                    cur = trial
                    improved = True
                    break
        if not improved:
            break
    return cur
