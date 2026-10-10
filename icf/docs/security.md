# What ICF trusts

The solver's code is the only untrusted input, and it runs in the sandbox the
rest of lootcode uses. What follows is what that does and does not buy, in the
terms `docs/security.md` uses — including one guarantee ICF cannot give.

## The boundary

Grading goes through `app/executor/sandbox.py::run_harness`, the same launcher
the core executor uses: same rlimits (address space, CPU, file size, task
count), same throwaway run directory, same minimal environment with no
secrets, same process group killed on timeout — and **the same backend**. An
operator who set `EXECUTOR_BACKEND=docker` gets containers here too
(no network, dropped capabilities, read-only rootfs, non-root user). With the
default `subprocess` backend, ICF is exactly as (un)contained as `/problems`
is: notably, network access is *not* blocked.

`icf/sandbox/harness.py` follows the rules `app/executor/harness.py` follows:
stdlib only, no imports from `app` or `icf`, and it replaces `sys.path[0]`
(the directory it was launched from) with the run directory so the solver's
code cannot import the package that started it.

## Two processes, two runs

Core keeps the oracle outside the sandbox: expected values never go in. ICF's
oracle is code — authored `@case` functions that drive the solver's class —
so it has to. The compensation is structural (see
[ADR 0003](../../docs/adr/0003-icf-grading-runs-two-processes.md)):

* **The process that writes the results never runs the solution.** The harness
  supervisor imports the trusted test modules, deletes their sources *and*
  their `__pycache__` copies from the run directory, then forks a worker that
  imports `solution.py` and runs the cases, reporting each over a pipe. A
  worker that dies, hangs, or exits early leaves its remaining cases marked
  failed by the supervisor — never passed. Writing `result.json` from a
  submission does nothing; the supervisor writes it last.
* **Hidden cases get their own sandbox run**, and `icf/runner.py` drops that
  run's captured output, messages *and* timings, keeping only the verdicts. A
  submission in the visible run has no hidden test to read — not on disk and
  not in memory. A submission in the hidden run does still share an address
  space with the oracle that is grading it (the test modules are imported in
  that worker, and `__code__.co_consts` is readable), so what the split buys
  is not secrecy inside that process but the absence of a channel wide enough
  to carry anything out: all that escapes a hidden case is its pass/fail. A
  hidden run's load error is replaced with a generic message for the same
  reason — a traceback is a channel.

## What ICF does **not** guarantee

**A score the submission cannot influence.** A case function and the solution
share an interpreter — so a submission can patch `icf_testkit.expect`, or read
the expected values straight out of the imported test module's code objects,
and pass cases it did not solve. That is a solver cheating their own practice
attempt: it cannot leak a hidden test, reach another user's data, or escape
the sandbox. Closing it means running the judge outside the process and
proxying every method call, which costs the in-process fidelity several tests
depend on (object identity, aliasing, "the list you passed in must not be the
list I stored").

The trade is recorded rather than papered over. If ICF is ever used for
anything competitive, or for more than one person's practice, revisit it
first.

## Test modules are trusted content

An ICF test module is Python that runs in the sandbox next to the solution.
It is repo content, exactly as trusted as a canonical solution — and so
**ICF problems are file-authored only**. There is no admin UI for them, no
route that accepts test code, and no generator that writes one. Changing that
would make user-supplied code an *oracle*, which is a different security
question and needs its own review.

## What a solver can see

`icf/views.py` is the one place that decides, and `icf/store.py` never
persists what it would not show: a hidden case is reduced to
`{hidden, label: "Hidden test N", status, passed}` — no case name, no
assertion message, no captured output, in the response or in the database.
Attempts are scoped to the cookie identity that created them: another visitor
asking for the id gets a 404.
