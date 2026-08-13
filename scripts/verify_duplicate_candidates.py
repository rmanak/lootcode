#!/usr/bin/env python3
"""Verify candidate duplicate pairs by *cross-executing* their canonical solutions.

Input is the JSON produced by ``scripts/find_duplicate_problems.py --json``.
For each candidate pair whose signatures are compatible (same kind, same param
types in the same order, same return type — plus, for class problems, the same
method set), this runs

    A's canonical solution  against  B's tests      (aliased to B's entry point)
    B's canonical solution  against  A's tests

through the ordinary sandboxed grading path (:func:`app.executor.run_submission`),
the same one ``scripts/verify_bank.py`` uses. Verdicts:

    equivalent   both directions pass — the two problems grade the same function,
                 so barring a statement-level difference they are duplicates
    subsumes     one direction passes only — usually a generalization, a
                 differently-constrained variant, or differing param order
    distinct     neither direction passes
    n/a          signatures aren't compatible, so this check can't speak

``distinct`` is not proof of non-duplication (param order, differing return
conventions and stricter constraints all cause it) — it just means this
particular check abstains. ``equivalent`` is the strong result.

Usage:
    python scripts/verify_duplicate_candidates.py cands.json -o verdicts.json -j 8
    python scripts/verify_duplicate_candidates.py cands.json --min-score 0.8
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from types import SimpleNamespace

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app import content  # noqa: E402
from app.executor import problem_view, run_submission  # noqa: E402

ROOTS = [REPO_ROOT / "content" / "problems",
         REPO_ROOT / "content" / "problems-extended"]


def load_bank() -> dict[str, dict]:
    bank: dict[str, dict] = {}
    for root in ROOTS:
        if not root.is_dir():
            continue
        for d in sorted(root.iterdir()):
            if not d.is_dir() or d.name.startswith(".") or not (d / "meta.json").is_file():
                continue
            try:
                p = content.load_problem_dir(d)
            except Exception:  # noqa: S112 - a malformed dir is skipped, not fatal
                continue
            bank[p["slug"]] = p
    return bank


def _tests(p: dict) -> list[SimpleNamespace]:
    return [SimpleNamespace(name=t.get("name", f"t{i}"), input=t.get("input", {}),
                            expected=t.get("expected"), weight=t.get("weight", 1),
                            hidden=t.get("hidden", False))
            for i, t in enumerate(p.get("tests", []))]


def _sig(p: dict) -> tuple:
    params = tuple((q.get("type") or "") for q in (p.get("params") or []))
    methods = tuple(sorted((m.get("name") or "") + ":" +
                           str(len(m.get("params") or []))
                           for m in (p.get("class_methods") or [])))
    return (p.get("kind", "function"), params, p.get("return_type") or "", methods)


def compatible(a: dict, b: dict) -> bool:
    return _sig(a) == _sig(b) and bool(a.get("canonical_solution")) \
        and bool(b.get("canonical_solution")) and bool(a.get("tests")) \
        and bool(b.get("tests"))


def _aliased(code: str, src: dict, dst: dict) -> str:
    """``src``'s canonical, with an alias so it exposes ``dst``'s entry point."""
    if dst.get("kind") == "class":
        a, b = src.get("class_name") or "", dst.get("class_name") or ""
    else:
        a, b = src.get("function_name") or "", dst.get("function_name") or ""
    if a and b and a != b:
        code = f"{code}\n\n{b} = {a}\n"
    return code


def run_one_way(src: dict, dst: dict) -> tuple[int, int, str]:
    """Grade ``src``'s canonical against ``dst``'s tests. -> (passed, total, err)."""
    try:
        graded = run_submission(_aliased(src["canonical_solution"], src, dst),
                                problem_view(dst), _tests(dst))
    except Exception as exc:  # noqa: BLE001
        return 0, len(dst.get("tests") or []), str(exc)[:200]
    return graded.passed_count, graded.total_count, ""


def verify_pair(rec: dict, bank: dict[str, dict]) -> dict:
    a, b = bank.get(rec["a"]), bank.get(rec["b"])
    out = dict(rec)
    if a is None or b is None or not compatible(a, b):
        out["verdict"] = "n/a"
        return out
    pa, ta, ea = run_one_way(a, b)     # A's solution on B's tests
    pb, tb, eb = run_one_way(b, a)     # B's solution on A's tests
    a2b = ta > 0 and pa == ta
    b2a = tb > 0 and pb == tb
    out["a_on_b"] = f"{pa}/{ta}"
    out["b_on_a"] = f"{pb}/{tb}"
    if ea or eb:
        out["exec_error"] = (ea or "") + (" | " + eb if eb else "")
    if a2b and b2a:
        out["verdict"] = "equivalent"
    elif a2b or b2a:
        out["verdict"] = "subsumes"
        out["direction"] = f"{rec['a']} solves {rec['b']}" if a2b \
            else f"{rec['b']} solves {rec['a']}"
    else:
        out["verdict"] = "distinct"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("candidates", type=pathlib.Path)
    ap.add_argument("-o", "--output", type=pathlib.Path, required=True)
    ap.add_argument("-j", "--jobs", type=int, default=8)
    ap.add_argument("--min-score", type=float, default=0.0)
    args = ap.parse_args()

    recs = json.loads(args.candidates.read_text())
    recs = [r for r in recs if r.get("score", 0) >= args.min_score]
    bank = load_bank()
    print(f"bank: {len(bank)} problems; pairs to check: {len(recs)}", file=sys.stderr)

    results: list[dict] = []
    done = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futs = {pool.submit(verify_pair, r, bank): r for r in recs}
        for fut in as_completed(futs):
            results.append(fut.result())
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(recs)}", file=sys.stderr)

    order = {"equivalent": 0, "subsumes": 1, "distinct": 2, "n/a": 3}
    results.sort(key=lambda r: (order[r["verdict"]], -r.get("score", 0)))
    args.output.write_text(json.dumps(results, indent=2))

    counts: dict[str, int] = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print("verdicts: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
