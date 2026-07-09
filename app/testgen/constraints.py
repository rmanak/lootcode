"""Best-effort parser for the prose constraints in a problem's ``problem.md``.

Constraints live as backtick math like ``1 <= n <= 10^5`` or ``-10^9 <= nums[i]
<= 10^9`` — sometimes in a ``## Constraints`` section, sometimes inline. There is
no machine-readable bound in the schema today, so we extract ``(name, lo, hi)``
ranges heuristically and let the generators look them up by param name.

Keys are stored under the *raw* token seen in the text:
  - a bare identifier / ``n`` / ``target``         → scalar bound for that name
  - ``nums[i]`` / ``grid[i][j]``                    → element bound (indexed form)
  - ``len(nums)`` / ``nums.length`` / ``nums.size`` → size bound

:func:`bounds_for` resolves those raw keys against a concrete param name.
Everything is best-effort: callers fall back to type defaults when a lookup fails.
"""
from __future__ import annotations

import re
from typing import Optional

# A numeric literal as written in constraint prose: 10^9, 5*10^4, 2 * 10^5, -1000.
_NUM = r"-?\d+(?:\s*\*\s*10\s*\^\s*\d+|\s*\^\s*\d+|10\^\d+)?|-?10\^\d+|-?\d+"
# A "variable" token: identifier, len(x), x.length/.size, or indexed x[i], x[i][j].
_VAR = r"[A-Za-z_]\w*(?:\[[^\]]*\])*(?:\.(?:length|size))?|len\([A-Za-z_]\w*\)"


def _num(tok: str) -> Optional[int]:
    """Parse a constraint numeric literal (``10^5``, ``5*10^4`` …) to an int."""
    s = tok.strip().replace(" ", "").replace("^", "**")
    if not re.fullmatch(r"-?\d+(?:\*\*\d+)?(?:\*\d+(?:\*\*\d+)?)*", s):
        return None
    try:
        val = eval(s, {"__builtins__": {}}, {})  # noqa: S307 - digits/*/** only
    except Exception:  # noqa: BLE001
        return None
    return val if isinstance(val, int) else None


def _norm_key(var: str) -> str:
    """Canonicalize a variable token: strip whitespace, keep the indexed form."""
    return var.strip()


def parse_constraints(md_text: str) -> dict[str, tuple[Optional[int], Optional[int]]]:
    """Return ``{token: (lo, hi)}`` for every bound we can recognize."""
    bounds: dict[str, list[Optional[int]]] = {}

    def add(name: str, lo: Optional[int], hi: Optional[int]) -> None:
        cur = bounds.setdefault(_norm_key(name), [None, None])
        if lo is not None:
            cur[0] = lo if cur[0] is None else max(cur[0], lo)
        if hi is not None:
            cur[1] = hi if cur[1] is None else min(cur[1], hi)

    text = md_text
    # Two-sided over a comma-list:  A <= v1, v2, v3 <= B  (each var gets [A, B]).
    _VARG = rf"(?:{_VAR})"  # parenthesized so the inner `|` alternation can't escape
    _VARLIST = rf"{_VARG}(?:\s*,\s*{_VARG})+"
    for m in re.finditer(rf"({_NUM})\s*<=?\s*({_VARLIST})\s*<=?\s*({_NUM})", text):
        lo, hi = _num(m.group(1)), _num(m.group(3))
        for var in re.split(r"\s*,\s*", m.group(2)):
            add(var, lo, hi)
    # Two-sided:  A <= var <= B   (also < / >, and the reversed  B >= var >= A)
    for m in re.finditer(rf"({_NUM})\s*<=?\s*({_VAR})\s*<=?\s*({_NUM})", text):
        lo, var, hi = _num(m.group(1)), m.group(2), _num(m.group(3))
        add(var, lo, hi)
    for m in re.finditer(rf"({_NUM})\s*>=?\s*({_VAR})\s*>=?\s*({_NUM})", text):
        hi, var, lo = _num(m.group(1)), m.group(2), _num(m.group(3))
        add(var, lo, hi)
    # One-sided:  var <= B   /   var >= A   /   A <= var   /   B >= var
    for m in re.finditer(rf"({_VAR})\s*<=\s*({_NUM})", text):
        add(m.group(1), None, _num(m.group(2)))
    for m in re.finditer(rf"({_VAR})\s*>=\s*({_NUM})", text):
        add(m.group(1), _num(m.group(2)), None)
    for m in re.finditer(rf"({_NUM})\s*<=\s*({_VAR})(?!\s*<)", text):
        add(m.group(2), _num(m.group(1)), None)
    for m in re.finditer(rf"({_NUM})\s*>=\s*({_VAR})(?!\s*>)", text):
        add(m.group(2), None, _num(m.group(1)))

    return {k: (v[0], v[1]) for k, v in bounds.items()}


def _lookup(bounds: dict, keys: list[str]) -> tuple[Optional[int], Optional[int]]:
    for k in keys:
        if k in bounds:
            return bounds[k]
    return (None, None)


def elem_bounds(bounds: dict, param: str) -> tuple[Optional[int], Optional[int]]:
    """Value range for the *elements* of an array param (``nums[i]`` forms)."""
    # Try more-specific (deeper-indexed) forms first so that e.g. board[i][j]
    # is preferred over board[i] when both are present in the bounds dict.
    return _lookup(bounds, [f"{param}[i][j]", f"{param}[i]", f"{param}[j]"])


def size_bounds(bounds: dict, param: str) -> tuple[Optional[int], Optional[int]]:
    """Length range for an array/string param (``len(nums)`` / ``nums.length``)."""
    return _lookup(bounds, [f"len({param})", f"{param}.length", f"{param}.size"])


def scalar_bounds(bounds: dict, param: str) -> tuple[Optional[int], Optional[int]]:
    """Value range for a scalar param (looked up by its bare name)."""
    return _lookup(bounds, [param])
