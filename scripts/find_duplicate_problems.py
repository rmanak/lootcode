#!/usr/bin/env python3
"""Find candidate duplicate problems across the whole bank, using content.

Where ``scripts/find_duplicate_slugs.py`` looks at nothing but the directory
name, this reads what each problem actually *is* — statement, signature, test
cases, canonical solution — and unions several independent heuristics into one
high-recall candidate list for a human to confirm. It is a triage tool: tuned
for recall, so false positives are expected and the report shows, per pair,
which signals fired and how strongly.

Signals (each can nominate a pair on its own):

  name    IDF-weighted cosine over stemmed slug+title tokens (the existing
          ``find_similar_problems`` heuristic, applied pairwise to the bank).
  stmt    TF-IDF cosine over the normalized problem statement (problem.md).
  fname   Identical solver function name (``twoSum``), which is
          LeetCode-specific enough to be strong evidence on its own; plus a
          weaker "same parameter types + same return type" shape match.
  tests   Overlap of stored test-case inputs (and input→expected pairs) —
          near-conclusive when two problems literally grade the same data.
  sol     Shingle overlap of the canonical solution's *structure* (AST with all
          identifiers erased), which survives renaming and reformatting.
  behav   Behavioral fingerprint for the "one integer in → scalar out" family:
          run the canonical over n = 0..K and hash the output sequence. Two
          problems that reduce to each other emit the same sequence regardless
          of wording (climbing stairs ↔ compositions of {1,2} ↔ Fibonacci).

Usage:
    python scripts/find_duplicate_problems.py                    # -> duplicate_candidates.txt
    python scripts/find_duplicate_problems.py -o cands.txt --json cands.json
    python scripts/find_duplicate_problems.py --no-behavioral    # skip running canonicals
"""
from __future__ import annotations

import argparse
import ast
import json
import math
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.problem_validation import _STOPWORDS, _raw_tokens, _stem  # noqa: E402

DEFAULT_ROOTS = [
    REPO_ROOT / "content" / "problems",
    REPO_ROOT / "content" / "problems-extended",
]

# Function names too generic to mean anything on their own.
GENERIC_FN_NAMES = {"solve", "solution", "main", "run", "compute", "answer"}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
@dataclass
class Problem:
    slug: str
    root: str
    title: str = ""
    difficulty: str = ""
    tags: list[str] = field(default_factory=list)
    kind: str = "function"
    fn_name: str = ""
    param_types: tuple[str, ...] = ()
    return_type: str = ""
    method_names: tuple[str, ...] = ()
    statement: str = ""
    solution: str = ""
    inputs: set[str] = field(default_factory=set)        # hashes of test inputs
    io_pairs: set[str] = field(default_factory=set)      # hashes of (input, expected)
    name_tokens: set[str] = field(default_factory=set)
    stmt_tf: dict[str, int] = field(default_factory=dict)
    sol_shingles: set[str] = field(default_factory=set)
    behav: str = ""                                       # fingerprint or ""


def _canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def load_problem(d: Path, root_name: str) -> Problem | None:
    meta_path = d / "meta.json"
    if not meta_path.is_file():
        return None
    try:
        meta = json.loads(meta_path.read_text())
    except Exception:
        return None

    p = Problem(slug=d.name, root=root_name)
    p.title = meta.get("title") or ""
    p.difficulty = meta.get("difficulty") or ""
    p.tags = list(meta.get("tags") or meta.get("topics") or [])
    fn = meta.get("function") or {}
    cls = meta.get("class") or {}
    if cls:
        p.kind = "class"
        p.fn_name = cls.get("name") or ""
        p.param_types = tuple((q.get("type") or "") for q in (cls.get("params") or []))
        p.method_names = tuple(sorted((m.get("name") or "")
                                      for m in (cls.get("methods") or [])))
    else:
        p.fn_name = fn.get("name") or ""
        p.param_types = tuple((q.get("type") or "") for q in (fn.get("params") or []))
        p.return_type = (fn.get("returns") or {}).get("type") or ""

    md = d / "problem.md"
    if md.is_file():
        p.statement = md.read_text(errors="replace")
    sol = d / "solution" / "solution.py"
    if sol.is_file():
        p.solution = sol.read_text(errors="replace")

    cases_path = d / "tests" / "cases.json"
    if cases_path.is_file():
        try:
            cases = json.loads(cases_path.read_text()).get("cases") or []
        except Exception:
            cases = []
        for c in cases:
            inp = _canon(c.get("input"))
            p.inputs.add(inp)
            p.io_pairs.add(_canon([c.get("input"), c.get("expected")]))
    return p


def load_bank(roots: list[Path]) -> list[Problem]:
    out: list[Problem] = []
    for root in roots:
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            p = load_problem(child, root.name)
            if p is not None:
                out.append(p)
    return out


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------
_MD_NOISE = re.compile(r"```.*?```", re.S)
_CONSTRAINTS = re.compile(r"^#+\s*constraints\b.*?(?=^#|\Z)", re.S | re.M | re.I)


def statement_tokens(text: str, drop_examples: bool = False) -> dict[str, int]:
    """Bag of stemmed content words for a statement.

    Constraints sections are dropped (they are near-identical boilerplate across
    the bank and would inflate every pair's similarity); fenced example blocks
    are kept, since a shared worked example is real evidence.
    """
    text = _CONSTRAINTS.sub(" ", text)
    if drop_examples:
        text = _MD_NOISE.sub(" ", text)
    tf: dict[str, int] = {}
    for w in _raw_tokens(text):
        if w in _STOPWORDS or len(w) <= 1:
            continue
        s = _stem(w)
        tf[s] = tf.get(s, 0) + 1
    return tf


class _IdentityEraser(ast.NodeTransformer):
    """Rewrite every identifier/constant to a placeholder, keeping structure."""

    def visit_Name(self, node):  # noqa: N802
        return ast.copy_location(ast.Name(id="_", ctx=node.ctx), node)

    def visit_arg(self, node):  # noqa: N802
        node.arg = "_"
        node.annotation = None
        return node

    def visit_Attribute(self, node):  # noqa: N802
        self.generic_visit(node)
        node.attr = "_"
        return node

    def visit_Constant(self, node):  # noqa: N802
        return ast.copy_location(ast.Constant(value=0), node)

    def visit_FunctionDef(self, node):  # noqa: N802
        self.generic_visit(node)
        node.name = "_"
        node.decorator_list = []
        # drop docstring
        if (node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)):
            node.body = node.body[1:] or [ast.Pass()]
        return node

    def visit_ClassDef(self, node):  # noqa: N802
        self.generic_visit(node)
        node.name = "_"
        return node


def solution_shingles(src: str, k: int = 6) -> set[str]:
    """k-gram shingles over the identifier-erased AST node stream."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()
    tree = _IdentityEraser().visit(tree)
    ast.fix_missing_locations(tree)
    stream = [type(n).__name__ for n in ast.walk(tree)]
    # ast.walk is BFS: stable enough for structural comparison, and cheap.
    if len(stream) < k:
        return {"|".join(stream)} if stream else set()
    return {"|".join(stream[i:i + k]) for i in range(len(stream) - k + 1)}


# ---------------------------------------------------------------------------
# Behavioral fingerprint (Stage 2 of docs/duplicate-detection-plan.md)
# ---------------------------------------------------------------------------
SCALAR_IN = {"int"}
SCALAR_OUT = {"int", "float", "bool", "string", "str"}

_PROBE = r"""
import json, sys
sys.setrecursionlimit(10000)
ns = {}
exec(open(sys.argv[1]).read(), ns)
fn = ns[sys.argv[2]]
out = []
for n in range(int(sys.argv[3])):
    try:
        out.append(fn(n))
    except Exception:
        out.append(None)
print(json.dumps(out, default=str))
"""


def behavioral_fp(p: Problem, upto: int = 16, timeout: int = 10) -> str:
    """Hash of canonical(n) for n = 0..upto-1, for one-int-in/scalar-out problems.

    Returns "" when the problem's shape doesn't fit or the probe fails. Runs the
    repo's *own* canonical solutions (trusted content), one short subprocess per
    problem, with a timeout.
    """
    if p.kind != "function" or len(p.param_types) != 1:
        return ""
    if p.param_types[0] not in SCALAR_IN or p.return_type not in SCALAR_OUT:
        return ""
    sol = REPO_ROOT / "content" / p.root / p.slug / "solution" / "solution.py"
    if not sol.is_file():
        return ""
    probe = REPO_ROOT / "scratchpad" / ".probe_behavioral.py"
    probe.parent.mkdir(exist_ok=True)
    probe.write_text(_PROBE)
    try:
        r = subprocess.run(
            [sys.executable, str(probe), str(sol), p.fn_name, str(upto)],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return ""
    if r.returncode != 0 or not r.stdout.strip():
        return ""
    try:
        seq = json.loads(r.stdout)
    except Exception:
        return ""
    if all(v is None for v in seq):
        return ""
    # Constant / all-equal sequences carry no information.
    if len({_canon(v) for v in seq}) <= 1:
        return ""
    return _canon(seq)


# ---------------------------------------------------------------------------
# Pairwise similarity
# ---------------------------------------------------------------------------
def _cosine_pairs(docs: dict[str, dict[str, float]], min_score: float,
                  max_df_frac: float = 0.25) -> dict[tuple[str, str], float]:
    """Sparse cosine over weighted bags, via an inverted index.

    Terms appearing in more than ``max_df_frac`` of the corpus are dropped: they
    contribute almost nothing after IDF weighting but dominate the pair blowup.
    """
    n = len(docs)
    df: dict[str, int] = defaultdict(int)
    for bag in docs.values():
        for t in bag:
            df[t] += 1
    keep = {t for t, c in df.items() if c <= max(2, int(max_df_frac * n))}

    norms: dict[str, float] = {}
    weighted: dict[str, dict[str, float]] = {}
    for slug, bag in docs.items():
        w = {}
        for t, v in bag.items():
            idf = math.log((n + 1) / (df[t] + 1)) + 1.0
            w[t] = v * idf
        norms[slug] = math.sqrt(sum(x * x for x in w.values())) or 1.0
        weighted[slug] = w

    index: dict[str, list[str]] = defaultdict(list)
    for slug, w in weighted.items():
        for t in w:
            if t in keep:
                index[t].append(slug)

    dots: dict[tuple[str, str], float] = defaultdict(float)
    for t, members in index.items():
        if len(members) < 2:
            continue
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                a, b = members[i], members[j]
                key = (a, b) if a < b else (b, a)
                dots[key] += weighted[a][t] * weighted[b][t]

    out = {}
    for (a, b), dot in dots.items():
        s = dot / (norms[a] * norms[b])
        if s >= min_score:
            out[(a, b)] = s
    return out


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


ROMAN = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"}


def variant_base(slug: str) -> str:
    parts = slug.split("-")
    if len(parts) > 1 and (parts[-1] in ROMAN or parts[-1].isdigit()):
        return "-".join(parts[:-1])
    return slug


def is_variant_pair(a: str, b: str) -> bool:
    return a != b and variant_base(a) == variant_base(b)


def build_candidates(probs: list[Problem], args) -> list[dict]:
    by_slug = {p.slug: p for p in probs}
    cand: dict[tuple[str, str], dict] = {}

    def note(a: str, b: str, signal: str, score: float, detail: str = "") -> None:
        key = (a, b) if a < b else (b, a)
        rec = cand.setdefault(key, {"a": key[0], "b": key[1], "signals": {},
                                    "details": {}})
        if score > rec["signals"].get(signal, 0.0):
            rec["signals"][signal] = score
            if detail:
                rec["details"][signal] = detail

    # --- name (slug + title) -------------------------------------------------
    name_docs = {p.slug: dict.fromkeys(p.name_tokens, 1.0) for p in probs}
    for (a, b), s in _cosine_pairs(name_docs, args.min_name, max_df_frac=0.10).items():
        note(a, b, "name", s)

    # --- statement -----------------------------------------------------------
    stmt_docs = {p.slug: {t: 1.0 + math.log(c) for t, c in p.stmt_tf.items()}
                 for p in probs if p.stmt_tf}
    for (a, b), s in _cosine_pairs(stmt_docs, args.min_stmt).items():
        note(a, b, "stmt", s)

    # --- function name / signature ------------------------------------------
    by_fn: dict[str, list[str]] = defaultdict(list)
    by_sig: dict[tuple, list[str]] = defaultdict(list)
    for p in probs:
        if p.fn_name and p.fn_name.lower() not in GENERIC_FN_NAMES:
            by_fn[p.fn_name.lower()].append(p.slug)
        if p.kind == "function" and p.param_types:
            by_sig[(p.param_types, p.return_type)].append(p.slug)
    for fn, members in by_fn.items():
        if 1 < len(members) <= 12:
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    note(members[i], members[j], "fname", 1.0, f"both '{fn}'")
    # Same signature shape is weak on its own; only record it for pairs some
    # other signal already nominated (handled below).

    # --- tests ---------------------------------------------------------------
    input_index: dict[str, list[str]] = defaultdict(list)
    for p in probs:
        for h in p.inputs:
            input_index[h].append(p.slug)
    seen_pairs: set[tuple[str, str]] = set()
    for _h, members in input_index.items():
        if len(members) < 2 or len(members) > 30:
            continue  # a trivial input ([] , 0, "") shared bank-wide means nothing
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                a, b = members[i], members[j]
                key = (a, b) if a < b else (b, a)
                seen_pairs.add(key)
    for a, b in seen_pairs:
        pa, pb = by_slug[a], by_slug[b]
        ji = _jaccard(pa.inputs, pb.inputs)
        jio = _jaccard(pa.io_pairs, pb.io_pairs)
        shared_io = len(pa.io_pairs & pb.io_pairs)
        if ji >= args.min_tests or shared_io >= 2:
            note(a, b, "tests", max(ji, jio),
                 f"shared inputs={len(pa.inputs & pb.inputs)}/"
                 f"{min(len(pa.inputs), len(pb.inputs))}, shared io={shared_io}")

    # --- canonical solution structure ---------------------------------------
    sol_docs = {p.slug: dict.fromkeys(p.sol_shingles, 1.0)
                for p in probs if len(p.sol_shingles) >= 8}
    for (a, b), s in _cosine_pairs(sol_docs, args.min_sol, max_df_frac=0.05).items():
        note(a, b, "sol", s)

    # --- behavioral fingerprint ---------------------------------------------
    fp_index: dict[str, list[str]] = defaultdict(list)
    for p in probs:
        if p.behav:
            fp_index[p.behav].append(p.slug)
    for fp, members in fp_index.items():
        if len(members) < 2:
            continue
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                note(members[i], members[j], "behav", 1.0,
                     f"identical f(0..15) = {fp[:60]}")

    # --- combine -------------------------------------------------------------
    results = []
    for (a, b), rec in cand.items():
        pa, pb = by_slug[a], by_slug[b]
        sig = rec["signals"]
        # Weighted union: any strong signal alone is enough to shortlist.
        score = (
            1.00 * sig.get("tests", 0.0)
            + 0.90 * sig.get("behav", 0.0)
            + 0.80 * sig.get("stmt", 0.0)
            + 0.70 * sig.get("name", 0.0)
            + 0.60 * sig.get("fname", 0.0)
            + 0.50 * sig.get("sol", 0.0)
        )
        same_shape = (pa.kind == pb.kind and pa.param_types == pb.param_types
                      and pa.return_type == pb.return_type)
        if same_shape:
            score += 0.15
        shared_tags = set(pa.tags) & set(pb.tags)
        score += 0.05 * len(shared_tags)
        rec.update({
            "score": score,
            "same_shape": same_shape,
            "shared_tags": sorted(shared_tags),
            "variant": is_variant_pair(a, b),
            "title_a": pa.title, "title_b": pb.title,
            "root_a": pa.root, "root_b": pb.root,
            "n_signals": len(sig),
        })
        results.append(rec)

    results.sort(key=lambda r: (-r["score"], r["a"], r["b"]))
    return results


# ---------------------------------------------------------------------------
def render(results: list[dict], probs: list[Problem]) -> str:
    lines = [
        "# Candidate duplicate problems (content-based heuristics, high recall)",
        f"# problems scanned: {len(probs)}   candidate pairs: {len(results)}",
        "# signals: tests=shared test data, behav=identical f(0..15) sequence,",
        "#          stmt=statement TF-IDF cosine, name=slug/title IDF cosine,",
        "#          fname=same solver function name, sol=canonical AST shingles",
        "# NOT a verdict — every pair here still needs a human read.",
        "",
    ]
    for r in results:
        sig = ", ".join(f"{k}={v:.2f}" for k, v in
                        sorted(r["signals"].items(), key=lambda kv: -kv[1]))
        flags = []
        if r["variant"]:
            flags.append("numeral-variant")
        if r["same_shape"]:
            flags.append("same-signature")
        lines.append(f"{r['score']:.2f}  {r['a']}  <->  {r['b']}")
        lines.append(f"        {r['title_a']}  |  {r['title_b']}")
        lines.append(f"        [{sig}]" + (f"  ({', '.join(flags)})" if flags else ""))
        for k, d in r["details"].items():
            lines.append(f"        {k}: {d}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--content-dir", action="append", type=Path)
    p.add_argument("-o", "--output", type=Path,
                   default=REPO_ROOT / "duplicate_candidates.txt")
    p.add_argument("--json", type=Path, help="also write the raw candidate records")
    p.add_argument("--min-name", type=float, default=0.45)
    p.add_argument("--min-stmt", type=float, default=0.42)
    p.add_argument("--min-sol", type=float, default=0.55)
    p.add_argument("--min-tests", type=float, default=0.20)
    p.add_argument("--no-behavioral", action="store_true",
                   help="skip running canonical solutions for the n=0..15 probe")
    p.add_argument("--limit", type=int, default=0, help="cap the report to N pairs")
    args = p.parse_args()

    roots = args.content_dir or DEFAULT_ROOTS
    probs = load_bank(roots)
    print(f"loaded {len(probs)} problems", file=sys.stderr)

    for pr in probs:
        pr.name_tokens = {_stem(w) for w in _raw_tokens(pr.slug + " " + pr.title)
                          if w not in _STOPWORDS}
        pr.stmt_tf = statement_tokens(pr.statement)
        pr.sol_shingles = solution_shingles(pr.solution)

    if not args.no_behavioral:
        n_fp = 0
        for pr in probs:
            pr.behav = behavioral_fp(pr)
            if pr.behav:
                n_fp += 1
        print(f"behavioral fingerprints: {n_fp}", file=sys.stderr)

    results = build_candidates(probs, args)
    if args.limit:
        results = results[:args.limit]

    args.output.write_text(render(results, probs))
    if args.json:
        args.json.write_text(json.dumps(results, indent=2))
    print(f"wrote {len(results)} candidate pairs to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
