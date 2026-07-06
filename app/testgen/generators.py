"""Type-keyed candidate-*input* generators (techniques T1–T4 in the plan).

Given a problem's ``params`` (``[{name, type}]``), existing example inputs (used
as fuzz seeds), and parsed constraint bounds, produce a de-duplicated list of
candidate inputs — each a dict keyed by param name, ready to feed the canonical.

We deliberately *only* generate inputs here. Expected values come later from
executing the canonical, and *selection* is driven by mutation kills — the model's
judgment is out of the trust path.
"""
from __future__ import annotations

import copy
import json
import random
import string as _string
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from . import constraints as C


@dataclass
class GenConfig:
    n_fuzz: int = 80            # random small inputs (T3)
    n_seed_mut: int = 3         # perturbed copies per existing example (T3, seeded)
    max_candidates: int = 140   # hard cap (edges + seeds + stress kept first)
    fuzz_size: int = 8          # max array/string length for small fuzz
    stress_n: int = 20_000      # size of the single large-stress input (T4)
    seed: int = 1234
    include_stress: bool = True


# --------------------------------------------------------------------------- #
# Type model
# --------------------------------------------------------------------------- #
def parse_type(t: str) -> tuple[str, int]:
    """``"int[][]"`` -> ``("int", 2)``.  Unknown bases pass through as-is."""
    t = (t or "").strip()
    dims = 0
    while t.endswith("[]"):
        dims += 1
        t = t[:-2].strip()
    return t, dims


_SCALAR_ALIASES = {"num": "int", "integer": "int", "str": "string", "boolean": "bool"}

# Rich types whose declared form is dims-0 but whose on-the-wire (and on-disk)
# encoding is an *array*: TreeNode is a level-order array; the linked-list nodes
# are a flat value array. Generators treat these as arrays, not scalars.
_LINKED_LIST_BASES = ("ListNode", "DoublyLinkedList")
_RICH_ARRAY_BASES = ("TreeNode",) + _LINKED_LIST_BASES


def _base(t: str) -> str:
    return _SCALAR_ALIASES.get(t, t)


# --------------------------------------------------------------------------- #
# Scalar / value generation
# --------------------------------------------------------------------------- #
def _rand_scalar(rng: random.Random, base: str, lo: Optional[int], hi: Optional[int]) -> Any:
    base = _base(base)
    if base == "bool":
        return rng.choice([True, False])
    if base == "float":
        a = lo if lo is not None else -50
        b = hi if hi is not None else 50
        return round(rng.uniform(a, b), 3)
    if base in ("string",):
        alpha = _string.ascii_lowercase[: rng.choice([2, 3, 4, 26])]
        n = rng.randint(1, 6)
        return "".join(rng.choice(alpha) for _ in range(n))
    # int / any / unknown -> small int
    a = lo if lo is not None else -50
    b = hi if hi is not None else 50
    if a > b:
        a, b = b, a
    # keep fuzz values small even when constraints allow huge ranges
    a = max(a, -1000)
    b = min(b, 1000)
    return rng.randint(a, b)


def _rand_value(rng: random.Random, base: str, dims: int,
                lo: Optional[int], hi: Optional[int], size: int) -> Any:
    if base == "TreeNode":
        return _rand_tree(rng, size, lo, hi)
    if base in _LINKED_LIST_BASES:
        # Flat value array (the linked-list wire form): a list of node values.
        return [_rand_scalar(rng, "int", lo, hi) for _ in range(rng.randint(0, size))]
    if dims == 0:
        return _rand_scalar(rng, base, lo, hi)
    n = rng.randint(0, size)
    return [_rand_value(rng, base, dims - 1, lo, hi, size) for _ in range(n)]


def _rand_tree(rng: random.Random, size: int, lo: Optional[int], hi: Optional[int]) -> list:
    """Random level-order tree array (with ``None`` holes), the harness input form."""
    n = rng.randint(0, max(1, size))
    out: list[Any] = []
    a = max(lo if lo is not None else -50, -1000)
    b = min(hi if hi is not None else 50, 1000)
    for i in range(n):
        # root always present; internal holes allowed but keep it mostly filled
        if i == 0 or rng.random() > 0.25:
            out.append(rng.randint(a, b))
        else:
            out.append(None)
    while out and out[-1] is None:
        out.pop()
    return out


# --------------------------------------------------------------------------- #
# T1 — structured edge shapes (per param type)
# --------------------------------------------------------------------------- #
def _scalar_edges(base: str, lo: Optional[int], hi: Optional[int]) -> list[Any]:
    base = _base(base)
    if base == "bool":
        return [True, False]
    if base == "float":
        vals = [0.0, 1.0, -1.0]
        if lo is not None:
            vals.append(float(lo))
        if hi is not None:
            vals.append(float(hi))
        return vals
    if base == "string":
        return ["", "a", "aa", "ab", "zzzz"]
    vals = [0, 1, -1]
    for v in (lo, hi):
        if v is not None:
            vals.append(v)
            vals.append(v + 1 if v is not None else v)
    # Respect parsed bounds: don't inject out-of-domain values (e.g. -1/0 when the
    # constraint is `1 <= x`) — those make many canonicals error or loop forever.
    out = [v for v in dict.fromkeys(vals)
           if (lo is None or v >= lo) and (hi is None or v <= hi)]
    return out or [lo if lo is not None else 0]


def _array_edges(base: str, dims: int, lo: Optional[int], hi: Optional[int]) -> list[Any]:
    if base == "TreeNode":
        return [[], [1], [1, 2, 3], [1, 2, 3, 4, 5, 6, 7],
                [1, 2, None, 3, None, 4], [1, None, 2, None, 3]]  # empty/single/full/left/right
    if base in _LINKED_LIST_BASES:
        return [[], [1], [1, 2], [2, 1], [1, 1, 1], [1, 2, 3, 4, 5],
                [5, 4, 3, 2, 1], [1, 1, 2, 2]]  # empty/single/pair/dup/sorted/reversed
    inner = (_array_edges(base, dims - 1, lo, hi) if dims > 1
             else _scalar_edges(base, lo, hi))
    # a representative single element for building shapes
    one = inner[0] if inner else (0 if _base(base) == "int" else "")
    two = inner[1] if len(inner) > 1 else one
    shapes: list[Any] = [
        [],                       # empty
        [one],                    # singleton
        [one, one, one],          # all-equal
        [one, two],               # pair
        [two, one],               # reversed pair
        [one, one, two, two],     # duplicate-heavy
    ]
    if _base(base) == "int" and dims == 1:
        shapes += [[3, 4, 6, 6, 1], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1]]
    return shapes


def edge_values(param_type: str, lo: Optional[int], hi: Optional[int]) -> list[Any]:
    base, dims = parse_type(param_type)
    if base in _RICH_ARRAY_BASES:
        return _array_edges(base, 1, lo, hi)
    if dims == 0:
        return _scalar_edges(base, lo, hi)
    return _array_edges(base, dims, lo, hi)


# --------------------------------------------------------------------------- #
# T3 — seed-based structural mutation (perturb an existing example input)
# --------------------------------------------------------------------------- #
def _mutate_json(rng: random.Random, val: Any) -> Any:
    if isinstance(val, bool):
        return not val if rng.random() < 0.5 else val
    if isinstance(val, int):
        return val + rng.choice([-2, -1, 1, 2]) if rng.random() < 0.7 else val
    if isinstance(val, float):
        return round(val + rng.uniform(-2, 2), 3)
    if isinstance(val, str):
        if not val or rng.random() < 0.3:
            return val
        i = rng.randrange(len(val))
        c = rng.choice(_string.ascii_lowercase[:4])
        return val[:i] + c + val[i + 1:]
    if isinstance(val, list):
        out = [_mutate_json(rng, x) for x in val]
        r = rng.random()
        if out and r < 0.25:                 # duplicate an element
            out.insert(rng.randrange(len(out)), copy.deepcopy(rng.choice(out)))
        elif out and r < 0.45:               # drop an element
            out.pop(rng.randrange(len(out)))
        elif out and r < 0.65:               # reorder
            rng.shuffle(out)
        return out
    return val


# --------------------------------------------------------------------------- #
# T4 — one large-stress input per array/string param
# --------------------------------------------------------------------------- #
def _stress_value(rng: random.Random, base: str, dims: int,
                  lo: Optional[int], hi: Optional[int], n: int) -> Any:
    if base in _RICH_ARRAY_BASES:
        return [rng.randint(1, 100) for _ in range(n)]
    if dims == 0:
        # a scalar "n" param: push it large (bounded by hi if known)
        top = hi if hi is not None else n
        return min(top, n) if _base(base) == "int" else _rand_scalar(rng, base, lo, hi)
    if dims == 1:
        if _base(base) == "string":
            return "".join(rng.choice("ab") for _ in range(n))
        a = max(lo if lo is not None else -1000, -10**6)
        b = min(hi if hi is not None else 1000, 10**6)
        # adversarial-ish: long runs plus periodic repeats
        return [(i % 7) if rng.random() < 0.5 else rng.randint(a, b) for i in range(n)]
    inner_n = max(1, int(n ** 0.5))
    rows = max(1, n // inner_n)
    return [_stress_value(rng, base, dims - 1, lo, hi, inner_n) for _ in range(rows)]


# --------------------------------------------------------------------------- #
# Design/streaming problems: vocabulary-aware "operations" generator
# --------------------------------------------------------------------------- #
# Many design problems take a single param that is a list of operation records,
# each ``[<op-name:str>, <args...>]`` (e.g. ``[["addNum",3],["findMedian"]]``).
# Random JSON fuzzing destroys that structure (the canonical then errors and the
# candidate is dropped), so we *learn* the op vocabulary from the example inputs
# and synthesize valid sequences — which is what actually exposes streaming bugs.
def _is_ops(values: list) -> bool:
    """Heuristic: every example value is a list of ``[str, ...]`` records."""
    saw = False
    for v in values:
        if not isinstance(v, list):
            return False
        for op in v:
            if not (isinstance(op, list) and op and isinstance(op[0], str)):
                return False
            saw = True
    return saw


@dataclass
class _OpVocab:
    # op-name -> list of per-arg "domains"; a domain is a set of observed values
    # (for small enums like keys) plus an int range when numeric.
    names: list[str] = field(default_factory=list)
    arg_types: dict = field(default_factory=dict)   # name -> [type,...]
    arg_vals: dict = field(default_factory=dict)     # (name, i) -> list of observed
    int_lo: int = 1
    int_hi: int = 9


def _learn_ops(values: list) -> _OpVocab:
    v = _OpVocab()
    ints: list[int] = []
    for seq in values:
        for op in seq:
            name, args = op[0], op[1:]
            if name not in v.arg_types:
                v.names.append(name)
                v.arg_types[name] = [type(a).__name__ for a in args]
            for i, a in enumerate(args):
                v.arg_vals.setdefault((name, i), [])
                if a not in v.arg_vals[(name, i)]:
                    v.arg_vals[(name, i)].append(a)
                if isinstance(a, int) and not isinstance(a, bool):
                    ints.append(a)
    if ints:
        lo, hi = min(ints), max(ints)
        # keep a small span so duplicates/collisions are frequent (they trigger bugs)
        v.int_lo, v.int_hi = lo, max(hi, lo + 8)
    return v


def _gen_op(rng: random.Random, v: _OpVocab, name: str, small_ints: bool) -> list:
    op = [name]
    for i, t in enumerate(v.arg_types.get(name, [])):
        observed = v.arg_vals.get((name, i), [])
        if t == "str":
            # sample from observed keys plus a couple fresh ones (small alphabet)
            pool = observed + ["a", "b", "c"]
            op.append(rng.choice(pool))
        elif t in ("int", "float"):
            if small_ints or not observed:
                lo, hi = (1, 6) if small_ints else (v.int_lo, v.int_hi)
                val = rng.randint(lo, hi)
            else:
                val = rng.choice(observed + [rng.randint(v.int_lo, v.int_hi)])
            op.append(val if t == "int" else float(val))
        elif t == "bool":
            op.append(rng.choice([True, False]))
        else:
            op.append(observed[0] if observed else 0)
    return op


def _gen_ops_seq(rng: random.Random, v: _OpVocab, length: int,
                 small_ints: bool = True) -> list:
    return [_gen_op(rng, v, rng.choice(v.names), small_ints) for _ in range(length)]


def _gen_ops_stress(rng: random.Random, v: _OpVocab, n: int) -> list:
    """A large T4 sequence that stresses the data structure but keeps *output*
    small — dominated by mutating ops with only a sparse sprinkle of queries, so
    the returned array (and thus result size) stays well under the output cap."""
    mutators = [x for x in v.names if v.arg_types.get(x)] or v.names
    queries = [x for x in v.names if not v.arg_types.get(x)]
    every = max(1, n // 50)  # ~50 query results total, regardless of n
    out = []
    for i in range(n):
        if queries and i % every == every - 1:
            out.append([rng.choice(queries)])
        else:
            out.append(_gen_op(rng, v, rng.choice(mutators), False))
    return out


def _ops_edges(rng: random.Random, v: _OpVocab) -> list[list]:
    """Structured edge sequences for a design problem."""
    out: list[list] = [[]]                                  # empty program
    # single of each op
    for n in v.names:
        out.append([_gen_op(rng, v, n, True)])
    # a burst of the first (mutating) op then every query op, duplicate-heavy
    mutators = [n for n in v.names if v.arg_types.get(n)]
    queries = [n for n in v.names if not v.arg_types.get(n)]
    if mutators:
        m = mutators[0]
        burst = [_gen_op(rng, v, m, True) for _ in range(5)]
        out.append(burst + [[q] for q in queries] if queries else burst)
        # duplicate-heavy: same arg repeated
        dup = [_gen_op(rng, v, m, True) for _ in range(3)]
        for op in dup:
            for i, t in enumerate(v.arg_types.get(m, []), start=1):
                if t in ("int", "float"):
                    op[i] = dup[0][i]
        out.append(dup + [[q] for q in queries] if queries else dup)
    return out


# --------------------------------------------------------------------------- #
# Structural invariants learned from a problem's OWN example inputs
# --------------------------------------------------------------------------- #
# Many problems carry an input *precondition* that prose-parsing can't reliably
# extract — "ascending array of unique values" (binary-search), "a permutation of
# 0..N-1" (array-nesting), "sorted, possibly rotated" (search-rotated). Fuzzing
# blindly violates these, and baking the canonical's answer on an *invalid* input
# would unfairly fail a correct solution written to the contract.
#
# We can't read the statement, but we can check which structural properties hold
# across *every* stored example for a param and enforce them. This is unsound in
# one direction only, and safely so: OVER-inferring a property we don't truly need
# just makes generation more conservative (still-valid inputs); UNDER-inferring is
# the residual risk. So it strictly reduces unfair-test risk without ever adding to
# it. Same mechanical, in-process spirit as the op-vocabulary learner above.
def _cyclic_descents(v: list) -> int:
    """Number of i where ``v[i] > v[(i+1) % n]`` — 1 for a sorted-or-rotated
    distinct array, ≥2 for an arbitrary one."""
    n = len(v)
    return sum(1 for i in range(n) if v[i] > v[(i + 1) % n])


def _numeric_1d(v: Any) -> bool:
    return (isinstance(v, list)
            and all(isinstance(x, int) and not isinstance(x, bool) for x in v))


def learn_array_invariants(seed_vals: list) -> set[str]:
    """Structural properties true of *every* seed value for a 1-D int-array param.

    Returns a subset of {asc, desc, perm0, perm1, rot}. Requires ≥3 example arrays
    and at least one of length ≥2 so a couple of trivially-short samples can't
    manufacture a spurious invariant."""
    arrs = [v for v in seed_vals if _numeric_1d(v)]
    nontriv = [v for v in arrs if len(v) >= 2]
    if len(arrs) < 3 or not nontriv:
        return set()
    inv: set[str] = set()
    if all(v == sorted(v) for v in nontriv):
        inv.add("asc")
    if all(v == sorted(v, reverse=True) for v in nontriv):
        inv.add("desc")
    if all(sorted(v) == list(range(len(v))) for v in arrs):
        inv.add("perm0")
    if all(sorted(v) == list(range(1, len(v) + 1)) for v in arrs):
        inv.add("perm1")
    if all(len(set(v)) == len(v) and _cyclic_descents(v) <= 1 for v in nontriv):
        inv.add("rot")               # sorted-or-rotated with distinct values
    return inv


def array_satisfies(v: list, inv: set[str]) -> bool:
    """Whether array ``v`` respects the learned invariants ``inv``."""
    if not v or not _numeric_1d(v):
        return True                  # empty / non-numeric: other filters handle it
    if "asc" in inv and v != sorted(v):
        return False
    if "desc" in inv and v != sorted(v, reverse=True):
        return False
    if "perm0" in inv and sorted(v) != list(range(len(v))):
        return False
    if "perm1" in inv and sorted(v) != list(range(1, len(v) + 1)):
        return False
    if "rot" in inv and not (len(set(v)) == len(v) and _cyclic_descents(v) <= 1):
        return False
    return True


# --------------------------------------------------------------------------- #
# Graph node-label domain for int[][] edge/adjacency params ("A+" fairness)
# --------------------------------------------------------------------------- #
# The 1-D invariant guard above only understands flat int arrays. The integers
# *inside* an int[][] edge/adjacency param are graph node labels bounded by the
# problem's contract (`0 <= node < n`, or `< len(adj)` for an adjacency list).
# Fuzz mutates those into out-of-domain labels (negatives, ids >= n) that a
# correct solution written to the contract would reject — an unfair test. We learn
# the domain from the param's *own* examples (mechanical, no statement reading) and
# drop violating candidates. Safe-in-one-direction, exactly like the array guard:
# an over-guess only makes generation more conservative.
_MATRIX_NAMES = {                      # value grids — never node-label graphs
    "grid", "matrix", "mat", "board", "image", "img", "img1", "img2",
    "obstaclegrid", "targetgrid", "heights", "wall", "dp", "cells", "field",
    "points", "intervals", "queries", "rectangles", "envelopes", "triangle",
}
_EDGE_NAMES = {
    "edges", "connections", "prerequisites", "graph", "adj", "adjlist",
    "flights", "roads", "times", "pairs", "dislikes", "relations",
    "dependencies", "routes", "rededges", "blueedges", "trust", "bridges",
}


def _matrix_ints(m: list) -> list:
    return [x for r in m if isinstance(r, list) for x in r
            if isinstance(x, int) and not isinstance(x, bool)]


def _endpoint_ints(m: list) -> list:
    """Node-label columns of an edge list: first two of a wide (weighted) row,
    all of a width-≤2 row. Adjacency out-of-range is caught by ``lt_len`` instead."""
    out: list = []
    for r in m:
        if not isinstance(r, list):
            continue
        cols = r[:2] if len(r) >= 3 else r
        out += [x for x in cols if isinstance(x, int) and not isinstance(x, bool)]
    return out


def learn_intmatrix_domain(name: str, seed_mats: list,
                           scalar_seeds: dict) -> Optional[dict]:
    """Learn the node-label domain of an int[][] edge/adjacency param.

    Returns a dict with any of ``{"nonneg", "lt_len", "lt_params"}`` or None.
    ``scalar_seeds`` maps each scalar-int param name to its value in each of the
    *same* seeds as ``seed_mats`` (1:1). Requires ≥2 examples. Only fires once the
    param is confidently graph-like — a structural index signal (adjacency
    self-reference or a scalar upper bound) or an edge-ish name — so value grids
    and coordinate/interval pairs are left untouched."""
    mats = [m for m in seed_mats
            if isinstance(m, list) and all(isinstance(r, list) for r in m)]
    if len(mats) < 2:
        return None
    lname = name.lower()
    if lname in _MATRIX_NAMES:
        return None
    all_ints = [x for m in mats for x in _matrix_ints(m)]
    if not all_ints:
        return None

    dom: dict = {}
    ragged = len({len(r) for m in mats for r in m}) > 1
    # adjacency self-bound: every entry indexes a row of the same matrix
    if (ragged or lname in ("graph", "adj", "adjlist")) and \
            all(0 <= x < len(m) for m in mats for x in _matrix_ints(m)):
        dom["lt_len"] = True
    # scalar upper bound: endpoint labels < some scalar param (n, numCourses, …)
    lt: list = []
    for q, qvals in scalar_seeds.items():
        if q == name or len(qvals) != len(mats) or not qvals:
            continue
        if all(isinstance(qv, int) and qv > 0 for qv in qvals) and \
                any(_endpoint_ints(m) for m in mats) and \
                all(0 <= x < qv
                    for m, qv in zip(mats, qvals) for x in _endpoint_ints(m)):
            lt.append(q)
    if lt:
        dom["lt_params"] = lt

    graphlike = bool(dom) or lname in _EDGE_NAMES
    if not graphlike:
        return None                          # ambiguous shape, no name → leave alone
    if all(x >= 0 for x in all_ints):
        dom["nonneg"] = True
    return dom or None


def intmatrix_satisfies(m: list, dom: dict, inp: dict) -> bool:
    """Whether int-matrix ``m`` respects the learned node-label domain ``dom``
    (``inp`` supplies the current value of any scalar upper-bound param)."""
    if not isinstance(m, list) or not all(isinstance(r, list) for r in m):
        return True
    ints = _matrix_ints(m)
    if not ints:
        return True                          # empty edge set: length filters handle it
    if dom.get("nonneg") and any(x < 0 for x in ints):
        return False
    if dom.get("lt_len") and any(not (0 <= x < len(m)) for x in ints):
        return False
    for q in dom.get("lt_params", []):
        qv = inp.get(q)
        # qv <= 0 ⇒ no valid node ids, so any reference is out of domain.
        if isinstance(qv, int) and not isinstance(qv, bool) and \
                any(not (0 <= x < qv) for x in _endpoint_ints(m)):
            return False
    return True


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def _key(inp: dict) -> str:
    return json.dumps(inp, sort_keys=True, default=str)


@dataclass
class Candidate:
    input: dict
    origin: str            # "seed" | "edge" | "fuzz" | "stress"
    protected: bool = False  # always keep in the final suite (edges + stress)


def generate_candidates(params: list[dict], seeds: list[dict],
                        bounds: dict, cfg: GenConfig,
                        validator: Optional[Callable[[dict], bool]] = None
                        ) -> list[Candidate]:
    """Produce de-duplicated candidate inputs (T1 ∪ T3 ∪ T4; T2 folds into bounds).

    ``validator``, if given, is a predicate ``inp_dict -> bool`` that returns True
    iff the input satisfies the problem's *stated* constraints (typically the
    machine-generated ``content/problems/<slug>/input_validator/input_validator.py``). Any candidate
    it rejects is dropped, so an out-of-domain input can never become a baked hidden
    test that unfairly fails a correct solution. This is the general fairness gate;
    it runs alongside (and after) the mechanical length/invariant/graph guards below,
    which stay as a cheap first pass. A too-strict validator only loses coverage
    (never injects an illegal input), so the gate is safe-in-one-direction."""
    rng = random.Random(cfg.seed)
    cands: list[Candidate] = []
    seen: set[str] = set()

    # Parsed minimum length for each array/string param (from `2 <= len(nums)`
    # etc.). Generators otherwise happily emit `[]`/singletons; baking an
    # out-of-domain input as a required hidden test would unfairly fail a correct
    # solution written to the stated contract. TreeNode is excluded: its level-
    # order array length is not the node count, so a size bound wouldn't map.
    size_lo: dict[str, int] = {}
    for _p in params:
        _base, _dims = parse_type(_p["type"])
        if _base == "TreeNode" or (_dims == 0 and _base != "string"):
            continue
        _lo, _ = C.size_bounds(bounds, _p["name"])
        if _lo is not None and _lo > 0:
            size_lo[_p["name"]] = _lo

    # Structural invariants learned from each 1-D int-array param's own examples
    # (sorted / permutation / rotated-sorted). See learn_array_invariants above.
    invariants: dict[str, set[str]] = {}
    for _p in params:
        _base, _dims = parse_type(_p["type"])
        if _dims == 1 and _base in ("int", "integer", "num"):
            vals = [s[_p["name"]] for s in seeds if _p["name"] in s]
            got = learn_array_invariants(vals)
            if got:
                invariants[_p["name"]] = got

    # Node-label domains for int[][] edge/adjacency params (the "A+" graph guard).
    _INT_BASES = ("int", "integer", "num")
    scalar_int_names = [p["name"] for p in params
                        if parse_type(p["type"])[1] == 0
                        and parse_type(p["type"])[0] in _INT_BASES]
    imdomains: dict[str, dict] = {}
    for _p in params:
        _b, _dims = parse_type(_p["type"])
        if _dims == 2 and _b in _INT_BASES:
            _name = _p["name"]
            _rows = [s for s in seeds if isinstance(s.get(_name), list)]
            _mats = [s[_name] for s in _rows]
            _scal = {q: [s[q] for s in _rows]
                     for q in scalar_int_names
                     if _rows and all(isinstance(s.get(q), int)
                                      and not isinstance(s.get(q), bool) for s in _rows)}
            _dom = learn_intmatrix_domain(_name, _mats, _scal)
            if _dom:
                imdomains[_name] = _dom

    def _in_domain(inp: dict) -> bool:
        for name, lo in size_lo.items():
            v = inp.get(name)
            if isinstance(v, (list, str)) and len(v) < lo:
                return False
        for name, inv in invariants.items():
            v = inp.get(name)
            if isinstance(v, list) and not array_satisfies(v, inv):
                return False
        for name, dom in imdomains.items():
            v = inp.get(name)
            if isinstance(v, list) and not intmatrix_satisfies(v, dom, inp):
                return False
        # General stated-constraint gate (validate_input). Runs last: the cheap
        # mechanical guards above have already dropped the obvious out-of-domain
        # shapes, so this only adjudicates what they can't express.
        if validator is not None and not validator(inp):
            return False
        return True

    def emit(inp: dict, origin: str, protected: bool = False) -> None:
        if not _in_domain(inp):
            return
        k = _key(inp)
        if k in seen:
            return
        seen.add(k)
        cands.append(Candidate(input=inp, origin=origin, protected=protected))

    def eb(p: dict) -> tuple[Optional[int], Optional[int]]:
        base, dims = parse_type(p["type"])
        name = p["name"]
        if dims == 0 and base not in _RICH_ARRAY_BASES:
            lo, hi = C.scalar_bounds(bounds, name)
        else:
            lo, hi = C.elem_bounds(bounds, name)
        return lo, hi

    # Detect "operations" params (design/streaming) and learn their vocab.
    ops_vocab: dict[str, _OpVocab] = {}
    for p in params:
        obs = [s[p["name"]] for s in seeds if p["name"] in s]
        if obs and _is_ops(obs):
            ops_vocab[p["name"]] = _learn_ops(obs)

    def gen_param(p: dict, size: int, small_ints: bool = True):
        name = p["name"]
        if name in ops_vocab:
            return _gen_ops_seq(rng, ops_vocab[name], rng.randint(1, max(2, size)),
                                small_ints)
        base, dims = parse_type(p["type"])
        lo, hi = eb(p)
        return _rand_value(rng, base, dims, lo, hi, size)

    def a_small_input() -> dict:
        return {p["name"]: gen_param(p, rng.randint(1, 4)) for p in params}

    # T1 — edges: vary one param to each edge shape, others small-random.
    for p in params:
        name = p["name"]
        if name in ops_vocab:
            evs = _ops_edges(rng, ops_vocab[name])
        else:
            lo, hi = eb(p)
            evs = edge_values(p["type"], lo, hi)
        for ev in evs:
            inp = a_small_input()
            inp[name] = copy.deepcopy(ev)
            emit(inp, "edge", protected=True)

    # Existing examples as seeds + their perturbations (T3). Op-sequence params
    # (design/streaming) must NOT go through _mutate_json: it flips characters
    # inside operation-name strings ("findMedian" -> "fbndMedian"), producing an
    # out-of-domain op the canonical only handles by accident — an unfair test.
    # Regenerate those from the learned vocabulary instead.
    for s in seeds:
        emit(copy.deepcopy(s), "seed", protected=True)
        for _ in range(cfg.n_seed_mut):
            m = {}
            for k, v in s.items():
                if k in ops_vocab:
                    length = len(v) if isinstance(v, list) and v else 4
                    m[k] = _gen_ops_seq(rng, ops_vocab[k], rng.randint(1, max(2, length)))
                else:
                    m[k] = _mutate_json(rng, copy.deepcopy(v))
            emit(m, "fuzz")

    # T3 — small random fuzz.
    for _ in range(cfg.n_fuzz):
        emit({p["name"]: gen_param(p, cfg.fuzz_size) for p in params}, "fuzz")

    # T4 — one large-stress input.
    if cfg.include_stress:
        out = {}
        for p in params:
            name = p["name"]
            if name in ops_vocab:
                out[name] = _gen_ops_stress(rng, ops_vocab[name], cfg.stress_n)
            else:
                base, dims = parse_type(p["type"])
                lo, hi = eb(p)
                out[name] = _stress_value(rng, base, dims, lo, hi, cfg.stress_n)
        emit(out, "stress", protected=True)

    # Cap: keep protected (edges/seeds/stress) first, then as many fuzz as fit.
    if len(cands) > cfg.max_candidates:
        protected = [c for c in cands if c.protected]
        rest = [c for c in cands if not c.protected]
        cands = protected + rest[: max(0, cfg.max_candidates - len(protected))]
    return cands
