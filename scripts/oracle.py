#!/usr/bin/env python3
"""oracle.py — differential test-case analysis for a single problem.

Built for the `test-strengthener` agent (and humans hardening a suite by hand).
It closes the "my solution passes here but fails on LeetCode" gap: a stored
hidden suite that is too weak to separate a *correct* solution from a
*plausibly-wrong* one.

Two hard rules, enforced by construction:
  * The **canonical solution is the only oracle.** Every `expected` value is
    computed by executing the canonical — never hand-written, never guessed by a
    model. A wrong `expected` would unfairly fail correct submissions, so we never
    author one.
  * A new case is only fair if the input is **in-domain**, so every candidate
    input is gated through the problem's own
    `content/problems/<slug>/input_validator/input_validator.py`.

Everything runs through the real judge (``app.executor.run_submission``), so
`compare` semantics (exact / unordered / set_of_lists) and the rich-type codecs
(TreeNode / ListNode / DoublyLinkedList) match the running app exactly.

Subcommands
-----------
  suite    Run a candidate solution against the problem's *stored* suite. A wrong
           candidate that still solves it proves the suite is too weak — this is
           the bug to close.

  analyze  For each candidate input, report: in-domain? (validator), the
           canonical's output (== the correct `expected`), its runtime, and —
           with ``--solution`` — whether the candidate DIVERGES from the canonical
           there. Diverging in-domain inputs are printed back as ready-to-paste
           hidden cases: they catch the candidate's bug while staying fair to
           correct code.

Examples
--------
  # Does a suspected-wrong solution slip through the current suite?
  python scripts/oracle.py suite two-sum --solution /tmp/adversary.py

  # Which of my proposed inputs catch it (and what is each one's expected)?
  python scripts/oracle.py analyze two-sum --solution /tmp/adversary.py \
      --inputs /tmp/candidate_inputs.json

  # Just get the correct expected + legality for one input (no candidate):
  python scripts/oracle.py analyze two-sum --input '{"nums":[0,4,3,0],"target":0}'
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from types import SimpleNamespace

_SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS_DIR.parent))
sys.path.insert(0, str(_SCRIPTS_DIR))  # so sibling scripts (strengthen_tests) import

from app import content              # noqa: E402
from app.config import settings      # noqa: E402
from app.executor import run_submission, _equal  # noqa: E402

# A grade status of "passed"/"wrong" both mean the code *ran cleanly* and produced
# a value (`.returned`); only "timeout"/"error" mean it never returned one. We
# grade the oracle against a dummy expected, so the grade is always "wrong" — what
# we care about is whether it ran, and what it returned.
_RAN = {"passed", "wrong"}


# --------------------------------------------------------------------------- #
# Problem loading (mirrors scripts/verify_bank.py so the judge sees the same
# lightweight problem stand-in the app builds).
# --------------------------------------------------------------------------- #
def _find_problem(slug: str) -> dict | None:
    """Load a problem by slug from any configured content root (default + extended)."""
    for root in settings.content_dirs:
        d = root / slug
        if (d / "meta.json").exists():
            return content.load_problem_dir(d)
    return None


def _as_prob(p: dict) -> SimpleNamespace:
    return SimpleNamespace(
        function_name=(p.get("function_name") or "").strip(),
        params=p.get("params", []),
        return_type=(p.get("return_type") or "").strip(),
        time_limit_ms=p["time_limit_ms"],
        memory_limit_mb=p["memory_limit_mb"],
        points=p.get("points", 100),
        compare=p.get("compare", "exact"),
    )


def _mk_tests(inputs, expected=None):
    exp = expected if expected is not None else [None] * len(inputs)
    return [
        SimpleNamespace(name=f"t{i}", input=inp, expected=exp[i], weight=1, hidden=True)
        for i, inp in enumerate(inputs)
    ]


def _run(code: str, prob_ns, inputs: list[dict]):
    """Grade ``code`` on ``inputs`` (expected is irrelevant; we read `.returned`)."""
    if not (code or "").strip() or not inputs:
        return []
    return run_submission(code, prob_ns, _mk_tests(inputs)).results


def _load_validator(slug: str, params: list[dict]):
    """The problem's stated-constraint predicate, or None. Reuses the exact loader
    strengthen_tests uses (same dual-encoding for TreeNode params)."""
    try:
        from strengthen_tests import _load_input_validator
        return _load_input_validator(slug, params)
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Input parsing
# --------------------------------------------------------------------------- #
def _as_input(x):
    """Accept a bare input dict, or a case-shaped dict with an 'input' key."""
    if isinstance(x, dict) and isinstance(x.get("input"), dict):
        return x["input"]
    return x


def _gather_inputs(args, prob: dict) -> list[dict]:
    if getattr(args, "input", None):
        return [_as_input(json.loads(args.input))]
    if getattr(args, "inputs", None):
        raw = sys.stdin.read() if args.inputs == "-" else \
            pathlib.Path(args.inputs).read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, dict) and "cases" in data:
            data = data["cases"]
        if isinstance(data, dict):
            data = [data]
        return [_as_input(x) for x in data]
    # Default: the problem's own stored inputs (handy with --solution to see which
    # existing cases already catch a candidate).
    return [t["input"] for t in prob["tests"]]


def _trunc(v, n=48) -> str:
    s = json.dumps(v, default=str)
    return s if len(s) <= n else s[: n - 1] + "…"


def _die(msg: str) -> int:
    print(f"error: {msg}", file=sys.stderr)
    return 2


# --------------------------------------------------------------------------- #
# suite
# --------------------------------------------------------------------------- #
def cmd_suite(args) -> int:
    prob = _find_problem(args.slug)
    if prob is None:
        return _die(f"no problem '{args.slug}' in any content root")
    code = pathlib.Path(args.solution).read_text(encoding="utf-8")
    prob_ns = _as_prob(prob)
    tests = [
        SimpleNamespace(name=t["name"], input=t["input"], expected=t["expected"],
                        weight=t.get("weight", 1), hidden=t.get("hidden", False))
        for t in prob["tests"]
    ]
    graded = run_submission(code, prob_ns, tests)

    print(f"# suite: {args.slug}  ({len(tests)} cases, compare={prob.get('compare','exact')})")
    print(f"{'':2} {'case':30} {'vis':4} {'status':8} {'ms':>7}")
    for t, r in zip(tests, graded.results):
        mark = "ok" if r.passed else "XX"
        vis = "hid" if t.hidden else "vis"
        ms = f"{r.time_ms:.1f}" if r.time_ms is not None else "-"
        print(f"{mark:2} {t.name[:30]:30} {vis:4} {r.status:8} {ms:>7}")

    print(f"\n  passed {graded.passed_count}/{graded.total_count}"
          f"  score {graded.score}/{prob.get('points', 100)}"
          f"  solved={graded.solved}")
    if graded.solved:
        print("\n  !! This candidate PASSES the current suite. If it is a WRONG "
              "solution,\n     the suite is too weak — use `analyze --solution` to "
              "find a discriminating input.")
    return 0


# --------------------------------------------------------------------------- #
# analyze
# --------------------------------------------------------------------------- #
def cmd_analyze(args) -> int:
    prob = _find_problem(args.slug)
    if prob is None:
        return _die(f"no problem '{args.slug}' in any content root")
    canonical = (prob.get("canonical_solution") or "").strip()
    if not canonical:
        return _die(f"'{args.slug}' has no canonical solution to use as oracle")

    prob_ns = _as_prob(prob)
    compare = prob.get("compare", "exact")
    inputs = _gather_inputs(args, prob)
    validator = None if args.no_validator else _load_validator(args.slug, prob.get("params", []))

    canon_res = _run(canonical, prob_ns, inputs)
    cand_code = pathlib.Path(args.solution).read_text(encoding="utf-8") if args.solution else None
    cand_res = _run(cand_code, prob_ns, inputs) if cand_code else None

    have_cand = cand_res is not None
    print(f"# analyze: {args.slug}  ({len(inputs)} inputs, compare={compare}, "
          f"validator={'on' if validator else 'none'})")
    header = f"{'':2} {'legal':6} {'canon':8} {'ms':>7} {'expected':50}"
    if have_cand:
        header += f" {'cand':8} {'diverge':8}"
    print(header)

    keep = []
    for i, inp in enumerate(inputs):
        cr = canon_res[i]
        canon_ok = cr.status in _RAN
        legal = None if validator is None else bool(validator(inp))
        legal_s = "-" if legal is None else ("yes" if legal else "OUT")
        ms = f"{cr.time_ms:.1f}" if cr.time_ms is not None else "-"
        canon_s = "ok" if canon_ok else cr.status
        exp_s = _trunc(cr.returned) if canon_ok else f"<{cr.status}>"

        diverge = None
        if have_cand:
            dr = cand_res[i]
            if not canon_ok:
                diverge = None  # canonical itself can't run it -> not a usable case
            elif dr.status not in _RAN:
                diverge = True   # candidate errors/TLEs where canonical is fine
            else:
                diverge = not _equal(dr.returned, cr.returned, compare)

        # Row marker: * = keepable new case.
        if have_cand:
            keepable = canon_ok and legal is not False and diverge is True
        else:
            keepable = canon_ok and legal is not False
        mark = "*" if keepable else ""

        row = f"{mark:2} {legal_s:6} {canon_s:8} {ms:>7} {exp_s:50}"
        if have_cand:
            dr = cand_res[i]
            cand_s = "ok" if dr.status in _RAN else dr.status
            dv = "-" if diverge is None else ("DIVERGE" if diverge else "agree")
            row += f" {cand_s:8} {dv:8}"
        print(row)

        if keepable:
            keep.append({
                "name": f"disc-{len(keep) + 1}",
                "input": inp,
                "expected": cr.returned,
                "weight": 1,
                "hidden": True,
            })

    legend = "legal=OUT -> out of stated domain (never add); canon=<status> -> canonical can't run it"
    if have_cand:
        legend += "; DIVERGE -> input separates candidate from canonical (worth adding)"
    print(f"\n  {legend}")

    if keep:
        label = ("in-domain inputs that catch the candidate"
                 if have_cand else "in-domain inputs (rename before adding)")
        print(f"\n# {len(keep)} case(s) worth adding ({label}) — paste into "
              f"content/problems/{args.slug}/tests/cases.json, then run\n"
              f"#   python scripts/check_constraint_validators.py --slug {args.slug} && "
              f"python scripts/seed.py && python scripts/audit.py")
        print(json.dumps(keep, indent=2))
    else:
        msg = "no diverging in-domain inputs" if have_cand else "no in-domain inputs"
        print(f"\n# {msg} — nothing to add.")
    return 0


# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("suite", help="run a candidate against the stored suite")
    s.add_argument("slug")
    s.add_argument("--solution", required=True, help="path to the candidate .py")
    s.set_defaults(func=cmd_suite)

    a = sub.add_parser("analyze", help="per-input oracle + divergence analysis")
    a.add_argument("slug")
    src = a.add_mutually_exclusive_group()
    src.add_argument("--input", help="a single input as a JSON object")
    src.add_argument("--inputs", help="path to a JSON list of inputs (or '-' for stdin); "
                                       "default: the problem's stored inputs")
    a.add_argument("--solution", help="path to a candidate .py to test for divergence")
    a.add_argument("--no-validator", action="store_true",
                   help="skip the in-domain fairness gate")
    a.set_defaults(func=cmd_analyze)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
