"""Grade a torch-runtime submission against the canonical as a live oracle.

The Python runtime compares a submission with *stored* expected values. Here
the canonical solution is the oracle and runs on every submission, which is
what lets a test be "a random 8×16 tensor" rather than a written-down matrix:

1. every stored test's input is made concrete in this process
   (:mod:`.inputs` — stdlib PRNG, seeded from the test's name), and the
   problem's generator adds ``random_tests`` fresh hidden draws from a seed
   picked now, so each submission meets inputs no earlier one saw;
2. the submission and the canonical run in **two separate sandboxes**, in
   parallel, on byte-identical inputs. The submission's process never
   contains the canonical, cannot read it, and cannot touch its outputs —
   the same reason ICF grades in two processes (docs/adr/0003);
3. their outputs are compared here with ``torch.allclose`` semantics
   (:mod:`.compare`), never inside a sandbox.

Nothing about the Python runtime changes: this module is imported only when a
problem says ``"runtime": "torch"``.
"""
from __future__ import annotations

import os
import secrets
import threading
from concurrent.futures import ThreadPoolExecutor

from ...config import settings
from ...logging_config import get_logger
from .. import CaseView, GradedRun, ProblemView, TestResult, sandbox, unrunnable
from .. import subprocess_executor as core_exec
from ..base import Limits, Outcome, TestSpec
from . import unavailable_reason
from .compare import DEFAULT_ATOL, DEFAULT_RTOL, compare
from .inputs import (
    MAX_RUN_ELEMENTS,
    MAX_RUN_TESTS,
    SpecError,
    check_config,
    count_elements,
    generated_inputs,
    materialize_input,
)

HARNESS = os.path.join(os.path.dirname(__file__), "harness.py")
#: The core harness's source, shipped into every run so the torch adapter
#: drives the very file the Python runtime runs.
CORE_HARNESS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "harness.py")


log = get_logger(__name__)

#: Torch sandboxes alive at once, process-wide. Each one may hold 2 GB of
#: address space and, on a hang, a server thread for its whole budget; every
#: Run starts two. Without a cap, the request thread pool decides the total.
_slots = threading.BoundedSemaphore(max(1, settings.EXEC_TORCH_MAX_PARALLEL))


#: A bad input spec is a problem bug, reported per test, never a 500. Besides
#: SpecError, arithmetic on author-supplied numbers can raise (an overflow in a
#: generator option, a non-finite parameter); the generator's random tests get
#: a fresh seed every run, so such a draw can surface live although `make
#: check` was green.
_CONTENT_ERRORS = (SpecError, ArithmeticError, ValueError, TypeError, LookupError)


def limits_for(pv: ProblemView) -> Limits:
    """The problem's limits, with the memory cap raised to what torch needs
    (a problem may ask for more than the runtime's floor, up to its ceiling)."""
    return Limits(
        time_limit_ms=pv.time_limit_ms or settings.EXEC_TIME_LIMIT_MS,
        memory_limit_mb=min(max(pv.memory_limit_mb or 0, settings.EXEC_TORCH_MEMORY_LIMIT_MB),
                            settings.EXEC_TORCH_MEMORY_LIMIT_MAX_MB),
        max_output_kb=settings.EXEC_MAX_OUTPUT_KB,
    )


def _run(code: str, pv: ProblemView, specs: list[TestSpec],
         limits: Limits, forbid: list[str] | None = None) -> dict[str, Outcome]:
    with _slots:
        return _run_unbounded(code, pv, specs, limits, forbid)


def forbidden_names(pv: ProblemView) -> list[str]:
    """The problem's ``torch.forbid`` list: torch callables a *submission* may
    not use (``"torch.nn.functional.layer_norm"``, ``"torch.Tensor.backward"``),
    because they would do the exercise for it. Malformed entries are kept, so
    the harness reports them as a problem bug instead of silently allowing
    the call. Never applied to the canonical, which may use the built-in as
    the reference. An honesty aid for the person practising, not a security
    boundary: ``torch._C`` reaches the same kernels."""
    raw = (pv.runtime_config or {}).get("forbid") or []
    return [str(x) for x in raw] if isinstance(raw, list) else [str(raw)]


def _run_unbounded(code: str, pv: ProblemView, specs: list[TestSpec],
                   limits: Limits, forbid: list[str] | None = None) -> dict[str, Outcome]:
    with open(CORE_HARNESS, encoding="utf-8") as fh:
        core_source = fh.read()
    payload = core_exec.build_payload(
        code, pv.function_name, pv.params, pv.return_type, specs, limits,
        kind=pv.kind, class_name=pv.class_name, class_methods=pv.class_methods)
    if forbid:
        payload["forbid"] = list(forbid)
    data, timed_out = sandbox.run_harness(
        harness_path=HARNESS,
        files={"solution.py": code, "_lc_core_harness.py": core_source},
        payload=payload,
        limits=limits,
        overall_s=core_exec.overall_timeout_s(specs, limits) + settings.TORCH_STARTUP_S,
        prefix="lc_torch_",
        python=settings.TORCH_PYTHON,
        image=settings.TORCH_DOCKER_IMAGE,
    )
    return core_exec.outcomes(data, specs, timed_out)


def _unique(name: str, taken: set[str]) -> str:
    out, i = name, 2
    while out in taken:
        out, i = f"{name}-{i}", i + 1
    taken.add(out)
    return out


def grade(code: str, pv: ProblemView, tests: list[CaseView], *,
          random_seed: int | None = None) -> GradedRun:
    """Grade ``code`` for a torch problem. Same result shape as the Python
    runtime's :func:`app.executor.run_submission`, so every caller — the run
    endpoint, seed, verify_bank, the admin gate — works unchanged."""
    reason = unavailable_reason()
    if reason:
        return unrunnable(tests, f"This problem needs the PyTorch runtime, which is not "
                                 f"available here: {reason}. See docs/torch-runtime.md.")
    canonical = (pv.canonical_solution or "").strip()
    if not canonical:
        return unrunnable(tests, "This PyTorch problem has no reference solution to "
                                 "grade against (a problem bug, not yours).")

    cfg = pv.runtime_config or {}
    try:
        rtol, atol, random_weight = check_config(cfg, DEFAULT_RTOL, DEFAULT_ATOL)
    except SpecError as exc:
        return unrunnable(tests, f"This problem's torch settings are invalid (a problem "
                                 f"bug, not yours): {exc}")

    # --- 1. concrete inputs -------------------------------------------------
    cases: list[CaseView] = []
    specs: list[TestSpec] = []
    bad_input: dict[str, str] = {}
    taken = {t.name for t in tests}
    if len(tests) > MAX_RUN_TESTS:
        return unrunnable(tests, f"Too many tests for one torch run ({len(tests)}; "
                                 f"limit {MAX_RUN_TESTS}).")
    budget = MAX_RUN_ELEMENTS  # numbers built in THIS process, across the run
    for t in tests:
        cases.append(t)
        try:
            inp = materialize_input(t.input, pv.params, seed_base=t.name)
        except _CONTENT_ERRORS as exc:
            bad_input[t.name] = str(exc)
            continue
        budget -= count_elements(inp)
        if budget < 0:
            return unrunnable(tests, "This run's test inputs are too large in total "
                                     f"(limit {MAX_RUN_ELEMENTS} numbers).")
        specs.append(TestSpec(name=t.name, input=inp))
    seed = secrets.randbits(31) if random_seed is None else random_seed
    try:
        fresh = generated_inputs(cfg, pv.params, seed=seed)
        budget -= sum(count_elements(inp) for inp in fresh)
        if budget < 0:
            raise SpecError(f"random tests exceed the run's {MAX_RUN_ELEMENTS}-number budget")
    except _CONTENT_ERRORS as exc:
        fresh = []
        bad_input["random"] = str(exc)
    for i, inp in enumerate(fresh):
        name = _unique(f"random-{i + 1}", taken)
        cases.append(CaseView(name=name, input=inp, expected=None,
                              weight=random_weight, hidden=True))
        specs.append(TestSpec(name=name, input=inp))

    # --- 2. two sandboxes, in parallel --------------------------------------
    limits = limits_for(pv)
    if specs:
        if code.strip() == canonical:
            # Grading the canonical itself (seed, verify_bank): one run is both.
            mine = oracle = _run(code, pv, specs, limits)
        else:
            with ThreadPoolExecutor(max_workers=2) as pool:
                f_mine = pool.submit(_run, code, pv, specs, limits, forbidden_names(pv))
                f_oracle = pool.submit(_run, canonical, pv, specs, limits)
                mine, oracle = f_mine.result(), f_oracle.result()
    else:
        mine = oracle = {}

    # --- 3. compare here ----------------------------------------------------
    results: list[TestResult] = []
    earned = total = passed_count = 0
    runtime = 0.0
    for t in cases:
        total += t.weight
        if t.name in bad_input:
            results.append(TestResult(
                name=t.name, hidden=t.hidden, passed=False, status="error",
                time_ms=None, stdout="",
                error=f"This test's input spec is invalid (a problem bug): {bad_input[t.name]}"))
            continue
        oc = mine.get(t.name) or Outcome(status="error", error="No result.")
        ref = oracle.get(t.name) or Outcome(status="error", error="No result.")
        runtime += oc.time_ms or 0
        if oc.status != "ok":
            passed, status, error = False, oc.status, oc.error
        elif ref.status != "ok":
            # The reference's traceback is its source: log it, never show it.
            log.warning("torch reference solution failed on test %r: %s",
                        t.name, (ref.error or "")[-2000:])
            passed, status = False, "error"
            error = ("The reference solution failed on this input, so it cannot be "
                     "graded (a problem bug, not yours). The details are in the "
                     "server log.")
        else:
            passed, why = compare(oc.returned, ref.returned, rtol=rtol, atol=atol)
            status = "passed" if passed else "wrong"
            error = None if passed else f"Wrong answer — {why}."
        if passed:
            passed_count += 1
            earned += t.weight
        results.append(TestResult(
            name=t.name, hidden=t.hidden, passed=passed, status=status,
            time_ms=oc.time_ms, error=error, stdout=oc.stdout,
            returned=(oc.returned if oc.status == "ok" else None)))

    if "random" in bad_input:
        results.append(TestResult(
            name="random", hidden=True, passed=False, status="error", time_ms=None,
            stdout="", error=f"The random-test generator is invalid: {bad_input['random']}"))
        total += 1

    score = round(pv.points * earned / total) if total else 0
    return GradedRun(
        results=results, passed_count=passed_count, total_count=len(results),
        earned_weight=earned, total_weight=total, score=score,
        solved=(len(results) > 0 and passed_count == len(results)), runtime_ms=runtime)
