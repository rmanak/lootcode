"""Structural *input-feature* coverage tokens (solution-independent).

The core fix to the old selection flaw (see docs/test-strengthening.md, "Why
coverage, not adversaries"): an input's worth is *how much new behavior it
covers*, not whether some invented adversary or canonical-mutant happens to fail
on it. Adversary/mutant populations have systematic blind spots, so gating on
them throws away genuinely discriminating inputs (e.g. a nested-negative
expression that crashes a whole *class* of wrong parsers, yet kills no mutant of
a sign-stack canonical).

This module supplies the **reliable backbone** of the coverage model: a set of
coarse, bucketed, *structural* tokens describing an input's shape, derived purely
from the input and its declared types — no solution required. Two inputs that
produce different token sets exercise structurally different cases; selection
(app/testgen/select.py) keeps a small covering set over the union of these
tokens and the execution/output tokens from coverage.py.

Tokens are strings ``feat:<param>:<name>`` (param-scoped so multi-arg problems
don't alias). Buckets are deliberately coarse: the universe must be *finite and
small enough for a handful of cases to cover*, while still separating the
structural regimes wrong solutions mishandle (empty / singleton / duplicates /
ties / sortedness / signs / nesting depth / size extremes).
"""
from __future__ import annotations

from typing import Any

from .generators import (
    parse_type, looks_expression, _RICH_ARRAY_BASES, _LINKED_LIST_BASES,
)


# --------------------------------------------------------------------------- #
# Coarse numeric / size buckets
# --------------------------------------------------------------------------- #
def _sign(n: int) -> str:
    return "neg" if n < 0 else ("zero" if n == 0 else "pos")


def _mag(n: int) -> str:
    """Coarse magnitude bucket for an integer value."""
    a = abs(n)
    if a == 0:
        return "m0"
    if a == 1:
        return "m1"
    if a <= 10:
        return "m10"
    if a <= 1000:
        return "m1k"
    if a <= 10 ** 6:
        return "m1M"
    return "mBig"


def _size_bucket(n: int) -> str:
    """Coarse length bucket for a list/string (the classic boundary regimes)."""
    if n == 0:
        return "n0"
    if n == 1:
        return "n1"
    if n == 2:
        return "n2"
    if n <= 10:
        return "n<=10"
    if n <= 100:
        return "n<=100"
    if n <= 1000:
        return "n<=1k"
    return "nBig"


# --------------------------------------------------------------------------- #
# Per-type feature extraction
# --------------------------------------------------------------------------- #
def _int_list_feats(vals: list) -> set[str]:
    """Structural regimes of a flat list of ints (or int-like)."""
    out: set[str] = set()
    ints = [v for v in vals if isinstance(v, int) and not isinstance(v, bool)]
    if not ints:
        return out
    if any(v < 0 for v in ints):
        out.add("has-neg")
    if any(v == 0 for v in ints):
        out.add("has-zero")
    if all(v > 0 for v in ints):
        out.add("all-pos")
    if len(set(ints)) != len(ints):
        out.add("has-dup")
    if len(set(ints)) == 1:
        out.add("all-equal")
    if ints == sorted(ints):
        out.add("sorted-asc")
    if ints == sorted(ints, reverse=True):
        out.add("sorted-desc")
    out.add(f"min{_mag(min(ints))}")
    out.add(f"max{_mag(max(ints))}")
    return out


def _expr_feats(s: str) -> set[str]:
    """Structural features of an *expression-like* string (digits/ops/parens).

    Captures the nesting / sign / spacing regimes that separate correct
    expression evaluators from the many plausible-wrong ones, without evaluating
    the expression (that semantic regime is covered by coverage.py's value
    tokens). Only emitted when the string looks like arithmetic (see
    :func:`_looks_expression`)."""
    out: set[str] = set()
    depth = maxdepth = 0
    for ch in s:
        if ch == "(":
            depth += 1
            maxdepth = max(maxdepth, depth)
        elif ch == ")":
            depth = max(0, depth - 1)
    out.add(f"depth{min(maxdepth, 4)}")
    if "(-" in s.replace(" ", ""):
        out.add("unary-after-paren")
    if s.lstrip().startswith("-"):
        out.add("leading-minus")
    if "  " in s:
        out.add("multi-space")
    if any(c.isdigit() for c in s):
        # multi-digit run present?
        run = 0
        for ch in s:
            run = run + 1 if ch.isdigit() else 0
            if run >= 2:
                out.add("multi-digit")
                break
    if "()" in s.replace(" ", ""):
        out.add("empty-group")
    return out


def _str_feats(s: str) -> set[str]:
    out: set[str] = {_size_bucket(len(s))}
    if s and s == s[::-1]:
        out.add("palindrome")
    if len(set(s)) == 1 and s:
        out.add("all-same-char")
    if " " in s:
        out.add("has-space")
    return out


def _depth_size(v: Any) -> int:
    """Node count of a level-order tree array / linked-list value array."""
    if not isinstance(v, list):
        return 0
    return sum(1 for x in v if x is not None)


def _tree_feats(arr: list) -> set[str]:
    out: set[str] = {_size_bucket(_depth_size(arr))}
    n = len(arr)
    if n == 0:
        out.add("empty")
    elif n == 1:
        out.add("single")
    # Skew heuristic: a (near-)linear chain has array length ~ node count, while a
    # balanced tree packs ~2^d nodes into depth d. Compare length to a balanced
    # bound to flag skew vs balance without decoding.
    filled = _depth_size(arr)
    if filled >= 3:
        out.add("skewed" if n > 2 * filled - 1 else "bushy")
    if any(x is None for x in arr):
        out.add("has-holes")
    return out


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def _count_bucket(n: int) -> str:
    """Coarse call-count bucket for how often one method appears in a sequence."""
    if n == 0:
        return "c0"
    if n == 1:
        return "c1"
    if n <= 3:
        return "c<=3"
    if n <= 10:
        return "c<=10"
    return "cMany"


def _ops_seq_feats(operations: list, args: list) -> set[str]:
    """Structural regimes of a design problem's ``{operations, args}`` sequence.

    Solution-independent, exactly like the other feature extractors: length band,
    per-method call-count band, how many distinct methods are exercised, first/last
    method, and whether a first-argument value repeats (the collision/overwrite
    regime that trips stateful bugs). Emitted as ``feat:ops:*`` tokens so a handful
    of selected sequences cover the distinct shapes."""
    out: set[str] = {f"len:{_size_bucket(len(operations))}"}
    from collections import Counter
    names = [o for o in operations if isinstance(o, str)]
    counts = Counter(names)
    for name, c in counts.items():
        out.add(f"{name}:{_count_bucket(c)}")
    out.add(f"distinct:{min(len(counts), 6)}")
    # Skip index 0 (the constructor) for first/last-*method* signals.
    methods = names[1:]
    if methods:
        out.add(f"first:{methods[0]}")
        out.add(f"last:{methods[-1]}")
    # First-argument repetition across method calls (key collisions / overwrites).
    first_args = [a[0] for a in args[1:]
                  if isinstance(a, list) and a and _hashable(a[0])]
    if len(first_args) >= 2 and len(set(first_args)) < len(first_args):
        out.add("dup-first-arg")
    return out


def _hashable(v: Any) -> bool:
    try:
        hash(v)
        return True
    except TypeError:
        return False


def input_features(inp: dict, params: list[dict],
                   expr_hint: set[str] | None = None) -> set[str]:
    """Structural ``feat:<param>:<tok>`` tokens for one input.

    ``expr_hint`` (optional) names string params already known to carry
    expressions (inferred once from the seeds by the caller); those get the
    richer :func:`_expr_feats` treatment in addition to generic string features.

    A design problem's ``{operations, args}`` input (``kind == "class"``) is
    recognized by its keys and gets :func:`_ops_seq_feats` sequence tokens instead
    of per-param ones (its "params" are the constructor's, not the whole input).
    """
    expr_hint = expr_hint or set()
    out: set[str] = set()

    def add(name: str, toks: set[str]) -> None:
        for t in toks:
            out.add(f"feat:{name}:{t}")

    # Class/design problems: the input is a method-call sequence, not per-param.
    if (isinstance(inp.get("operations"), list)
            and isinstance(inp.get("args"), list)):
        add("ops", _ops_seq_feats(inp["operations"], inp["args"]))
        return out

    for p in params:
        name = p["name"]
        if name not in inp:
            continue
        v = inp[name]
        base, dims = parse_type(p.get("type", ""))

        if base in _RICH_ARRAY_BASES:
            if base in _LINKED_LIST_BASES:
                add(name, {_size_bucket(_depth_size(v))} |
                    ({"empty"} if _depth_size(v) == 0 else set()))
                if isinstance(v, list):
                    add(name, _int_list_feats(v))
            else:  # TreeNode
                if isinstance(v, list):
                    add(name, _tree_feats(v))
            continue

        if dims == 0:
            if base == "string":
                if isinstance(v, str):
                    add(name, _str_feats(v))
                    if name in expr_hint:
                        add(name, _expr_feats(v))
            elif base == "bool":
                add(name, {f"b{int(bool(v))}"})
            else:  # scalar int/num/float
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    add(name, {_sign(int(v)), _mag(int(v))})
            continue

        # Array (dims >= 1).
        if isinstance(v, list):
            add(name, {_size_bucket(len(v))})
            if dims == 1:
                if base == "string":
                    add(name, {f"strs-{_size_bucket(len(v))}"})
                else:
                    add(name, _int_list_feats(v))
            elif dims == 2:
                add(name, {f"rows{_size_bucket(len(v))}"})
                flat = [x for row in v if isinstance(row, list) for x in row]
                add(name, _int_list_feats(flat))
                if v and all(isinstance(r, list) for r in v):
                    widths = {len(r) for r in v}
                    add(name, {"ragged" if len(widths) > 1 else "rect"})
    return out


def expression_params(params: list[dict], seeds: list[dict]) -> set[str]:
    """Names of string params whose seed values look like arithmetic expressions."""
    hint: set[str] = set()
    for p in params:
        base, dims = parse_type(p.get("type", ""))
        if dims == 0 and base == "string":
            vals = [s[p["name"]] for s in seeds if isinstance(s.get(p["name"]), str)]
            if looks_expression(vals):
                hint.add(p["name"])
    return hint
