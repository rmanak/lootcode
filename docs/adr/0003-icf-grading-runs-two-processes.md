# 0003 — ICF grades in two processes, and hidden cases get their own run

- **Status:** Accepted
- **Date:** 2026-09-12

## Context

The core executor keeps the oracle out of the sandbox: only inputs go in, the
harness returns a value, and the comparison happens in the trusted parent
(`app/executor/__init__.py`). That is what makes two of the promises in
`docs/security.md` structural rather than best-effort — "hidden tests never
sent to the browser", and a score the submitted code cannot write for itself.

The Industry Coding Framework extension (`icf/`, see `docs/extensions.md`)
cannot inherit that shape. Its oracle *is* code: a level is graded by authored
`@case` functions that drive the solver's class through a scenario and assert
along the way, which is the only way to express "a field is gone at exactly
`ts + ttl`" for forty cases a level. Those functions have to run beside the
solution.

The first implementation ran everything in one process, and a security review
demonstrated two working attacks against it:

1. **Hidden tests were readable.** Every test module for the levels being
   submitted was written into the run directory before the solution was
   imported. Three lines in `__init__` — open the file, print it — put the
   hidden cases into a *visible* case's captured stdout, which the UI shows in
   full. Compiled copies in `__pycache__` leaked the same constants (`python
   -I` implies `-E`, so `PYTHONDONTWRITEBYTECODE` in the environment is
   ignored).
2. **The score was writable.** The process that ran the solution also wrote
   `result.json`. Six lines — read the case ids out of `payload.json`, write
   every one of them as `passed`, `os._exit(0)` — scored 49/49 across all four
   levels, hidden cases included.

## Decision

**Two processes, and two runs.**

*Two processes.* The harness (`icf/sandbox/harness.py`) is a **supervisor**
that imports the trusted test modules, deletes their sources and bytecode from
the run directory, forks a **worker**, and is the only process that writes
`result.json`. The worker imports `solution.py`, runs the cases, and reports
each one over a pipe. A worker that dies, hangs or goes silent leaves the
cases it never reported marked failed by the supervisor — never passed.

*Two runs.* A submission is graded in two separate sandbox launches: the
visible cases (whose messages and captured output come back to the solver),
and the hidden cases (whose output and messages `icf/runner.py` discards,
keeping only the verdicts). Untrusted code in the visible run has nothing
secret to read; untrusted code in the hidden run has nowhere to print what it
found.

The process cap is now expressed as headroom (`sandbox.nproc_limit`): a flat
`RLIMIT_NPROC` of 256 counts every task the *machine's user* already owns, so
on a workstation with a browser open the supervisor's single `fork()` failed
with `EAGAIN` and every case came back "the process was killed". It is now
`current tasks + 64`, which is what the anti-fork-bomb control meant all along.

## Consequences

- ICF submissions cost two sandbox launches instead of one, and one extra
  process each. Both are cheap next to the run itself.
- **What is fixed:** a solution cannot read the tests that grade it, cannot
  write the results file, and cannot be credited for a case that never
  reported.
- **What remains, deliberately:** a worker can still lie about a verdict
  *inside its own process* — by patching `icf_testkit.expect`, say — because
  the case function and the solution share an interpreter. That buys a solver
  a false score on their own practice attempt; it cannot leak a hidden test
  and it cannot touch anyone else. Closing it needs the judge to run outside
  the process entirely, with every method call proxied across the boundary,
  which costs the in-process fidelity the tests rely on (object identity,
  aliasing, "the list you passed in must not be the list I stored"). If ICF
  ever becomes competitive or multi-user, that is the trade to revisit — and
  `icf/docs/security.md` says so plainly rather than implying a guarantee that
  is not there.
- `verify_icf.py` is unaffected: it runs authored canonicals, not submissions.

## Amendment (same day, after the fixes were re-reviewed)

Two corrections to the Consequences above, from the second review:

- **Scope of the residual.** It is not only "a worker can patch the assertion
  kit". The worker shares an address space with the oracle it is being graded
  by, so it can also read expected values out of the imported test modules'
  code objects. Same conclusion, wider statement — and it is why the hidden
  run now discards timings as well as output and messages: a per-case
  `sleep` is a channel, narrow but real.
- **What the run split buys.** Not "nothing hidden can be printed back", but
  "nothing hidden can get *out*": in the hidden run all that escapes is the
  per-case verdict, which is revealed by design.
