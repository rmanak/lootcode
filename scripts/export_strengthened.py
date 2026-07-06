#!/usr/bin/env python3
"""Export newly generated (but not yet applied) hidden test cases to a JSONL file.

Runs the full strengthen pipeline in dry-run mode and writes every selected
case to a single JSONL file so we can inspect, diff, or review before applying.

Each JSONL line is one problem with sufficient metadata to identify it and its
selected cases:

    {
      "slug": "median-from-data-stream",
      "title": "Median from Data Stream",
      "difficulty": "hard",
      "compare": "exact",
      "params": [{"name": "operations", "type": "int[][]"}],
      "return_type": "int[]",
      "status": "ok",
      "n_candidates": 140,
      "n_valid": 132,
      "n_mutants": 18,
      "n_pop": 4,
      "killable": 22,
      "killed_before": 10,
      "killed_after": 20,
      "pop_killable": 1,
      "pop_caught_before": 0,
      "pop_caught_after": 1,
      "survivors": ["mut:cmp:<->>="],
      "elapsed_s": 1.23,
      "selected": [
        {
          "name": "gen-1",
          "input": {"operations": [["addNum", 1], ["findMedian"]]},
          "expected": [1],
          "weight": 1,
          "hidden": true,
          "_origin": "fuzz",
          "_kills": 5
        },
        ...
      ]
    }

Problems with status "skip" or "error" are also emitted (with an empty
"selected" array and an "error" field) so nothing is silently dropped.

Usage:
    python scripts/export_strengthened.py output.jsonl
    python scripts/export_strengthened.py --filter tree tree-cases.jsonl
    python scripts/export_strengthened.py -j 8 --fuzz 1500 bank.jsonl
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app import content  # noqa: E402
from app.testgen import GenConfig  # noqa: E402
from scripts.strengthen_tests import (  # noqa: E402
    Report,
    _print,
    _work,
    strengthen,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("output", help="JSONL file to write selected cases to")
    ap.add_argument("slugs", nargs="*", help="only these slugs (default: all)")
    ap.add_argument("--filter", help="only slugs containing this substring")
    ap.add_argument("-j", "--jobs", type=int, default=1, help="problems in parallel")
    ap.add_argument("--verbose", action="store_true", help="print per-problem report")
    ap.add_argument("--cap", type=int, default=12, help="max new cases per problem")
    ap.add_argument("--mut-cap", type=int, default=60, help="max mutants per problem")
    ap.add_argument("--fuzz", type=int, default=80, help="random fuzz inputs")
    ap.add_argument("--no-stress", action="store_true", help="skip the T4 stress case")
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--mutants", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--population", action=argparse.BooleanOptionalAction, default=True)
    args = ap.parse_args()

    if not args.mutants and not args.population:
        ap.error("nothing to select against: pass at least one of --mutants/--population")

    all_probs = content.load_all()
    by_slug = {p["slug"]: p for p in all_probs}

    if args.slugs:
        probs = [by_slug[s] for s in args.slugs if s in by_slug]
        for s in args.slugs:
            if s not in by_slug:
                print(f"[ERROR] unknown slug: {s}")
    elif args.filter:
        probs = [p for p in all_probs if args.filter in p["slug"]]
    else:
        probs = all_probs

    cfg = GenConfig(
        n_fuzz=args.fuzz,
        max_candidates=max(140, args.fuzz + 60),
        seed=args.seed,
        include_stress=not args.no_stress,
    )

    out_path = pathlib.Path(args.output)
    reports: list[Report] = []
    t0 = time.time()

    if args.jobs > 1:
        jobs = [(p, cfg, args.cap, args.mut_cap, args.mutants, args.population)
                for p in probs]
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            for rep in ex.map(_work, jobs):
                reports.append(rep)
                if args.verbose:
                    _print(rep, True)
    else:
        for p in probs:
            rep = strengthen(p, cfg, args.cap, args.mut_cap,
                             use_mutants=args.mutants, use_population=args.population)
            reports.append(rep)
            if args.verbose:
                _print(rep, True)

    # Build a slug -> problem lookup for metadata enrichment
    slug_meta = {p["slug"]: p for p in probs}

    # Write JSONL
    with open(out_path, "w", encoding="utf-8") as f:
        for rep in reports:
            meta = slug_meta.get(rep.slug, {})
            line = {
                "slug": rep.slug,
                "title": meta.get("title", ""),
                "difficulty": rep.difficulty,
                "compare": meta.get("compare", "exact"),
                "params": meta.get("params", []),
                "return_type": meta.get("return_type", ""),
                "status": rep.status,
                "n_candidates": rep.n_candidates,
                "n_valid": rep.n_valid,
                "n_mutants": rep.n_mutants,
                "n_pop": rep.n_pop,
                "killable": rep.killable,
                "killed_before": rep.killed_before,
                "killed_after": rep.killed_after,
                "pop_killable": rep.pop_killable,
                "pop_caught_before": rep.pop_caught_before,
                "pop_caught_after": rep.pop_caught_after,
                "survivors": rep.survivors,
                "elapsed_s": round(rep.elapsed_s, 2),
                "selected": rep.selected,
            }
            if rep.error:
                line["error"] = rep.error
            f.write(json.dumps(line, default=str) + "\n")

    ok = [r for r in reports if r.status == "ok"]
    added = sum(len(r.selected) for r in ok)
    print(f"\n{len(ok)} problems processed, {added} cases exported to {out_path}, "
          f"{time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
