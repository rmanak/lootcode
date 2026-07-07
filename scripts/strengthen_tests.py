#!/usr/bin/env python3
"""Strengthen a problem's test suite so it catches buggy *user* solutions.

Pipeline (see docs/test-strengthening.md and test-strengthening-plan.md):

  1. Load the problem (canonical, params, compare, existing tests, statement).
  2. Parse constraint bounds from the statement (best-effort; T2).
  3. Generate candidate inputs — edge shapes ∪ seed perturbations ∪ small fuzz ∪
     one large stress (T1/T3/T4).
  4. Compute each candidate's *expected* by running the trusted canonical through
     the real judge; drop candidates the canonical can't run cleanly.
  5. Build single-edit mutants of the canonical (T5) and grade each against every
     candidate; a candidate that makes a mutant diverge from the canonical kills it.
  6. Select the minimal set of NEW cases that kills mutants the existing suite
     misses (greedy set-cover; always keep the stress case).
  7. Report a before/after mutation score. With --apply, append the selected cases
     as hidden tests to content/problems/<slug>/tests/cases.json.

Nothing here re-implements the sandbox or judge — expected values and mutant
grading both go through app.executor.run_submission, so compare semantics and the
TreeNode codec are honored. This mirrors scripts/verify_bank.py's bank loop.

Usage:
    python scripts/strengthen_tests.py median-from-data-stream          # dry-run report
    python scripts/strengthen_tests.py --filter tree -j 8               # many, parallel
    python scripts/strengthen_tests.py two-sum --apply                  # write cases back
    python scripts/strengthen_tests.py median-from-data-stream --cap 12 --fuzz 120
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from types import SimpleNamespace

_SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS_DIR.parent))
sys.path.insert(0, str(_SCRIPTS_DIR))  # so the sibling generator imports

from app import content  # noqa: E402
from app.config import settings  # noqa: E402
from app.executor import run_submission, _equal  # noqa: E402
# Reuse the harness's own rich-type codecs (the exact same array<->object mapping
# the real judge uses) so TreeNode/ListNode problems can grade on the fast
# in-process path instead of the ~100× slower sandbox path. Side-effect-free.
from app.executor.harness import (  # noqa: E402
    _CODECS, TreeNode, _tree_decode, _tree_encode,
)
from app.testgen import (  # noqa: E402
    GenConfig,
    generate_candidates,
    make_mutants,
    parse_constraints,
)
from app.testgen.mutate import Mutant  # noqa: E402
from app.testgen.select import select_cases  # noqa: E402
from app.testgen.coverage import CanonicalTracer  # noqa: E402
from app.testgen.features import input_features, expression_params  # noqa: E402

# Population of LLM candidate solutions (collected by scripts/collect_candidates.py).
# A wrong candidate is a discriminator exactly like a mutant — the difference the
# median sol.py class of bug needs (a from-scratch distributed bug, not a local
# edit). See plan §11.3.
CANDIDATE_CACHE = (pathlib.Path(__file__).resolve().parent.parent
                   / "testgen_cache" / "candidates")

# Per-problem stated-constraint validators (scripts/generate_constraint_validators.py;
# see docs/input-validators.md). Used as the fairness gate on generated inputs: a
# candidate the problem's own validate_input() rejects is out-of-domain and must never
# become a baked hidden test. This closes the out-of-domain leak that paused the apply
# (27/93 of the owner's own solutions were flagged by illegal inputs — all fairness,
# no real bugs).


def _validator_file(slug: str) -> pathlib.Path:
    return settings.CONTENT_DIR / slug / "input_validator" / "input_validator.py"


def _load_input_validator(slug: str, params: list[dict]):
    """Return a predicate ``inp_dict -> bool`` gating generated inputs to those the
    problem's stated constraints allow, or ``None`` if no validator exists.

    Mirrors ``generate_constraint_validators.verify_against_cases`` exactly — same
    dual-encoding (a ``TreeNode`` param is tried both as its raw level-order list and
    decoded to a node object) and same "exception ⇒ reject" semantics — so "legal
    input" here means precisely what the validator audit calls legal. The validator
    lives at ``content/problems/<slug>/input_validator/input_validator.py``.
    Import/exec failures degrade to ``None`` (gate off for that problem; the
    mechanical guards still run)."""
    vfile = _validator_file(slug)
    if not vfile.exists() or vfile.stat().st_size == 0:
        return None
    try:
        import generate_constraint_validators as gcv  # sibling script; lazy + cached
        fn = gcv._load_validator(vfile.read_text(encoding="utf-8"))
    except Exception:
        return None

    tree_params = gcv._tree_param_names(params)
    transforms = [lambda inp: inp]
    if tree_params:
        def _decode(inp: dict) -> dict:
            out = dict(inp)
            for name in tree_params:
                if name in out:
                    out[name] = gcv._tree_from_level_order(out[name])
            return out
        transforms.append(_decode)

    def check(inp: dict) -> bool:
        for tf in transforms:
            try:
                if bool(fn(**tf(inp))):
                    return True
            except Exception:
                continue
        return False

    return check

# Candidates are model-written, so screen out anything with side effects before we
# exec it in-process (the fork+watchdog only bounds runaway *compute*, not a stray
# file write). An algorithmic solution never needs these; a match just means "skip".
_UNSAFE = re.compile(
    r"\b(?:subprocess|socket|shutil|urllib|requests|ctypes|pty|multiprocessing|"
    r"os\.(?:system|popen|remove|unlink|rmdir|rename|replace|chmod|makedirs)|"
    r"__import__|sys\.exit)\b|\b(?:eval|exec|open)\s*\(")


def _load_candidate_codes(slug: str, canonical: str) -> list[tuple[str, str]]:
    """Return ``[(label, code)]`` for usable candidate solutions of ``slug``.

    Keeps only parseable candidates; drops ones identical to the canonical (they
    agree everywhere → no signal), exact duplicates, and anything the safety screen
    flags. Missing cache (collection not done for this slug) → empty, so the
    selector degrades gracefully to mutation-only."""
    path = CANDIDATE_CACHE / f"{slug}.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    canon = (canonical or "").strip()
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for c in data.get("candidates", []):
        if not c.get("parse_ok"):
            continue
        code = (c.get("code") or "").strip()
        if not code or code == canon or code in seen or _UNSAFE.search(code):
            continue
        seen.add(code)
        out.append((c.get("label", "?"), code))
    return out


def _prob(p: dict) -> SimpleNamespace:
    return SimpleNamespace(
        function_name=(p.get("function_name") or "").strip(),
        params=p.get("params", []),
        return_type=(p.get("return_type") or "").strip(),
        time_limit_ms=p["time_limit_ms"],
        memory_limit_mb=p["memory_limit_mb"],
        points=p.get("points", 100),
        compare=p.get("compare", "exact"),
    )


def _tests(inputs: list[dict], expected: list | None = None,
           offset: int = 0) -> list[SimpleNamespace]:
    out = []
    for i, inp in enumerate(inputs):
        out.append(SimpleNamespace(
            name=f"c{offset + i}", input=inp,
            expected=(expected[i] if expected is not None else None),
            weight=1, hidden=True,
        ))
    return out


#: Max serialized size (bytes) of a candidate's canonical output. A larger
#: `expected` is dropped: it would bloat cases.json AND risk blowing the user's
#: own output cap (EXEC_MAX_OUTPUT_KB) even for a correct solution.
MAX_EXPECTED_BYTES = 8 * 1024


def _grade(code: str, prob, inputs: list[dict], expected: list | None = None,
           chunk: int = 25) -> list:
    """Grade `code` over `inputs`, aligned to `inputs`, in small chunks.

    Chunking isolates a pathological candidate (e.g. one whose output overflows
    the harness result-file cap and would otherwise poison the whole batch). If a
    full chunk comes back all-error — the tell-tale of a killed harness — it is
    re-graded one input at a time so real per-input outcomes are recovered.
    """
    results: list = [None] * len(inputs)
    for start in range(0, len(inputs), chunk):
        sub = inputs[start:start + chunk]
        exp = expected[start:start + chunk] if expected is not None else None
        g = run_submission(code, prob, _tests(sub, exp, offset=start))
        rs = list(g.results)
        if len(sub) > 1 and all(r.status == "error" for r in rs):
            rs = []
            for j, inp in enumerate(sub):
                e = [exp[j]] if exp is not None else None
                gg = run_submission(code, prob, _tests([inp], e, offset=start + j))
                rs.append(gg.results[0])
        for j, r in enumerate(rs):
            results[start + j] = r
    return results


# --------------------------------------------------------------------------- #
# In-process fast grading (mutation SELECTION only).
#
# The sandbox is correct but slow (a subprocess per grade); with tens of mutants
# times hundreds of candidates it is far too slow for the bank. Because this is an
# offline authoring script running the *trusted* canonical and mechanical mutants
# of it (exactly like scripts/seed.py and scripts/build_bank.py already exec
# canonicals), we grade the mutation-selection loop in-process, guarded by a
# SIGALRM wall-clock timeout. The authoritative `expected` for any case we
# actually keep is still computed through the real sandbox (see _grade), and the
# canonical is re-verified against the sandbox before anything is written.
#
# SIGALRM only fires on the main thread, so the in-process path runs sequentially.
# Rich types (TreeNode/ListNode/...) reuse the harness codec in-process; only a
# *nested* rich type (e.g. TreeNode[]) falls back to the sandbox path.
# --------------------------------------------------------------------------- #
class _Timeout(Exception):
    pass


def _run_forked(fn, timeout_s: float):
    """Run ``fn()`` in a forked child with a hard wall-clock kill.

    SIGALRM (used by the in-process grader) cannot interrupt a mutant stuck in a
    single long C-level call (big-int arithmetic, a giant allocation). Forking and
    letting the parent SIGKILL the child's process group is the only robust bound —
    a lightweight echo of what the real sandbox does, without a subprocess exec.
    The child writes its pickled result to a temp file; only the result crosses the
    boundary, so ``fn`` may be an ordinary closure (fork copies its memory)."""
    import os
    import pickle
    import tempfile

    fd, path = tempfile.mkstemp(prefix="lc_grade_")
    os.close(fd)
    pid = os.fork()
    if pid == 0:  # child
        try:
            os.setpgrp()
        except OSError:
            pass
        try:
            payload = ("ok", fn())
        except BaseException as e:  # noqa: BLE001
            payload = ("err", f"{type(e).__name__}: {e}")
        try:
            with open(path, "wb") as f:
                pickle.dump(payload, f)
        finally:
            os._exit(0)

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        done, _ = os.waitpid(pid, os.WNOHANG)
        if done:
            break
        time.sleep(0.02)
    else:
        try:
            os.killpg(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            os.waitpid(pid, 0)
        except ChildProcessError:
            pass
        try:
            os.unlink(path)
        except OSError:
            pass
        raise _Timeout("in-process grading exceeded budget")

    try:
        with open(path, "rb") as f:
            kind, val = pickle.load(f)
    except (EOFError, OSError, pickle.UnpicklingError):
        raise RuntimeError("in-process grader died")
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
    if kind == "err":
        raise RuntimeError(val)
    return val


def _fast_available(prob) -> bool:
    # A top-level rich-type param/return (TreeNode/ListNode/...) is handled
    # in-process by the codec below; only a *nested* one (e.g. TreeNode[]) still
    # needs the sandbox path.
    types = [pp.get("type", "") for pp in prob.params] + [prob.return_type]
    for t in types:
        t = (t or "").strip()
        for tok in _CODECS:
            if tok in t and t != tok:
                return False
    return True


def _rich_codec(prob):
    """(decoders, encoder) mapping wire arrays <-> rich-type objects for a problem.

    ``decoders`` maps each rich-typed param name to its array->object decoder;
    ``encoder`` is the object->array encoder when the return type is a rich type
    (else None). Uses the harness's own _CODECS table, so in-process grading stays
    byte-for-byte faithful to the sandbox judge."""
    decoders = {pp["name"]: _CODECS[t][1] for pp in prob.params
                if (t := (pp.get("type", "") or "").strip()) in _CODECS}
    ret = (prob.return_type or "").strip()
    encoder = _CODECS[ret][2] if ret in _CODECS else None
    return decoders, encoder


def _compile(code: str, fname: str, inject: dict | None = None):
    g: dict = dict(inject or {})   # e.g. {"TreeNode": TreeNode} for tree problems
    exec(compile(code, "<sol>", "exec"), g)  # noqa: S102 - trusted canonical/mutant
    return g[fname]


def _call(func, inp: dict, decoders: dict | None, encoder):
    """Call ``func`` on ``inp``, decoding TreeNode params in and encoding a TreeNode
    return out — a fresh decode per call so a solution that mutates the tree can't
    corrupt a shared input (matches the sandbox's per-test decode)."""
    if decoders:
        args = dict(inp)
        for name, dec in decoders.items():
            args[name] = dec(args[name])
    else:
        args = inp
    val = func(**args)
    return encoder(val) if encoder is not None else val


def _inproc_grade(func, fname: str, inputs: list[dict], expected: list,
                  compare: str, timeout_s: float = 0.25,
                  budget_s: float = 0.6, decoders: dict | None = None,
                  encoder=None) -> list[str]:
    """Return per-input status: 'passed' | 'wrong' | 'error' | 'timeout'.

    Inputs are small, so the canonical runs in well under a millisecond; a mutant
    that exceeds ``timeout_s`` on one is looping/pathological and counts as killed.
    A per-mutant ``budget_s`` bounds a mutant that loops on *many* inputs: once it
    is exceeded we stop and mark the remainder 'timeout' (it's clearly killed —
    and such a mutant is dropped as stillborn if it "kills" every input anyway)."""
    out: list[str] = []

    def _alarm(*_):
        raise _Timeout()

    old = signal.signal(signal.SIGALRM, _alarm)
    start = time.time()
    try:
        for i, (inp, exp) in enumerate(zip(inputs, expected)):
            if time.time() - start > budget_s:
                out.extend(["timeout"] * (len(inputs) - i))  # bound pathological mutants
                break
            signal.setitimer(signal.ITIMER_REAL, timeout_s)
            try:
                val = _call(func, inp, decoders, encoder)
                out.append("passed" if _equal(val, exp, compare) else "wrong")
            except _Timeout:
                out.append("timeout")
            except Exception:  # noqa: BLE001
                out.append("error")
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
    finally:
        signal.signal(signal.SIGALRM, old)
    return out


def _inproc_expected(func, inputs: list[dict], timeout_s: float = 0.5,
                     budget_s: float = 8.0, decoders: dict | None = None,
                     encoder=None):
    """Run the canonical in-process; return list of (ok, value) per input.

    A generated input outside the problem's domain can make even the *canonical*
    loop (e.g. a bit-twiddling ``while a`` on a negative ``a``); the tight per-input
    cap drops such inputs cheaply, and the total ``budget_s`` bounds a pile-up of
    them. Dropped inputs are simply not used — they were bad candidates. TreeNode
    params/returns are decoded/encoded so the stored expected matches the sandbox."""
    out = []

    def _alarm(*_):
        raise _Timeout()

    old = signal.signal(signal.SIGALRM, _alarm)
    start = time.time()
    try:
        for i, inp in enumerate(inputs):
            if time.time() - start > budget_s:
                out.extend([(False, None)] * (len(inputs) - i))
                break
            signal.setitimer(signal.ITIMER_REAL, timeout_s)
            try:
                out.append((True, _call(func, inp, decoders, encoder)))
            except _Timeout:
                out.append((False, None))
            except Exception:  # noqa: BLE001
                out.append((False, None))
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
    finally:
        signal.signal(signal.SIGALRM, old)
    return out


@dataclass
class Report:
    slug: str
    difficulty: str
    status: str = "ok"                 # ok | skip | error
    validator: bool = False            # stated-constraint fairness gate active for this problem
    n_candidates: int = 0
    n_valid: int = 0
    n_mutants: int = 0                  # live single-edit mutants (local-bug proxy)
    killable: int = 0
    killed_before: int = 0
    killed_after: int = 0
    n_pop: int = 0                      # live population candidates (from-scratch bugs)
    pop_killable: int = 0              # pop candidates caught by *some* input
    pop_caught_before: int = 0         # pop candidates already caught by seed tests
    pop_caught_after: int = 0          # pop candidates caught after selection
    selected: list[dict] = field(default_factory=list)   # new hidden cases
    survivors: list[str] = field(default_factory=list)   # discriminator descs still alive
    error: str | None = None
    elapsed_s: float = 0.0


def strengthen(p: dict, cfg: GenConfig, cap: int, mut_cap: int,
               grade_workers: int = 1, use_mutants: bool = True,
               use_population: bool = True, use_validator: bool = True) -> Report:
    slug = p["slug"]
    rep = Report(slug=slug, difficulty=p.get("difficulty", "?"))
    t0 = time.time()
    canonical = (p.get("canonical_solution") or "").strip()
    if not canonical:
        rep.status = "skip"
        return rep
    prob = _prob(p)
    if not prob.params:
        rep.status = "skip"
        rep.error = "no params"
        return rep

    try:
        bounds = parse_constraints(p.get("statement_md", ""))
        seeds = [t["input"] for t in p.get("tests", [])]
        expr_hint = expression_params(prob.params, seeds)
        validator = _load_input_validator(slug, prob.params) if use_validator else None
        rep.validator = validator is not None
        cands = generate_candidates(prob.params, seeds, bounds, cfg, validator=validator)
        rep.n_candidates = len(cands)
        compare = prob.compare
        fast = _fast_available(prob)
        decoders, encoder = _rich_codec(prob)
        inject = {cls.__name__: cls for cls, _dec, _enc in _CODECS.values()}

        # Mutation selection runs on everything EXCEPT the T4 stress case (which is
        # force-kept regardless — its value is timing, realized at user-run time).
        sel_cands = [c for c in cands if c.origin != "stress"]
        stress_cands = [c for c in cands if c.origin == "stress"]

        # 4. Expected via the canonical (in-process fast path when possible);
        #    drop candidates it can't run cleanly or whose output is oversized.
        def canonical_expected(inputs):
            if fast:
                def _fn():
                    cf = _compile(canonical, prob.function_name, inject)
                    return _inproc_expected(cf, inputs, decoders=decoders,
                                            encoder=encoder)
                try:
                    return _run_forked(_fn, timeout_s=15.0)
                except _Timeout:
                    return [(False, None)] * len(inputs)
            rs = _grade(canonical, prob, inputs)
            return [((r is not None and r.status in ("passed", "wrong")),
                     (r.returned if r is not None else None)) for r in rs]

        exp = canonical_expected([c.input for c in sel_cands])
        valid: list = []              # (Candidate, expected)
        for c, (ok, v) in zip(sel_cands, exp):
            if not ok:
                continue
            if len(json.dumps(v, default=str)) > MAX_EXPECTED_BYTES:
                continue
            valid.append((c, v))
        rep.n_valid = len(valid)
        if not valid:
            rep.status = "error"
            rep.error = "canonical produced no runnable candidate"
            rep.elapsed_s = time.time() - t0
            return rep

        vinputs = [c.input for c, _ in valid]
        vexpected = [e for _, e in valid]

        # 5. COVERAGE TOKENS per valid input — the backbone of selection. Each input
        #    is valued by how much *new behavior* it covers (solution-independent),
        #    NOT by whether some invented wrong solution fails on it. Two universes:
        #      * structural input features (app/testgen/features.py)
        #      * canonical execution regimes: line + joint value-signature + output
        #        class (app/testgen/coverage.py)
        #    Mutant/population kills are folded in below as one MORE universe of
        #    ('kill', i) tokens — add-only, never a gate. This is the fix to the old
        #    flaw where a genuinely-discriminating input was discarded merely because
        #    it killed no canonical-mutant (see docs/test-strengthening.md).
        def _cov_tokens(inputs: list[dict]) -> list[set]:
            feats = [input_features(inp, prob.params, expr_hint) for inp in inputs]
            if not fast or not inputs:
                return feats  # nested rich type: skip exec trace, features only
            def _fn():
                tr = CanonicalTracer(canonical, prob.function_name, inject,
                                     decoders, encoder)
                return [tr.tokens(inp) for inp in inputs]
            try:
                exec_toks = _run_forked(_fn, timeout_s=max(20.0, 0.06 * len(inputs) + 10))
            except Exception:  # noqa: BLE001 - tracing is best-effort, must never break a run
                exec_toks = [set() for _ in inputs]
            return [f | e for f, e in zip(feats, exec_toks)]

        cov = _cov_tokens(vinputs)   # aligned to `valid`

        # Discriminator populations (OPTIONAL, add-only): single-edit mutants of the
        # canonical (local-bug proxy) + cached LLM candidate solutions (from-scratch-
        # bug proxy). Each discriminator an input 'kills' adds one ('kill', idx) token
        # to that input — one extra coverage universe. Selection works fine with none.
        mutants = make_mutants(canonical, cap=mut_cap, seed=cfg.seed) if use_mutants else []
        pop = ([Mutant(desc=f"pop:{label}", code=code)
                for label, code in _load_candidate_codes(slug, canonical)]
               if use_population else [])
        pop_start = len(mutants)
        discriminators = mutants + pop

        def grade(code):
            if fast:
                try:
                    mf = _compile(code, prob.function_name, inject)
                except Exception:  # noqa: BLE001 - non-compiling: killed by all inputs
                    return set(range(len(vinputs)))
                st = _inproc_grade(mf, prob.function_name, vinputs, vexpected,
                                   compare, decoders=decoders, encoder=encoder)
                return {ci for ci, s in enumerate(st) if s != "passed"}
            rs = _grade(code, prob, vinputs, vexpected)
            return {ci for ci, r in enumerate(rs) if r is None or r.status != "passed"}

        results: list[tuple[int, set]] = []
        if discriminators:
            if fast:
                fork_budget = max(30.0, 0.7 * len(discriminators) + 10.0)
                def _grade_all():
                    return [(mi, grade(d.code)) for mi, d in enumerate(discriminators)]
                try:
                    results = _run_forked(_grade_all, timeout_s=fork_budget)
                except _Timeout:
                    results = []  # grading failure just means no 'kill' tokens; coverage stands
            else:
                results = [(mi, grade(d.code)) for mi, d in enumerate(discriminators)]

        # Drop stillborn discriminators (killed by *every* input -> no signal); the
        # rest fold into per-input coverage as ('kill', mi) tokens.
        n_valid = len(vinputs)
        live = {mi for mi, kb in results if len(kb) < n_valid}
        live_mut = {mi for mi in live if mi < pop_start}
        live_pop = {mi for mi in live if mi >= pop_start}
        rep.n_mutants = len(live_mut)
        rep.n_pop = len(live_pop)

        killed_any: set[int] = set()
        for mi, killed_by in results:
            if mi not in live:
                continue
            if killed_by:
                killed_any.add(mi)
            for ci in killed_by:
                cov[ci].add(("kill", mi))

        # Baseline = every token the EXISTING (seed) suite already covers.
        baseline: set = set()
        for i, (c, _) in enumerate(valid):
            if c.origin == "seed":
                baseline |= cov[i]

        # 6. Greedily select new cases that widen coverage beyond the baseline.
        pool = [i for i, (c, _) in enumerate(valid) if c.origin != "seed"]
        pool_tokens = [cov[i] for i in pool]
        pool_sizes = [len(json.dumps(valid[i][0].input, default=str)) for i in pool]
        all_coverable: set = set(baseline)
        for t in cov:
            all_coverable |= t
        sel = select_cases(pool_tokens, [], len(all_coverable), cap,
                           baseline=baseline, sizes=pool_sizes)

        rep.killable = len(all_coverable)
        rep.killed_before = len(baseline & all_coverable)
        rep.killed_after = sel.killed_by_chosen
        rep.survivors = [discriminators[mi].desc for mi in sorted(live)
                         if mi not in killed_any]

        # Population accounting: from-scratch wrong solutions now caught (a 'kill'
        # token for a live population discriminator appearing in the covered set).
        covered: set = set(baseline)
        for local_i, _gain in sel.per_pick:
            covered |= cov[pool[local_i]]
        def _pop_caught(tokens: set) -> int:
            return sum(1 for mi in live_pop if ("kill", mi) in tokens)
        rep.pop_killable = len(live_pop & killed_any)
        rep.pop_caught_before = _pop_caught(baseline)
        rep.pop_caught_after = _pop_caught(covered)

        # Assemble selected cases: greedy picks + the force-kept stress case.
        picks: list[dict] = []
        for local_i, gain in sel.per_pick:
            cand, e = valid[pool[local_i]]
            picks.append({"input": cand.input, "expected": e,
                          "origin": cand.origin, "kills": gain})
        for sc in stress_cands:
            picks.append({"input": sc.input, "expected": None,
                          "origin": "stress", "kills": 0})

        # 7/8. Recompute expected for kept cases through the REAL sandbox (the
        #      authoritative judge — honors compare/TreeNode) and verify the
        #      canonical passes each. Drop any that error / are oversized there.
        #      Grade via _grade (not run_submission directly): the force-kept T4
        #      stress case can produce an oversized output that truncates the shared
        #      harness result file and errors the *whole* batch — _grade's chunking
        #      + per-input re-grade isolates that case so the real picks survive.
        if picks:
            rs = _grade(canonical, prob, [pk["input"] for pk in picks])
            existing_names = {t["name"] for t in p.get("tests", [])}
            n = 1
            for pk, r in zip(picks, rs):
                if r is None or r.status not in ("passed", "wrong"):
                    continue
                if len(json.dumps(r.returned, default=str)) > MAX_EXPECTED_BYTES:
                    continue
                name = f"gen-{n}"
                while name in existing_names:
                    n += 1
                    name = f"gen-{n}"
                existing_names.add(name)
                n += 1
                rep.selected.append({
                    "name": name, "input": pk["input"], "expected": r.returned,
                    "weight": 1, "hidden": True,
                    "_origin": pk["origin"], "_kills": pk["kills"],
                })
    except Exception as exc:  # noqa: BLE001
        rep.status = "error"
        rep.error = f"{type(exc).__name__}: {exc}"
    rep.elapsed_s = time.time() - t0
    return rep


def apply_cases(slug: str, selected: list[dict]) -> int:
    """Append selected cases (as hidden) to tests/cases.json, preserving the rest."""
    path = settings.CONTENT_DIR / slug / "tests" / "cases.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = data.get("cases", [])
    for s in selected:
        cases.append({"name": s["name"], "input": s["input"],
                      "expected": s["expected"], "weight": s["weight"],
                      "hidden": True})
    data["cases"] = cases
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return len(selected)


# --------------------------------------------------------------------------- #
def _print(rep: Report, verbose: bool) -> None:
    if rep.status == "skip":
        print(f"[SKIP]  {rep.slug}: {rep.error or 'no canonical'}")
        return
    if rep.status == "error":
        print(f"[ERROR] {rep.slug}: {rep.error}")
        return
    delta = rep.killed_after - rep.killed_before
    score = f"{rep.killed_before} -> {rep.killed_after} (+{delta})"
    pop = ""
    if rep.n_pop:
        pop = (f"; pop-bugs caught {rep.pop_caught_before}->{rep.pop_caught_after}"
               f"/{rep.pop_killable} (of {rep.n_pop})")
    print(f"[OK]    {rep.slug} ({rep.difficulty}): "
          f"coverage {score}/{rep.killable} tokens; "
          f"mut={rep.n_mutants} pop={rep.n_pop}{pop}; "
          f"+{len(rep.selected)} cases; {rep.elapsed_s:.1f}s")
    if verbose:
        for s in rep.selected:
            inp = json.dumps(s["input"])
            if len(inp) > 100:
                inp = inp[:97] + "..."
            print(f"          + {s['name']} [{s['_origin']}, +{s['_kills']} cov] "
                  f"exp={json.dumps(s['expected'])[:60]}  in={inp}")
        if rep.survivors:
            print(f"          surviving discriminators ({len(rep.survivors)}): "
                  f"{', '.join(rep.survivors[:8])}"
                  f"{' ...' if len(rep.survivors) > 8 else ''}")


def _work(args_tuple):
    """Picklable worker for ProcessPoolExecutor."""
    p, cfg, cap, mut_cap, use_mutants, use_population, use_validator = args_tuple
    return strengthen(p, cfg, cap, mut_cap, use_mutants=use_mutants,
                      use_population=use_population, use_validator=use_validator)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*", help="only these slugs (default: all)")
    ap.add_argument("--filter", help="only slugs containing this substring")
    ap.add_argument("--exclude", action="append", default=[], metavar="SLUG",
                    help="skip this slug entirely (repeatable) — e.g. problems whose "
                         "under-specified statement makes the validator gate leak")
    ap.add_argument("--apply", action="store_true",
                    help="write selected cases back to cases.json (default: dry-run)")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("-j", "--jobs", type=int, default=1,
                    help="problems in parallel")
    ap.add_argument("--grade-jobs", type=int, default=4,
                    help="mutant gradings in parallel per problem")
    ap.add_argument("--cap", type=int, default=12, help="max new cases per problem")
    ap.add_argument("--mut-cap", type=int, default=60, help="max mutants per problem")
    ap.add_argument("--fuzz", type=int, default=80, help="random fuzz inputs")
    ap.add_argument("--no-stress", action="store_true", help="skip the T4 stress case")
    ap.add_argument("--mutants", action=argparse.BooleanOptionalAction, default=True,
                    help="use single-edit mutants as discriminators (default: on)")
    ap.add_argument("--population", action=argparse.BooleanOptionalAction, default=True,
                    help="use the LLM candidate population as discriminators "
                         "(default: on; no-op where no candidates are cached)")
    ap.add_argument("--validator", action=argparse.BooleanOptionalAction, default=True,
                    help="gate generated inputs through the problem's stated-constraint "
                         "validator (content/problems/<slug>/input_validator/input_validator.py), "
                         "dropping out-of-domain inputs (default: on; no-op where no validator exists)")
    ap.add_argument("--seed", type=int, default=1234)
    args = ap.parse_args()
    if not args.mutants and not args.population:
        ap.error("nothing to select against: pass at least one of --mutants/--population")

    all_probs = content.load_all()
    by_slug = {p["slug"]: p for p in all_probs}
    if args.slugs:
        probs = [by_slug[s] for s in args.slugs if s in by_slug]
        missing = [s for s in args.slugs if s not in by_slug]
        for s in missing:
            print(f"[ERROR] unknown slug: {s}")
    elif args.filter:
        probs = [p for p in all_probs if args.filter in p["slug"]]
    else:
        probs = all_probs

    if args.exclude:
        skip = set(args.exclude)
        before = len(probs)
        probs = [p for p in probs if p["slug"] not in skip]
        print(f"Excluding {before - len(probs)} slug(s): {', '.join(sorted(skip))}")

    cfg = GenConfig(n_fuzz=args.fuzz, max_candidates=max(140, args.fuzz + 60),
                    seed=args.seed, include_stress=not args.no_stress)

    reports: list[Report] = []
    t0 = time.time()
    # Problem-level parallelism uses *processes*, not threads: the in-process fast
    # grader arms SIGALRM, which only fires on a process's main thread.
    if args.jobs > 1:
        from concurrent.futures import ProcessPoolExecutor
        jobs = [(p, cfg, args.cap, args.mut_cap, args.mutants, args.population, args.validator)
                for p in probs]
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            for rep in ex.map(_work, jobs):
                reports.append(rep)
                _print(rep, args.verbose)
    else:
        for p in probs:
            rep = strengthen(p, cfg, args.cap, args.mut_cap,
                             use_mutants=args.mutants, use_population=args.population,
                             use_validator=args.validator)
            reports.append(rep)
            _print(rep, args.verbose)

    if args.apply:
        applied = 0
        for rep in reports:
            if rep.status == "ok" and rep.selected:
                applied += apply_cases(rep.slug, rep.selected)
        print(f"\nApplied {applied} new cases across "
              f"{sum(1 for r in reports if r.selected)} problems.")

    ok = [r for r in reports if r.status == "ok"]
    added = sum(len(r.selected) for r in ok)
    gained = sum(r.killed_after - r.killed_before for r in ok)
    pop_gained = sum(r.pop_caught_after - r.pop_caught_before for r in ok)
    pop_probs = sum(1 for r in ok if r.pop_caught_after > r.pop_caught_before)
    print(f"\n{len(ok)} problems processed, {added} cases selected, "
          f"+{gained} coverage tokens total "
          f"(+{pop_gained} population-bug catches across {pop_probs} problems), "
          f"{time.time() - t0:.1f}s{' (dry-run)' if not args.apply else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
