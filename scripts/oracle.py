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

Coverage-first, adversaries add-only
------------------------------------
The suite's backbone is *behavioral coverage*, not "beat an invented wrong
solution": an input earns a hidden case by exercising a structural/execution
regime the current suite misses (see ``cover`` and docs/test-strengthening.md).
A concrete wrong solution — invented or handed to you — only ever ADDS cases via
``fuzz``; it never gates the coverage suite. This is the fix to the old flaw
where a genuinely-discriminating input was discarded merely because no adversary
or canonical-mutant happened to fail on it.

Subcommands
-----------
  cover    Coverage-first hardening (the default backbone). Generates inputs and
           selects the few that most widen behavioral coverage of the canonical —
           no adversary required. Shares one engine with strengthen_tests.py.

  fuzz     When a concrete failing/suspect solution IS in hand, target it: fuzz a
           broad in-domain pool, keep every input on which it diverges from (or
           crashes where) the canonical, shrink each to a minimal reproducer, and
           add them. The reliable way to catch a known-bad solution — no guessing.

  suite    Run a candidate solution against the problem's *stored* suite. A wrong
           candidate that still solves it proves the suite is too weak.

  analyze  Per-input oracle table: in-domain? (validator), the canonical's output
           (== the correct `expected`), runtime, and — with ``--solution`` —
           whether a candidate diverges there. Enrichment/inspection; to actually
           harden, prefer ``cover`` (coverage) or ``fuzz`` (a concrete solution).

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
import contextlib
import io
import json
import pathlib
import sys
from types import SimpleNamespace

_SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS_DIR.parent))
sys.path.insert(0, str(_SCRIPTS_DIR))  # so sibling scripts (strengthen_tests) import

from app import content              # noqa: E402
from app.config import settings      # noqa: E402
from app.executor import run_submission, _equal, problem_view  # noqa: E402
from app.executor.harness import _CODECS  # noqa: E402

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


def _as_prob(p: dict):
    """The problem's grading view — the shared executor contract (handles function
    and class/design kinds, so nothing here drifts from what run_submission reads)."""
    return problem_view(p)


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
# fuzz — when a concrete failing/suspect solution IS in hand, target it directly.
#
# This is the principled replacement for hand-inventing adversaries and hoping a
# curated probe catches them. We generate a broad pool of in-domain inputs and
# keep every one on which the provided solution diverges from (or crashes where)
# the canonical, then shrink each to a minimal reproducer. Adversaries here only
# ever ADD cases — never gate the coverage-driven suite (`cover`).
# --------------------------------------------------------------------------- #
def _find_slug_root(slug: str) -> pathlib.Path | None:
    """Find the content root directory containing a slug (default or extended)."""
    for root in settings.content_dirs:
        if (root / slug / "meta.json").exists():
            return root
    return None


def _append_cases(slug: str, cases: list[dict]) -> int:
    root = _find_slug_root(slug) or settings.CONTENT_DIR
    path = root / slug / "tests" / "cases.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    existing = {c["name"] for c in data.get("cases", [])}
    n = 0
    for c in cases:
        name = c["name"]
        while name in existing:
            n += 1
            name = f"{c['name']}-{n}"
        existing.add(name)
        data.setdefault("cases", []).append(
            {"name": name, "input": c["input"], "expected": c["expected"],
             "weight": 1, "hidden": True})
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return len(cases)


def _has_rich_type(prob: dict) -> bool:
    types = [p.get("type", "") for p in prob.get("params", [])] + [prob.get("return_type", "")]
    return any(tok in (t or "") for t in types for tok in _CODECS)


def cmd_fuzz(args) -> int:
    from app.testgen.generators import (generate_candidates,
                                         generate_class_candidates, GenConfig)
    from app.testgen.constraints import parse_constraints
    from app.testgen.shrink import shrink

    prob = _find_problem(args.slug)
    if prob is None:
        return _die(f"no problem '{args.slug}' in any content root")
    canonical = (prob.get("canonical_solution") or "").strip()
    if not canonical:
        return _die(f"'{args.slug}' has no canonical solution to use as oracle")
    cand_code = pathlib.Path(args.solution).read_text(encoding="utf-8")
    prob_ns = _as_prob(prob)
    compare = prob.get("compare", "exact")
    params = prob.get("params", [])
    validator = None if args.no_validator else _load_validator(args.slug, params)

    bounds = parse_constraints(prob.get("statement_md", ""))
    seeds = [t["input"] for t in prob["tests"]]
    cfg = GenConfig(n_fuzz=args.fuzz, seed=args.seed, include_stress=False)
    if prob_ns.kind == "class":
        cands = generate_class_candidates(
            prob_ns.class_name, params, prob_ns.class_methods or [],
            seeds, bounds, cfg, validator=validator)
    else:
        cands = generate_candidates(params, seeds, bounds, cfg, validator=validator)
    inputs = [c.input for c in cands]

    canon_res = _run(canonical, prob_ns, inputs)
    cand_res = _run(cand_code, prob_ns, inputs)

    catchers: list[tuple[int, dict]] = []   # (size, input)
    for inp, cr, dr in zip(inputs, canon_res, cand_res):
        if cr.status not in _RAN:
            continue                         # canonical can't run it -> unusable
        if validator is not None and not validator(inp):
            continue
        diverge = dr.status not in _RAN or not _equal(dr.returned, cr.returned, compare)
        if diverge:
            catchers.append((len(json.dumps(inp, default=str)), inp))

    print(f"# fuzz: {args.slug}  ({len(inputs)} in-domain inputs, "
          f"{len(catchers)} catch the candidate)")
    if not catchers:
        print("# candidate diverges on none — it agrees with the canonical here "
              "(either correct, or the pool missed its bug; raise --fuzz).")
        return 0

    catchers.sort(key=lambda t: t[0])
    can_shrink = not _has_rich_type(prob)
    shrunk_inputs: list[dict] = []
    seen: set[str] = set()
    for _sz, inp in catchers:
        best = _shrink_catcher(inp, canonical, cand_code, prob, compare,
                               validator) if (args.shrink and can_shrink) else inp
        key = json.dumps(best, default=str)
        if key in seen:
            continue
        seen.add(key)
        shrunk_inputs.append(best)
        if len(shrunk_inputs) >= args.limit:
            break

    # Authoritative expected + confirm each still diverges, via the real judge.
    fresh_canon = _run(canonical, prob_ns, shrunk_inputs)
    fresh_cand = _run(cand_code, prob_ns, shrunk_inputs)
    keep: list[dict] = []
    for inp, cr, dr in zip(shrunk_inputs, fresh_canon, fresh_cand):
        if cr.status not in _RAN:
            continue
        diverge = dr.status not in _RAN or not _equal(dr.returned, cr.returned, compare)
        if not diverge:
            continue
        keep.append({"name": "hidden-fuzz", "input": inp, "expected": cr.returned})

    for k in keep:
        cand_r = _run(cand_code, prob_ns, [k["input"]])[0]
        how = "crashes" if cand_r.status not in _RAN else f"returns {_trunc(cand_r.returned)}"
        print(f"#   {json.dumps(k['input'])}  -> expected {_trunc(k['expected'])}  "
              f"(candidate {how})")

    if args.apply and keep:
        added = _append_cases(args.slug, keep)
        print(f"\n# applied {added} case(s) to content/problems/{args.slug}/tests/cases.json"
              f" — now run check_constraint_validators.py --slug {args.slug} && seed.py && audit.py")
    elif keep:
        print("\n# paste-ready (add --apply to write, --shrink to minimize):")
        print(json.dumps([{**k, "weight": 1, "hidden": True} for k in keep], indent=2))
    return 0


def _shrink_catcher(inp, canonical, cand_code, prob, compare, validator):
    """Delta-debug a catcher to a minimal in-domain input the candidate still fails.

    Uses fast in-process evaluation of the (trusted) canonical and the provided
    candidate for the search; the caller re-verifies the result through the real
    judge. Only used for non-rich-type problems."""
    import signal as _signal
    fname = (prob.get("function_name") or "").strip()

    def _compile(code):
        g: dict = {}
        exec(compile(code, "<s>", "exec"), g)  # noqa: S102 - authoring tool, operator-provided
        return g[fname]
    try:
        cf, df = _compile(canonical), _compile(cand_code)
    except Exception:  # noqa: BLE001
        return inp

    def _run1(fn, d):
        def _a(*_):
            raise TimeoutError
        old = _signal.signal(_signal.SIGALRM, _a)
        _signal.setitimer(_signal.ITIMER_REAL, 0.5)
        try:
            with contextlib.redirect_stdout(io.StringIO()):  # mute solution debug prints
                return ("ok", fn(**d))
        except Exception:  # noqa: BLE001
            return ("err", None)
        finally:
            _signal.setitimer(_signal.ITIMER_REAL, 0)
            _signal.signal(_signal.SIGALRM, old)

    def keep(d) -> bool:
        if validator is not None and not validator(d):
            return False
        ck, cv = _run1(cf, d)
        if ck != "ok":
            return False                      # canonical must run cleanly
        dk, dv = _run1(df, d)
        return dk != "ok" or not _equal(dv, cv, compare)

    if not keep(inp):
        return inp
    from app.testgen.shrink import shrink
    return shrink(inp, keep)


def cmd_cover(args) -> int:
    """Coverage-first hardening for one problem via the shared app.testgen engine
    (the same engine strengthen_tests.py drives in batch) — selects inputs that
    widen behavioral coverage, no adversary required."""
    from strengthen_tests import strengthen, apply_cases  # sibling; shares the engine
    from app.testgen import GenConfig

    by_slug = {p["slug"]: p for p in content.load_all_roots()}
    if args.slug not in by_slug:
        return _die(f"no problem '{args.slug}' in any content root")
    cfg = GenConfig(n_fuzz=args.fuzz, seed=args.seed, include_stress=not args.no_stress)
    rep = strengthen(by_slug[args.slug], cfg, cap=args.cap, mut_cap=args.mut_cap,
                     use_population=args.population)
    if rep.status != "ok":
        print(f"# cover: {args.slug} — {rep.status}: {rep.error or ''}")
        return 0
    print(f"# cover: {args.slug}  coverage {rep.killed_before}->{rep.killed_after}"
          f"/{rep.killable} tokens; +{len(rep.selected)} case(s)")
    for s in rep.selected:
        print(f"#   {json.dumps(s['input'])}  -> expected {_trunc(s['expected'])}")
    if args.apply and rep.selected:
        applied = apply_cases(args.slug, rep.selected)
        print(f"\n# applied {applied} case(s) — now run "
              f"check_constraint_validators.py --slug {args.slug} && seed.py && audit.py")
    elif rep.selected:
        print("\n# paste-ready (add --apply to write):")
        print(json.dumps([{"name": s["name"], "input": s["input"],
                           "expected": s["expected"], "weight": 1, "hidden": True}
                          for s in rep.selected], indent=2))
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

    f = sub.add_parser("fuzz", help="differential-fuzz a concrete solution; add every "
                                    "in-domain input it fails on (adversary add-only)")
    f.add_argument("slug")
    f.add_argument("--solution", required=True, help="path to the suspect/failing .py")
    f.add_argument("--fuzz", type=int, default=200, help="candidate inputs to generate")
    f.add_argument("--limit", type=int, default=3, help="max minimal catchers to report")
    f.add_argument("--shrink", action="store_true",
                   help="delta-debug each catcher to a minimal reproducer")
    f.add_argument("--apply", action="store_true", help="append catchers to cases.json")
    f.add_argument("--no-validator", action="store_true", help="skip the in-domain gate")
    f.add_argument("--seed", type=int, default=1234)
    f.set_defaults(func=cmd_fuzz)

    c = sub.add_parser("cover", help="coverage-first hardening (shared engine; no "
                                     "adversary needed) — select inputs that widen coverage")
    c.add_argument("slug")
    c.add_argument("--cap", type=int, default=12, help="max new cases")
    c.add_argument("--mut-cap", type=int, default=60)
    c.add_argument("--fuzz", type=int, default=80)
    c.add_argument("--no-stress", action="store_true")
    c.add_argument("--seed", type=int, default=1234)
    c.add_argument("--population", action=argparse.BooleanOptionalAction, default=False,
                   help="also fold in cached LLM candidate kills as a token universe")
    c.add_argument("--apply", action="store_true", help="write selected cases back")
    c.set_defaults(func=cmd_cover)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
