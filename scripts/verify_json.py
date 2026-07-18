#!/usr/bin/env python3
"""Verify the canonical solutions in a folder of problem JSON files.

For every ``*.json`` file in the given folder this script:

  1. checks the file is **valid JSON**,
  2. checks it carries the required **ingredients** the judge needs to run —
     kind-aware: a ``kind="function"`` file needs function_name/params/…; a
     ``kind="class"`` (design) file needs class_name/class_methods/params and
     ``{operations, args}`` test inputs instead,
  3. runs the file's ``canonical_solution`` against its ``tests`` using the
     *exact* execution + grading path the Admin "Verify" button uses
     (:func:`app.executor.run_submission`) — for a class problem the harness
     instantiates the class and replays each test's operation sequence, and
  4. reports whether **all tests passed**, or the **pass ratio**.

Nothing about the sandbox/executor/judge is re-implemented here — it only wires
already-implemented app functionality to a batch of loose JSON files (the same
shape the AI generator emits, e.g. ``test_output/4sum.json`` or a design
problem's ``generated_full_problem.json``).

The PATH argument may be, in order of specificity:

  * a single problem **.json file** — verify exactly that file
    (``python scripts/verify_json.py staging/two-sum/generated_full_problem.json``);
  * a single **slug directory** that contains a ``generated_full_problem.json`` —
    verify just that one file, ignoring any sibling ``meta.json``
    (``python scripts/verify_json.py staging/two-sum``); or
  * a **folder** of problems — either loose ``*.json`` files (the classic
    ``test_output`` layout) or a batch of ``<slug>/generated_full_problem.json``.

Usage:
    python scripts/verify_json.py test_output
    python scripts/verify_json.py path/to/folder --verbose
    python scripts/verify_json.py staging/two-sum                 # one slug dir
    python scripts/verify_json.py staging/two-sum/generated_full_problem.json  # one file

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

    An empty list means the file has every ingredient :func:`run_submission`
    needs. This checks *structure*, not correctness — the behavioral run in
    :func:`grade` is what confirms the ``expected`` values are actually right.

    Kind-aware: ``kind="function"`` (the default) needs a top-level
    ``function_name``; ``kind="class"`` (a design problem) needs ``class_name`` +
    a non-empty ``class_methods`` and per-test ``{operations, args}`` inputs, and
    must NOT be rejected for lacking ``function_name``.
    """
    if not isinstance(data, dict):
        return ["top-level JSON is not an object"]

    errors: list[str] = []

    kind = data.get("kind", "function") or "function"
    if kind not in ("function", "class"):
        errors.append(f"'kind' must be 'function' or 'class' (got {kind!r})")
        kind = "function"  # continue with the common + function checks

    # --- fields common to both kinds -----------------------------------------
    params = data.get("params")
    if not isinstance(params, list):
        errors.append("'params' must be a list of {name, type} objects")
    else:
        for i, p in enumerate(params):
            if not isinstance(p, dict) or not str(p.get("name", "")).strip():
                errors.append(f"params[{i}] missing 'name'")

    compare = data.get("compare", "exact")
    if compare not in COMPARE_MODES:
        errors.append(f"'compare' must be one of {COMPARE_MODES} (got {compare!r})")

    sol = data.get("canonical_solution")
    if not isinstance(sol, str) or not sol.strip():
        errors.append("missing/empty 'canonical_solution'")

    # --- kind-specific contract ----------------------------------------------
    if kind == "class":
        cn = data.get("class_name")
        if not isinstance(cn, str) or not cn.strip():
            errors.append("missing/empty 'class_name' (kind='class')")
        methods = data.get("class_methods")
        if not isinstance(methods, list) or not methods:
            errors.append("'class_methods' must be a non-empty list (kind='class')")
        else:
            for i, m in enumerate(methods):
                if not isinstance(m, dict) or not str(m.get("name", "")).strip():
                    errors.append(f"class_methods[{i}] missing 'name'")
    else:
        fn = data.get("function_name")
        if not isinstance(fn, str) or not fn.strip():
            errors.append("missing/empty 'function_name'")
        rt = data.get("return_type")
        if rt is not None and not isinstance(rt, str):
            errors.append("'return_type' must be a string")

    # --- tests (input shape depends on kind) ---------------------------------
    tests = data.get("tests")
    if not isinstance(tests, list) or not tests:
        errors.append("'tests' must be a non-empty list")
    else:
        for i, t in enumerate(tests):
            if not isinstance(t, dict):
                errors.append(f"tests[{i}] is not an object")
                continue
            inp = t.get("input")
            if not isinstance(inp, dict):
                errors.append(f"tests[{i}] missing object 'input'")
            elif kind == "class":
                # A class test replays a call sequence: input is {operations, args}.
                if set(inp) != {"operations", "args"}:
                    errors.append(
                        f"tests[{i}].input must have exactly keys "
                        "{operations, args} (kind='class')")
                elif not (isinstance(inp["operations"], list)
                          and isinstance(inp["args"], list)):
                    errors.append(f"tests[{i}].input operations/args must be arrays")
            if "expected" not in t:
                errors.append(f"tests[{i}] missing 'expected'")

    return errors


def grade(data: dict):
    """Run the canonical solution against the tests via the app's own judge.

    Builds the same lightweight ``problem``/``tests`` stand-ins the Admin
    verify endpoint builds (app/routers/admin.py) and hands them to
    :func:`app.executor.run_submission`.

    Kind-aware: for a class problem it forwards ``kind``/``class_name``/
    ``class_methods`` so the harness instantiates the class and replays each
    test's operation sequence. ``function_name`` is still supplied (the executor
    reads it unconditionally) — for a class it is ignored by the harness, so we
    fall back to the class name to keep it a valid identifier.
    """
    kind = data.get("kind", "function") or "function"
    prob = SimpleNamespace(
        kind=kind,
        function_name=(data.get("function_name") or data.get("class_name") or "").strip(),
        params=data.get("params", []),
        return_type=(data.get("return_type") or "").strip(),
        class_name=((data.get("class_name") or "").strip() or None),
        class_methods=(data.get("class_methods") or None),
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
    ap.add_argument("path", type=pathlib.Path,
                    help="a single problem .json FILE, a single <slug>/ dir "
                         "containing generated_full_problem.json, or a FOLDER of "
                         "problems (loose *.json, or a batch of "
                         "<slug>/generated_full_problem.json).")
    ap.add_argument("--glob", metavar="PATTERN", default=None,
                    help="explicit glob for the files to verify, relative to a "
                         "folder PATH (e.g. '*/generated_full_problem.json'). "
                         "Overrides the auto-detection below; ignored when PATH is "
                         "a single file.")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="for failing files, list each failing test (status/expected/actual)")
    args = ap.parse_args(argv)

    path = args.path
    if not path.exists():
        print(f"error: {path} does not exist", file=sys.stderr)
        return 2

    # Discovery + a `base` dir that labels are made relative to.
    #   * a single .json FILE                       -> verify just it;
    #   * a single <slug>/ dir with a
    #     generated_full_problem.json (and no --glob) -> verify just that one file,
    #     ignoring the sibling meta.json;
    #   * a FOLDER                                  -> an explicit --glob wins,
    #     else the direct *.json children (classic layout), else a fallback to the
    #     batch layout <folder>/<slug>/generated_full_problem.json the Mode-A
    #     generator writes (skipping direct-child *.json here avoids each slug
    #     dir's stray source meta.json).
    single_slug_file = path / "generated_full_problem.json"
    if path.is_file():
        files = [path]
        base = path.parent
    elif path.is_dir() and not args.glob and single_slug_file.is_file():
        files = [single_slug_file]
        base = path.parent  # label as "<slug>/generated_full_problem.json"
    elif path.is_dir():
        base = path
        if args.glob:
            files = sorted(path.glob(args.glob))
        else:
            files = sorted(path.glob("*.json"))
            if not files:
                files = sorted(path.glob("*/generated_full_problem.json"))
    else:
        print(f"error: {path} is not a file or directory", file=sys.stderr)
        return 2
    if not files:
        print(f"No problem .json files found in {path}")
        return 0

    n_pass = n_fail = n_invalid = 0
    for fpath in files:
        # Label by path relative to `base` so batch files (all named
        # generated_full_problem.json) are distinguishable by their slug dir.
        try:
            label = str(fpath.relative_to(base))
        except ValueError:
            label = fpath.name

        # 1) valid JSON?
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            n_invalid += 1
            print(f"[INVALID] {label}: not valid JSON — {exc}")
            continue

        # 2) all the right ingredients?
        errors = validate(data)
        if errors:
            n_invalid += 1
            print(f"[INVALID] {label}: " + "; ".join(errors))
            continue

        # 3) run canonical solution against tests (same path as the Admin UI).
        try:
            g = grade(data)
        except Exception as exc:  # noqa: BLE001 - report any judge/runtime failure per-file
            n_invalid += 1
            print(f"[ERROR]   {label}: could not run — {exc}")
            continue

        ratio = f"{g.passed_count}/{g.total_count}"
        pct = round(100 * g.passed_count / g.total_count) if g.total_count else 0
        if g.solved:
            n_pass += 1
            print(f"[PASS]    {label}: all tests passed ({ratio})")
        else:
            n_fail += 1
            print(f"[FAIL]    {label}: {ratio} passed ({pct}%)")
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
