"""Audit every problem for statement / test / canonical / judge consistency.

For each problem it verifies:
  1. canonical solution passes ALL its tests in the real sandbox
     (so the tests and the canonical solution agree), and that every test's
     expected value equals the canonical output under the problem's compare mode;
  2. the statement's ordering language matches the judge's compare mode —
     a statement that promises "any order" must NOT use exact matching;
  3. fairness: for order-insensitive modes, a deliberately RE-ORDERED valid
     answer is still accepted (proving the judge honours the promised flexibility).

Exits non-zero if any inconsistency is found.  Run:  python scripts/audit.py
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app.db import SessionLocal, init_db  # noqa: E402
from app.executor import _equal, run_submission  # noqa: E402
from app.models import Problem  # noqa: E402
from app.store import seed_from_content  # noqa: E402

AMBIGUITY = ("any order", "in any order", "any valid", "you may return",
             "return any", "multiple valid")


def _permute(out, mode):
    """Produce a differently-ordered but equivalent answer for `mode`."""
    if mode == "unordered" and isinstance(out, list):
        return list(reversed(out))
    if mode == "set_of_lists" and isinstance(out, list):
        return [list(reversed(e)) if isinstance(e, list) else e for e in reversed(out)]
    return out


def audit_problem(p: Problem) -> list[str]:
    issues: list[str] = []
    mode = p.compare or "exact"

    # 1) canonical passes its own tests (sandbox) => tests <-> canonical agree
    canon_ok = False
    if p.canonical_solution:
        canon_ok = run_submission(p.canonical_solution, p, p.tests).solved
        if not canon_ok:
            issues.append("canonical solution does NOT pass all its tests")
    else:
        issues.append("no canonical solution")

    # 2) statement ordering language vs compare mode (collapse whitespace so a
    #    line-wrapped "any\norder" is still detected)
    text = " ".join((p.statement_md or "").lower().split())
    amb = any(kw in text for kw in AMBIGUITY)
    if amb and mode == "exact":
        issues.append("statement allows 'any order' but compare=exact (judge is strict)")

    # 3) fairness: re-ordered valid answers must still pass for relaxed modes
    fair = "n/a"
    if mode in ("unordered", "set_of_lists") and p.canonical_solution and canon_ok:
        ns: dict = {}
        try:
            exec(p.canonical_solution, ns)
            fn = ns[p.function_name]
            ok = all(_equal(_permute(fn(**t.input), mode), t.expected, mode) for t in p.tests)
            fair = "honored" if ok else "BROKEN"
            if not ok:
                issues.append("compare mode does not actually accept re-ordered answers")
        except Exception as exc:  # noqa: BLE001
            fair = "error"
            issues.append(f"fairness check error: {exc}")

    p._mode, p._amb, p._fair, p._canon = mode, amb, fair, canon_ok  # for the report
    return issues


def main() -> int:
    init_db()
    with SessionLocal() as db:
        if not db.query(Problem).count():
            seed_from_content(db)
        problems = sorted(db.query(Problem).all(), key=lambda p: p.slug)

        all_issues: dict[str, list[str]] = {}
        print(f"{'slug':38} {'diff':6} {'compare':13} {'canon':6} {'any-order?':11} {'fairness':9}")
        print("-" * 95)
        for p in problems:
            issues = audit_problem(p)
            all_issues[p.slug] = issues
            flag = "  <-- " + "; ".join(issues) if issues else ""
            print(f"{p.slug:38} {p.difficulty:6} {p._mode:13} "
                  f"{'OK' if p._canon else 'FAIL':6} "
                  f"{('yes' if p._amb else 'no'):11} {p._fair:9}{flag}")

        bad = {s: i for s, i in all_issues.items() if i}
        print("\n" + ("=" * 95))
        if bad:
            print(f"INCONSISTENT: {len(bad)} problem(s) need attention:")
            for s, i in bad.items():
                print(f"  - {s}: {'; '.join(i)}")
            return 1
        print(f"ALL CONSISTENT: {len(problems)} problems — canonical passes all tests, "
              "statements match the judge, and 'any order' problems accept re-ordered answers.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
