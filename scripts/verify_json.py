#!/usr/bin/env python3
"""Verify the canonical solutions in a folder of problem JSON files.

For every ``*.json`` file in the given folder this script:

  1. checks the file is **valid JSON**,
  2. checks it carries the required **ingredients** (the fields the judge needs
     to run — function name, params, canonical solution, tests, ...),
  3. runs the file's ``canonical_solution`` against its ``tests`` using the
     *exact* execution + grading path the Admin "Verify" button uses
     (:func:`app.executor.run_submission`), and
  4. reports whether **all tests passed**, or the **pass ratio**.

Nothing about the sandbox/executor/judge is re-implemented here — it only wires
already-implemented app functionality to a batch of loose JSON files (the same
shape the AI generator emits, e.g. ``test_output/4sum.json``).

Usage:
    python scripts/verify_json.py test_output
    python scripts/verify_json.py path/to/folder --verbose

Exit status is 0 only when every file is valid *and* its canonical solution
passes all of its tests (handy for CI / pre-import gating).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.executor import run_submission  # noqa: E402

# Mirrors app/routers/admin.py so we accept exactly what the Admin UI accepts.
COMPARE_MODES = ("exact", "unordered", "set_of_lists")


def validate(data: object) -> list[str]:
    """Return a list of human-readable reasons the payload can't be judged.

    An empty list means the file has every ingredient
    :func:`run_submission` needs. This checks *structure*, not correctness.
    """
    if not isinstance(data, dict):
        return ["top-level JSON is not an object"]

    errors: list[str] = []

    fn = data.get("function_name")
    if not isinstance(fn, str) or not fn.strip():
        errors.append("missing/empty 'function_name'")

    params = data.get("params")
    if not isinstance(params, list):
        errors.append("'params' must be a list of {name, type} objects")
    else:
        for i, p in enumerate(params):
            if not isinstance(p, dict) or not str(p.get("name", "")).strip():
                errors.append(f"params[{i}] missing 'name'")

    rt = data.get("return_type")
    if rt is not None and not isinstance(rt, str):
        errors.append("'return_type' must be a string")

    compare = data.get("compare", "exact")
    if compare not in COMPARE_MODES:
        errors.append(f"'compare' must be one of {COMPARE_MODES} (got {compare!r})")

    sol = data.get("canonical_solution")
    if not isinstance(sol, str) or not sol.strip():
        errors.append("missing/empty 'canonical_solution'")

    tests = data.get("tests")
    if not isinstance(tests, list) or not tests:
        errors.append("'tests' must be a non-empty list")
    else:
        for i, t in enumerate(tests):
            if not isinstance(t, dict):
                errors.append(f"tests[{i}] is not an object")
                continue
            if not isinstance(t.get("input"), dict):
                errors.append(f"tests[{i}] missing object 'input'")
            if "expected" not in t:
                errors.append(f"tests[{i}] missing 'expected'")

    return errors


def grade(data: dict):
    """Run the canonical solution against the tests via the app's own judge.

    Builds the same lightweight ``problem``/``tests`` stand-ins the Admin
    verify endpoint builds (app/routers/admin.py) and hands them to
    :func:`app.executor.run_submission`.
    """
    prob = SimpleNamespace(
        function_name=data["function_name"].strip(),
        params=data.get("params", []),
        return_type=(data.get("return_type") or "").strip(),
        time_limit_ms=settings.EXEC_TIME_LIMIT_MS,
        memory_limit_mb=settings.EXEC_MEMORY_LIMIT_MB,
        points=100,
        compare=data.get("compare", "exact"),
    )
    tests = [
        SimpleNamespace(
            name=t.get("name", f"test-{i + 1}"),
            input=t.get("input", {}),
            expected=t.get("expected"),
            weight=t.get("weight", 1),
            hidden=t.get("hidden", False),
        )
        for i, t in enumerate(data["tests"])
    ]
    return run_submission(data["canonical_solution"], prob, tests)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("folder", type=pathlib.Path,
                    help="folder containing problem .json files (e.g. test_output)")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="for failing files, list each failing test (status/expected/actual)")
    args = ap.parse_args(argv)

    if not args.folder.is_dir():
        print(f"error: {args.folder} is not a directory", file=sys.stderr)
        return 2

    files = sorted(args.folder.glob("*.json"))
    if not files:
        print(f"No .json files found in {args.folder}")
        return 0

    n_pass = n_fail = n_invalid = 0
    for path in files:
        # 1) valid JSON?
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            n_invalid += 1
            print(f"[INVALID] {path.name}: not valid JSON — {exc}")
            continue

        # 2) all the right ingredients?
        errors = validate(data)
        if errors:
            n_invalid += 1
            print(f"[INVALID] {path.name}: " + "; ".join(errors))
            continue

        # 3) run canonical solution against tests (same path as the Admin UI).
        try:
            g = grade(data)
        except Exception as exc:  # noqa: BLE001 - report any judge/runtime failure per-file
            n_invalid += 1
            print(f"[ERROR]   {path.name}: could not run — {exc}")
            continue

        ratio = f"{g.passed_count}/{g.total_count}"
        pct = round(100 * g.passed_count / g.total_count) if g.total_count else 0
        if g.solved:
            n_pass += 1
            print(f"[PASS]    {path.name}: all tests passed ({ratio})")
        else:
            n_fail += 1
            print(f"[FAIL]    {path.name}: {ratio} passed ({pct}%)")
            if args.verbose:
                # g.results is in the same order as data["tests"], so the i-th
                # result's expected value is data["tests"][i]["expected"].
                for i, r in enumerate(g.results):
                    if r.passed:
                        continue
                    line = f"            - {r.name} [{r.status}]"
                    if r.error:
                        line += f": {r.error}"
                    print(line)
                    if r.status == "wrong":
                        expected = data["tests"][i].get("expected")
                        print(f"                expected={json.dumps(expected)}")
                        print(f"                actual  ={json.dumps(r.returned)}")

    total = len(files)
    print("\n" + "-" * 64)
    print(f"{total} file(s): {n_pass} all-pass, {n_fail} failing, {n_invalid} invalid")
    return 0 if (n_fail == 0 and n_invalid == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
