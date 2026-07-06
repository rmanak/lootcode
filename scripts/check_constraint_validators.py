"""Audit each problem's input-constraint validator against its own legal inputs.

Every problem under ``content/problems/`` carries an input validator at
``content/problems/<slug>/input_validator/input_validator.py`` exposing a
``validate_input(...)`` predicate (see ``docs/input-validators.md``). This loads
each validator and runs it over that problem's own test-case inputs
(``tests/cases.json``). Every real test input is, by definition, a legal input,
so a correct validator must return ``True`` for all of them — this reports, per
problem, whether it does.

By default it audits the vetted, in-tree validators. Pass a directory to instead
audit a *flat staging dir* of ``<slug>_input_test.py`` files (the shape
``scripts/generate_constraint_validators.py`` writes) — useful before promoting
freshly generated validators into the content tree. Problems whose validator is
missing are skipped.

Verification is delegated to the generator's own
``generate_constraint_validators.verify_against_cases`` so the result matches the
generator's self-verify exactly — including the dual-encoding handling for
``TreeNode`` params (a validator may legitimately validate either the raw
level-order list or a decoded node object).

Exit status is non-zero if any checked validator rejects a legal input (or fails
to load), so this is usable as a CI gate.

Usage (from the project root):
    python scripts/check_constraint_validators.py                 # audit in-tree validators
    python scripts/check_constraint_validators.py --slug two-sum  # just one problem
    python scripts/check_constraint_validators.py -v              # list every problem
    python scripts/check_constraint_validators.py -q              # summary only
    python scripts/check_constraint_validators.py staging_dir     # audit a flat staging dir
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS.parent))  # repo root, so `app` imports
sys.path.insert(0, str(_SCRIPTS))         # so the sibling generator imports

from app.config import settings  # noqa: E402
# Reuse the generator's verification verbatim (same dual-encoding TreeNode logic),
# so a validator that passes here passes there and vice versa.
import generate_constraint_validators as gcv  # noqa: E402


def _validator_file(slug: str, flat_dir: pathlib.Path | None,
                    content_dir: pathlib.Path) -> pathlib.Path:
    """Where this problem's validator lives.

    Default (``flat_dir is None``): the vetted in-tree location
    ``content/problems/<slug>/input_validator/input_validator.py``. Otherwise a
    ``<slug>_input_test.py`` in the given flat staging dir.
    """
    if flat_dir is None:
        return content_dir / slug / "input_validator" / "input_validator.py"
    return flat_dir / f"{slug}_input_test.py"


def _iter_problem_dirs(content_dir: pathlib.Path):
    for child in sorted(content_dir.iterdir()):
        if child.is_dir() and (child / "meta.json").exists():
            yield child


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", nargs="?", default=None,
                    help="optional flat staging dir of <slug>_input_test.py files "
                         "(e.g. the generator's --out-dir); default = the vetted "
                         "in-tree content/problems/<slug>/input_validator/ validators")
    ap.add_argument("--slug", action="append", default=[],
                    help="only this slug (repeatable); default = all problems")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print a line for every problem (PASS / n-a too), not just failures")
    ap.add_argument("-q", "--quiet", action="store_true",
                    help="print only the final summary")
    args = ap.parse_args()

    flat_dir = None
    if args.dir is not None:
        flat_dir = pathlib.Path(args.dir)
        if not flat_dir.is_dir():
            print(f"ERROR: not a directory: {flat_dir}")
            return 2

    content_dir = settings.CONTENT_DIR
    wanted = set(args.slug)

    checked = passed = failed = errored = no_cases = skipped = 0
    failures: list[tuple[str, str, str]] = []

    for d in _iter_problem_dirs(content_dir):
        slug = d.name
        if wanted and slug not in wanted:
            continue
        vfile = _validator_file(slug, flat_dir, content_dir)
        if not vfile.exists() or vfile.stat().st_size == 0:
            skipped += 1
            continue

        checked += 1
        code = vfile.read_text(encoding="utf-8")
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        params = (meta.get("function") or {}).get("params") or []
        cases_path = d / "tests" / "cases.json"
        cases = []
        if cases_path.exists():
            cases = json.loads(cases_path.read_text(encoding="utf-8")).get("cases", [])

        try:
            npass, total, detail = gcv.verify_against_cases(code, cases, params)
        except Exception as e:  # noqa: BLE001 - e.g. validator source won't parse/load
            errored += 1
            failures.append((slug, "load-error", f"{type(e).__name__}: {e}"))
            if not args.quiet:
                print(f"  ERR  {slug}: {type(e).__name__}: {e}")
            continue

        if total == 0:
            no_cases += 1
            if args.verbose and not args.quiet:
                print(f"  n/a  {slug}  (no test inputs to check)")
        elif npass == total:
            passed += 1
            if args.verbose and not args.quiet:
                print(f"  PASS {slug}  ({npass}/{total})")
        else:
            failed += 1
            failures.append((slug, f"{npass}/{total}", detail))
            if not args.quiet:
                print(f"  FAIL {slug}  ({npass}/{total})  {detail}")

    where = "content/problems/<slug>/input_validator/" if flat_dir is None else f"{flat_dir}/"
    missing_hint = ("input_validator.py" if flat_dir is None
                    else "{slug}_input_test.py")
    print()
    print(f"Checked {checked} validator(s) from {where}: "
          f"{passed} passed, {failed} rejected a legal input, "
          f"{errored} failed to load, {no_cases} had no test inputs. "
          f"({skipped} problem(s) skipped — no {missing_hint}.)")

    if failures and args.quiet:
        print("Failing/erroring validators:")
        for slug, ratio, detail in failures:
            print(f"  - {slug} ({ratio}): {detail}")

    return 1 if (failed or errored) else 0


if __name__ == "__main__":
    raise SystemExit(main())
