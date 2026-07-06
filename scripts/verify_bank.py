#!/usr/bin/env python3
"""Run every problem's canonical solution against its own tests.

Loads all problems from every configured content root — ``content/problems/`` (the
durable problem bank) plus the optional, gitignored ``content/problems-extended/``
when present — and, for each one, runs its ``canonical_solution`` against its
``tests`` using the
*exact* execution + grading path the app uses (:func:`app.executor.run_submission`)
— the same tooling ``scripts/verify_json.py`` wires up for loose JSON files, only
pointed at the whole on-disk bank instead of a folder of generator output.

Nothing about the sandbox / executor / judge is re-implemented here.

Usage:
    python scripts/verify_bank.py                 # verify the whole bank
    python scripts/verify_bank.py two-sum 3sum    # only these slugs
    python scripts/verify_bank.py --filter tree   # only slugs containing "tree"
    python scripts/verify_bank.py -v              # list each failing test
    python scripts/verify_bank.py -j 8            # run 8 problems in parallel
    python scripts/verify_bank.py -q              # only failures + summary
    python scripts/verify_bank.py --failfast      # stop at the first failure

Exit status is 0 only when every checked problem's canonical solution passes all
of its tests. A problem with no canonical solution is a warning (counted, but not
a failure) unless ``--strict`` is given.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app import content  # noqa: E402
from app.executor import run_submission  # noqa: E402


# ---------------------------------------------------------------------------
# Small ANSI color helper (auto-disabled when output is not a TTY).
# ---------------------------------------------------------------------------
class Palette:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def _wrap(self, code: str, s: str) -> str:
        return f"\033[{code}m{s}\033[0m" if self.enabled else s

    def green(self, s: str) -> str:
        return self._wrap("32", s)

    def red(self, s: str) -> str:
        return self._wrap("31", s)

    def yellow(self, s: str) -> str:
        return self._wrap("33", s)

    def dim(self, s: str) -> str:
        return self._wrap("2", s)

    def bold(self, s: str) -> str:
        return self._wrap("1", s)


@dataclass
class Result:
    """Outcome of verifying one problem's canonical solution."""
    slug: str
    difficulty: str
    kind: str                       # pass | fail | skip | error
    passed: int = 0
    total: int = 0
    runtime_ms: float = 0.0
    error: str | None = None        # populated for kind == "error"
    # (test dict, TestResult) pairs for the FAILED tests only (for --verbose).
    failed_tests: list[tuple[dict, object]] = field(default_factory=list)


def _as_prob(p: dict) -> SimpleNamespace:
    """Build the lightweight problem stand-in run_submission expects (mirrors
    scripts/verify_json.py and the Admin verify endpoint)."""
    return SimpleNamespace(
        function_name=(p.get("function_name") or "").strip(),
        params=p.get("params", []),
        return_type=(p.get("return_type") or "").strip(),
        time_limit_ms=p["time_limit_ms"],
        memory_limit_mb=p["memory_limit_mb"],
        points=p.get("points", 100),
        compare=p.get("compare", "exact"),
    )


def _as_tests(p: dict) -> list[SimpleNamespace]:
    return [
        SimpleNamespace(
            name=t.get("name", f"test-{i + 1}"),
            input=t.get("input", {}),
            expected=t.get("expected"),
            weight=t.get("weight", 1),
            hidden=t.get("hidden", False),
        )
        for i, t in enumerate(p.get("tests", []))
    ]


def evaluate(p: dict) -> Result:
    """Verify one problem. Never raises — failures are captured on the Result."""
    slug = p["slug"]
    difficulty = p.get("difficulty", "?")
    tests = p.get("tests", [])

    if not (p.get("canonical_solution") or "").strip():
        return Result(slug, difficulty, "skip", total=len(tests))

    try:
        graded = run_submission(p["canonical_solution"], _as_prob(p), _as_tests(p))
    except Exception as exc:  # noqa: BLE001 - report any judge/runtime failure per-problem
        return Result(slug, difficulty, "error", total=len(tests), error=str(exc))

    kind = "pass" if graded.solved else "fail"
    failed = []
    if kind == "fail":
        # graded.results is in the same order as tests, so results[i] matches
        # tests[i] (used to show the expected value on wrong answers).
        for i, r in enumerate(graded.results):
            if not r.passed:
                failed.append((tests[i] if i < len(tests) else {}, r))
    return Result(
        slug, difficulty, kind,
        passed=graded.passed_count, total=graded.total_count,
        runtime_ms=graded.runtime_ms, failed_tests=failed,
    )


def _pct(passed: int, total: int) -> int:
    return round(100 * passed / total) if total else 0


def print_result(r: Result, c: Palette, args) -> None:
    """Print one problem's line (respecting -q/--quiet and -v/--verbose)."""
    if r.kind == "pass":
        if args.quiet:
            return
        timing = c.dim(f"{r.runtime_ms:.0f}ms")
        print(f"{c.green('[PASS] ')} {r.slug}: {r.passed}/{r.total} {timing}")
        return

    if r.kind == "skip":
        if args.quiet:
            return
        print(f"{c.yellow('[SKIP] ')} {r.slug}: no canonical solution")
        return

    if r.kind == "error":
        print(f"{c.red('[ERROR]')} {r.slug}: could not run — {r.error}")
        return

    # fail
    print(f"{c.red('[FAIL] ')} {r.slug} ({r.difficulty}): "
          f"{r.passed}/{r.total} passed ({_pct(r.passed, r.total)}%)")
    if args.verbose:
        for test, res in r.failed_tests:
            line = f"           - {res.name} [{res.status}]"
            if res.error:
                line += f": {res.error}"
            print(line)
            if res.status == "wrong":
                print(f"               expected={json.dumps(test.get('expected'))}")
                print(f"               actual  ={json.dumps(res.returned)}")


def print_summary(results: list[Result], elapsed: float, c: Palette, args) -> None:
    by_kind = {"pass": [], "fail": [], "skip": [], "error": []}
    for r in results:
        by_kind[r.kind].append(r)

    tests_total = sum(r.total for r in results)
    tests_passed = sum(r.passed for r in results)

    n_pass, n_fail = len(by_kind["pass"]), len(by_kind["fail"])
    n_skip, n_error = len(by_kind["skip"]), len(by_kind["error"])

    print("\n" + "=" * 70)
    print(c.bold(f"Summary — {len(results)} problem(s) checked in {elapsed:.1f}s"))
    print(
        f"  {c.green(f'{n_pass} passed')}   "
        f"{c.red(f'{n_fail} failed')}   "
        f"{c.yellow(f'{n_skip} no-canonical')}   "
        f"{c.red(f'{n_error} errored')}"
    )
    print(f"  test cases: {tests_passed}/{tests_total} passed "
          f"({_pct(tests_passed, tests_total)}%)")

    # Where the failures land, by difficulty (only when there are any).
    broken = by_kind["fail"] + by_kind["error"]
    if broken:
        by_diff: dict[str, int] = {}
        for r in broken:
            by_diff[r.difficulty] = by_diff.get(r.difficulty, 0) + 1
        order = {"easy": 0, "medium": 1, "hard": 2}
        parts = ", ".join(f"{n} {d}" for d, n in
                          sorted(by_diff.items(), key=lambda kv: order.get(kv[0], 9)))
        print(f"  broken by difficulty: {parts}")

    if by_kind["error"]:
        print(c.red("\nProblems that could not run:"))
        for r in by_kind["error"]:
            print(f"  - {r.slug}: {r.error}")

    if by_kind["fail"]:
        print(c.red("\nFailing canonical solutions:"))
        for r in sorted(by_kind["fail"], key=lambda r: r.slug):
            print(f"  - {r.slug} ({r.difficulty}): "
                  f"{r.passed}/{r.total} ({_pct(r.passed, r.total)}%)")

    if by_kind["skip"] and not args.quiet:
        print(c.yellow(f"\nProblems with no canonical solution ({n_skip}):"))
        for r in sorted(by_kind["skip"], key=lambda r: r.slug):
            print(f"  - {r.slug}")

    # Slowest problems — handy for spotting solutions creeping toward the TLE.
    if args.slowest > 0:
        ran = [r for r in results if r.kind in ("pass", "fail")]
        ran.sort(key=lambda r: r.runtime_ms, reverse=True)
        if ran:
            print(c.dim(f"\nSlowest {min(args.slowest, len(ran))}:"))
            for r in ran[:args.slowest]:
                print(c.dim(f"  {r.runtime_ms:7.0f}ms  {r.slug}"))


def select_problems(args) -> list[dict]:
    # No --content-dir: verify every configured root (content/problems/ plus the
    # optional content/problems-extended/). An explicit --content-dir verifies just
    # that one dir.
    if args.content_dir is not None:
        problems = content.load_all(args.content_dir)
    else:
        problems = content.load_all_roots()
    if args.slugs:
        wanted = set(args.slugs)
        found = {p["slug"] for p in problems}
        for missing in sorted(wanted - found):
            print(f"warning: no such problem slug: {missing}", file=sys.stderr)
        problems = [p for p in problems if p["slug"] in wanted]
    if args.filter:
        problems = [p for p in problems if args.filter in p["slug"]]
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("slugs", nargs="*",
                    help="restrict to these exact problem slugs (default: whole bank)")
    ap.add_argument("--filter", metavar="SUBSTR",
                    help="restrict to slugs containing this substring")
    ap.add_argument("--content-dir", type=pathlib.Path, default=None,
                    help="verify just this one problem bank dir (default: all "
                         "configured roots — content/problems/ plus the optional "
                         "content/problems-extended/)")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="for failing problems, list each failing test (status/expected/actual)")
    ap.add_argument("-q", "--quiet", action="store_true",
                    help="suppress per-problem PASS/SKIP lines; show only failures + summary")
    ap.add_argument("-j", "--jobs", type=int, default=1, metavar="N",
                    help="verify N problems in parallel (default: 1)")
    ap.add_argument("--failfast", action="store_true",
                    help="stop after the first failing/erroring problem (forces -j 1)")
    ap.add_argument("--strict", action="store_true",
                    help="treat a missing canonical solution as a failure (exit non-zero)")
    ap.add_argument("--slowest", type=int, default=5, metavar="N",
                    help="show the N slowest problems in the summary (0 to hide)")
    ap.add_argument("--no-color", action="store_true", help="disable colored output")
    args = ap.parse_args(argv)

    c = Palette(enabled=not args.no_color and sys.stdout.isatty())

    problems = select_problems(args)
    if not problems:
        print("No problems to verify.")
        return 0

    where = args.content_dir or "content/problems (+ extended, if present)"
    print(c.bold(f"Verifying {len(problems)} problem(s) from {where}"
                 f"{f' with {args.jobs} workers' if args.jobs > 1 else ''}...\n"))

    results: list[Result] = []
    start = time.perf_counter()
    aborted = False

    if args.failfast or args.jobs <= 1:
        for p in problems:
            r = evaluate(p)
            results.append(r)
            print_result(r, c, args)
            if args.failfast and r.kind in ("fail", "error"):
                aborted = True
                print(c.red(f"\n--failfast: stopping at {r.slug}"))
                break
    else:
        # Threads are fine: each run_submission uses its own temp dir/subprocess.
        # Results print in completion order (each line is self-contained).
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = {pool.submit(evaluate, p): p for p in problems}
            for fut in as_completed(futures):
                r = fut.result()
                results.append(r)
                print_result(r, c, args)

    elapsed = time.perf_counter() - start
    print_summary(results, elapsed, c, args)

    n_fail = sum(1 for r in results if r.kind in ("fail", "error"))
    n_skip = sum(1 for r in results if r.kind == "skip")
    bad = n_fail or aborted or (args.strict and n_skip)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
