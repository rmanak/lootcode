# 0002 — The sandbox file-size rlimit bounds `result.json`, not disk usage

- **Status:** Accepted
- **Date:** 2026-07-29

## Context

`docs/code-execution.md` lists resource caps as sandbox guarantee #5 and ends
"If a change can weaken any of the above, stop and write an ADR." This is that
ADR: fixing a user-visible bug required raising `RLIMIT_FSIZE`, and the reason
it was safe to do so is not obvious from the code.

**The bug.** A solution that called `print()` in a loop failed *every* test with
"The run was stopped (overall time limit or the process was killed — possible
memory limit or crash)". Two limits disagreed about scope:

- the harness capped captured stdout at `max_output_bytes` **per test**;
- the parent set `RLIMIT_FSIZE` to `max_output_kb * 1024 + 4096` (69,632 bytes)
  for the **whole** `result.json`, which holds *every* test's stdout.

With 13 tests the harness hit `OSError: [Errno 27] File too large` while writing
`result.json`. No results file existed, so `_collect` filled in every test with
its generic fallback — including tests that had already passed. The user saw a
crash message for a correct solution whose only sin was a debug `print`.

**What the cap was assumed to do.** Read quickly, a 68 KB file cap looks like the
control that stops a hostile submission filling the disk. It is not, and sizing
`result.json` against it conflated two unrelated jobs.

## Decision

Two changes, and one thing deliberately left alone.

1. **The output budget is run-wide, not per test.** `_OutputBudget` in
   `app/executor/harness.py` is a single budget shared across the run, so the
   captured total cannot scale with test count. Truncation is announced in the
   output, never silent.

2. **`RLIMIT_FSIZE` is sized for what it actually bounds** — one `result.json` —
   at `max_output_kb * 1024 + 1 MB` (1,114,112 bytes, from 69,632). The 1 MB is
   headroom for the per-test `returned`, `error`, `name` and timing fields.
   Because that headroom is a heuristic rather than a bound, `_write_results`
   degrades in steps on `OSError` — drop stdout, clip tracebacks, drop
   `returned` — reacting to the real failure instead of predicting byte sizes.
   Every degradation lands on a *failure* for the affected test, never a pass:
   the parent awards a pass only for status `ok` whose `returned` equals the
   (sandbox-invisible) expected value.

3. **We did not add an aggregate disk quota.** There isn't one today; see below.

We rejected the alternative of keeping the rlimit at 68 KB and having the
harness measure `result.json` before writing. It needs serialize → measure →
re-serialize in the trusted path, and when the estimate is wrong the failure
mode is exactly the bug above.

## Consequences

**What the raise actually costs.** `RLIMIT_FSIZE` bounds *any single file*, not
the total a process may write, so it never constrained a loop writing many
files. The nominal change is 16×; the measured change in sustained write
throughput is **~1.6×** (1216 MB/s in 68 KB files → 1972 MB/s in 1.06 MB files).

**The subprocess backend remains stricter than docker.** The docker backend sets
no file-size limit at all: `/sandbox` is an uncapped `rw` host bind mount and
only `/tmp` gets `--tmpfs size=16m`. A limit absent from the *hardened* backend
was never load-bearing in the default one.

**The real anti-disk-fill controls are the wall clock and cleanup**, not this
rlimit: `overall_s`, the PID cap, and the `shutil.rmtree` in the `finally`. That
line is thinner than it looks. `overall_s = import_budget + per_test × n_tests +
5`, which for a 20-test problem at the default 10 s limit is **210 seconds**. At
the throughput above that is ~250 GB, against 291 GB free on `/` — and the
sandbox workdir comes from `tempfile.mkdtemp()`, so it lands on `/tmp` on the
root filesystem, not on the larger `/home`. Filling that disk takes the OS down
with it.

**This hazard is pre-existing and unchanged in kind by this ADR** — 1.6× on a
budget that already reaches ~85% of the disk is not what decides the outcome.
It is recorded here because the file cap reads like protection against it and
isn't, and because the next person to touch these limits should know the wall
clock is what's holding the line.

**One non-zero delta.** The 68 KB cap incidentally prevented the child (same uid
as the server) from writing past the first 68 KB of any file, including
`lootcode.db`. That is now 1 MB. Since corrupting the first 68 KB already
destroys the SQLite header and page 1, the protection was illusory in practice —
but it is a real widening against the project's most valuable asset, and the
honest reason it's acceptable is #3 below, not the rlimit.

**Follow-ups, none of them blocking this change:**

- An aggregate write quota for the sandbox — a per-run tmpfs with a size cap
  would bound total bytes, which no current control does.
- The subprocess backend has no filesystem confinement at all: user code runs as
  the server uid and can read `content/`, `.env` and `lootcode.db`. `docs/
  security.md` acknowledges this; `docs/code-execution.md` states guarantees 4
  and 6 that the default backend does not meet and should say so.
- `result.json` is user-writable, and a solution that writes it at import and
  `chmod`s it read-only has its forgery honoured. Combined with the point above
  (hidden `expected` values are readable on disk) these two together are the
  exploitable pair, and the fix is a nonce in `payload.json` echoed back, or
  having the parent read results over an fd it opened.
- `proc.communicate()` buffers the child's real stdout **in the API process**;
  375 MB of writes drove the parent's RSS from 16 MB to 768 MB. The run-wide
  output budget covers *captured* stdout only, not fd 1 written directly.
