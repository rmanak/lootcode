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

import copy
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app.db import SessionLocal, init_db  # noqa: E402
from app.executor import _equal, run_submission  # noqa: E402
from app.executor.harness import _CODECS  # noqa: E402 - reuse the in-sandbox codec
from app.models import Problem  # noqa: E402
from app.store import seed_collections, seed_from_content  # noqa: E402

AMBIGUITY = ("any order", "in any order", "any valid", "you may return",
             "return any", "multiple valid")


def _permute(out, mode):
    """Produce a differently-ordered but equivalent answer for `mode`."""
    if mode == "unordered" and isinstance(out, list):
        return list(reversed(out))
    if mode == "set_of_lists" and isinstance(out, list):
        return [list(reversed(e)) if isinstance(e, list) else e for e in reversed(out)]
    return out


def _codecs_for(p):
    """Decoder map + return encoder for a problem's declared custom types, reusing
    the in-sandbox harness codec so this in-process path matches the real run."""
    decoders = {}
    for spec in p.params:
        codec = _CODECS.get(spec.get("type") or "")
        if codec:
            decoders[spec["name"]] = codec[1]
    ret = _CODECS.get(p.return_type or "")
    return decoders, (ret[2] if ret else None)


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
        ns: dict = {codec[0].__name__: codec[0] for codec in _CODECS.values()}
        try:
            exec(p.canonical_solution, ns)
            fn = ns[p.function_name]
            decoders, encoder = _codecs_for(p)
            ok = True
            for t in p.tests:
                # Deep-copy: some canonical solutions mutate their input in place
                # (e.g. the sign-flip trick), and t.input aliases the test data the
                # importer later writes to disk — see build_bank.py / import_top150.py.
                args = copy.deepcopy(dict(t.input))
                for name, dec in decoders.items():
                    args[name] = dec(args[name])
                out = fn(**args)
                if encoder is not None:
                    out = encoder(out)
                if not _equal(_permute(out, mode), t.expected, mode):
                    ok = False
                    break
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

        # Collection integrity: every manifest slug must resolve to a real problem,
        # so a typo can't silently drop a problem from a curated list.
        n_coll, unresolved = seed_collections(db)

        print("\n" + ("=" * 95))
        if bad:
            print(f"INCONSISTENT: {len(bad)} problem(s) need attention:")
            for s, i in bad.items():
                print(f"  - {s}: {'; '.join(i)}")
        if unresolved:
            print(f"BROKEN COLLECTIONS: {len(unresolved)} unknown problem slug(s):")
            for ref in unresolved:
                print(f"  - {ref}")
        if bad or unresolved:
            return 1
        print(f"ALL CONSISTENT: {len(problems)} problems across {n_coll} collection(s) — "
              "canonical passes all tests, statements match the judge, 'any order' "
              "problems accept re-ordered answers, and every collection slug resolves.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
