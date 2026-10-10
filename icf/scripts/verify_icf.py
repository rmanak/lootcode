#!/usr/bin/env python
"""Verify every ICF problem on disk. The gate before one is worth serving.

Four checks per problem, cheapest first:

1. **Spec** — ``icf/content.py::validate``: four levels, statements present,
   the starter declares every advertised method, no reserved slug.
2. **Starter fails** — the template must not accidentally pass anything. If a
   stubbed method returns the right answer, the level is not testing what the
   author thinks it is.
3. **Canonical passes** — every case of every level, visible and hidden.
4. **Each level adds work** — where the author supplied ``solution/levelN.py``
   checkpoints, level N+1's tests must *fail* against the level-N checkpoint.
   This is what stops a level being a restatement of the one before it.

Usage:
    python icf/scripts/verify_icf.py               # every problem
    python icf/scripts/verify_icf.py --slug in-memory-database -v
    python icf/scripts/verify_icf.py --skip-checkpoints
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from icf import content, runner  # noqa: E402
from icf.content import LEVELS, Problem  # noqa: E402

GREEN, RED, YELLOW, DIM, OFF = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"


def _fmt_failures(graded, limit: int = 6) -> list[str]:
    lines = []
    for level in graded.levels:
        for case in level.cases:
            if case.passed:
                continue
            head = f"L{case.level} {case.func} [{case.status}]"
            message = (case.message or "").strip().splitlines()
            lines.append(f"{head}: {message[0] if message else ''}")
            if len(lines) >= limit:
                lines.append("…")
                return lines
    return lines


def verify(problem: Problem, *, verbose: bool = False,
           check_checkpoints: bool = True) -> list[str]:
    """Return a list of failures; empty means the problem is servable."""
    failures = list(content.validate(problem))
    if failures:
        return failures

    all_levels = [lv.number for lv in problem.levels]

    # 2. the starter must not pass anything it does not implement.
    starter = runner.grade(problem, problem.starter_code, all_levels)
    if starter.passed_count:
        passed = [c.func for lv in starter.levels for c in lv.cases if c.passed]
        failures.append(
            f"the starter template passes {len(passed)} case(s) it should not: "
            + ", ".join(passed[:5]))

    # 3. the canonical must pass everything.
    canonical = runner.grade(problem, problem.canonical_code, all_levels)
    if canonical.load_error:
        failures.append(f"canonical failed to load: {canonical.load_error}")
    elif not canonical.all_passed:
        failures.append(
            f"canonical passes only {canonical.passed_count}/"
            f"{canonical.total_count} cases")
        failures.extend("  " + line for line in _fmt_failures(canonical))
    elif verbose:
        for lv in canonical.levels:
            print(f"    {DIM}L{lv.level} {lv.title}: {lv.passed_count}/"
                  f"{lv.total_count} cases{OFF}")

    # 4. every level must ask for something the one before it did not.
    if check_checkpoints:
        for number in LEVELS:
            previous = problem.checkpoints.get(number - 1)
            if previous is None:
                continue
            graded = runner.grade(problem, previous, [number])
            if graded.all_passed:
                failures.append(
                    f"level {number}'s tests all pass against the level "
                    f"{number - 1} checkpoint — level {number} adds nothing "
                    "the tests can see")
            elif verbose:
                print(f"    {DIM}L{number} vs L{number - 1} checkpoint: "
                      f"{graded.passed_count}/{graded.total_count} "
                      f"(must not be all){OFF}")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--slug", help="verify only this problem")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--skip-checkpoints", action="store_true",
                        help="skip the 'each level adds work' check (slowest)")
    parser.add_argument("--problems-dir", type=Path, default=None)
    args = parser.parse_args()

    problems = content.load_all(args.problems_dir)
    if args.slug:
        problems = [p for p in problems if p.slug == args.slug]
        if not problems:
            print(f"{RED}no such problem: {args.slug}{OFF}")
            return 2
    if not problems:
        print(f"{YELLOW}no ICF problems found — nothing to verify{OFF}")
        return 0

    bad = 0
    for problem in problems:
        print(f"  {problem.slug} ({problem.case_count} cases)")
        failures = verify(problem, verbose=args.verbose,
                          check_checkpoints=not args.skip_checkpoints)
        if failures:
            bad += 1
            for line in failures:
                print(f"    {RED}✗ {line}{OFF}")
        else:
            print(f"    {GREEN}✓ ok{OFF}")

    total = len(problems)
    print(f"\n{total - bad}/{total} problem(s) verified")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
