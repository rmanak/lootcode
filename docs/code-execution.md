# Code execution (running untrusted code safely)

> This is the highest-risk subsystem. **Read before changing `app/executor/`
> or any path that runs user code.** Pair changes with the
> `executor-security-reviewer` subagent and `docs/security.md`.

## The problem

We run arbitrary, untrusted, possibly hostile code submitted by users. It will
try (intentionally or not) to: read secrets, reach the network, exhaust CPU/RAM,
fork-bomb, fill the disk, escape the container, or attack other users' runs.
Containment is non-negotiable.

## Non-negotiable sandbox guarantees

Every run MUST be:

1. **Isolated** — its own disposable sandbox (container/microVM), destroyed after
   the run. No reuse of a dirty environment.
2. **Network-disabled** — no outbound/inbound network at all.
3. **Unprivileged** — non-root user, all Linux capabilities dropped, no new
   privileges (`no-new-privileges`), seccomp profile restricting syscalls.
4. **Read-only filesystem** — except one small, size-capped scratch dir (tmpfs).
5. **Resource-limited** — hard caps on:
   - wall-clock **time** (`EXECUTOR_TIME_LIMIT_MS`),
   - **memory** (`EXECUTOR_MEMORY_LIMIT_MB`, via cgroups),
   - **CPU** shares,
   - **processes/threads** (PID limit → stops fork bombs),
   - **output size** (`EXECUTOR_MAX_OUTPUT_KB`, truncate beyond) — a budget for
     the **whole run**, not per test, because it has to match the file-size
     rlimit covering the single `result.json` that holds every test's output.
     Truncation is announced in the captured output, never silent.
6. **Side-effect free toward us** — no access to host, API, DB, env secrets, or
   other submissions.

If a change can weaken any of the above, stop and write an ADR.

The **file-size** rlimit is not in that list on purpose. It bounds a single file
(so it never limited total bytes written) and exists to size `result.json`, not
to stop a submission filling the disk — the wall-clock limit and the workdir
cleanup are what do that, and less comfortably than they look. See
[ADR 0002](adr/0002-sandbox-file-size-limit.md), which also records where the
default subprocess backend falls short of guarantees 4 and 6.

## One launcher, two backends, two harnesses

`app/executor/sandbox.py` is the **launcher**: it materialises a throwaway run
directory, applies the limits, starts the process, and parses `result.json`.
Every harness in the tree goes through it, which is what stops a second one
from quietly getting a weaker boundary — `run_harness` dispatches on
`EXECUTOR_BACKEND`, so turning on `docker` turns it on for *all* grading, and
the container flags are written once (`sandbox.docker_command`).

Two things in there are worth knowing:

- **The process cap is headroom, not an absolute** (`sandbox.nproc_limit`).
  `RLIMIT_NPROC` counts every task the *machine's user* already owns — the
  browser and editor included — so a flat 256 means "256 minus whatever else
  is running", which on a workstation can be nothing at all. It is now
  measured-plus-64, which is what the anti-fork-bomb control always meant.
- **Run directories live in a private parent** (`sandbox.make_workdir`):
  `/tmp/lootcode-runs-<uid>`, mode 0700, `lstat`-checked so a pre-planted
  symlink or a squatted directory is refused. A run directory in a listable
  `/tmp` hands the submitted code to every local user.
- **The container runs as *our* uid, not `nobody`** (`sandbox.docker_command`,
  which refuses to run at all as root). A bind mount has no uid mapping, so
  anything another user created in the run directory — a `__pycache__` with a
  compiled copy of the submission, say — could not be deleted afterwards, and
  the "destroyed after the run" guarantee quietly stopped holding. Teardown
  (`sandbox._destroy`) now logs a warning instead of swallowing the failure.
- **The container gets the same file-size cap as the subprocess backend**
  (`--ulimit fsize=`). `/sandbox` is a host bind mount, so `--tmpfs /tmp`
  bounds nothing that matters; without the ulimit a container could fill the
  host disk, and the harness's own degradation ladder could never fire.
- **A timed-out container is killed by name** (`sandbox.kill_container`).
  `subprocess` timing out kills the `docker run` *client*; the daemon keeps
  the container, and an infinite loop keeps its CPU share indefinitely.
- **The harness's stdout/stderr go to `/dev/null`, and the process group is
  always killed.** Nothing grades on them, and *reading* them meant waiting
  for EOF — which one `setsid` grandchild could hold open for the entire run
  budget. Killing the group unconditionally (not only on timeout) is what
  makes "its own disposable sandbox" true for orphans too.

### The run directory belongs to the submission

Anything read back out of it is a path untrusted code controls, so neither
harness uses a plain `open()`:

- **Writing** `result.json` (`_open_result` in both harnesses) unlinks first,
  then creates with `O_EXCL | O_NOFOLLOW | O_NONBLOCK`. A submission that
  plants a fifo there otherwise blocks the harness for the whole run budget;
  a symlink would redirect the write.
- **Reading** it back (`sandbox.read_results`) opens with `O_NOFOLLOW |
  O_NONBLOCK`, requires a regular file, and caps the size. `os.symlink(
  "/dev/zero", "result.json")` previously made the *server* read until it was
  OOM-killed — with SQLite mid-write, that is the corruption scenario
  `docs/database.md` exists for — and a fifo blocked the request thread and
  leaked the run directory with it. Both are pinned by tests
  (`tests/test_executor.py`, `tests/test_sandbox.py`).

Two backends implement one interface (`app/executor/`); pick via `EXECUTOR_BACKEND`:

- **`subprocess` (default).** Runs `harness.py` in a child process with POSIX
  rlimits (address space / CPU / file size / PID cap), a per-test `SIGALRM`
  timeout, an overall kill-timeout, a minimal env (no secrets), and a throwaway
  working dir. **It does NOT block network access** — intended for a personal /
  home instance where solvers are trusted (you and family on the LAN).
- **`docker` (opt-in).** Runs the same harness in a throwaway container with
  `--network none --cap-drop ALL --security-opt no-new-privileges --read-only`,
  capped memory/CPU/PIDs/file-size, and a non-root user (the app's own uid, so
  the bind-mounted run directory stays deletable) — for untrusted, multi-user
  use.
  Build the image: `docker build -f infra/runner.Dockerfile -t lootcode-runner .`

Expected outputs never enter the sandbox (only inputs do); comparison and scoring
happen in the trusted parent (`app/executor/__init__.py`).

### The second harness: ICF

The optional `icf/` extension (`docs/extensions.md`) grades differently — its
oracle *is* code, so authored test functions run beside the solution and the
"expected values stay outside" property above cannot hold for it. It uses the
same launcher and the same limits, and recovers as much of the guarantee as it
can inside the sandbox:

- the harness process that writes `result.json` never imports the solution; a
  forked worker runs the cases and reports over a pipe, so a case with no
  report is failed, never passed;
- test sources (and their `__pycache__` copies — `python -I` ignores
  `PYTHONDONTWRITEBYTECODE`) are deleted before the worker starts;
- visible and hidden cases are graded in **separate runs**, and the hidden
  run's messages and output are discarded, so nothing hidden can be printed
  back to the solver.

What it does *not* get is a verdict the submission cannot influence at all.
See [ADR 0003](adr/0003-icf-grading-runs-two-processes.md) and
`icf/docs/security.md`.

The adversarial suite
lives in `tests/test_executor.py` — keep it green.

### Rich types (`TreeNode`, `ListNode`, `DoublyLinkedList`)

A problem may declare a parameter/return as a rich type (`TreeNode`; the singly-
linked `ListNode`; the doubly-linked `Node`, token `DoublyLinkedList`). The wire
format on disk and across the boundary stays a plain JSON value (a tree is a
level-order array; a linked list is a flat value array); a small **codec** in
`harness.py` (`_CODECS`) converts array⇄object on the **untrusted side** so solvers
work with real objects, then re-serializes a returned object back to the array
*before* the JSON gate — so the parent still grades on JSON arrays and the trust
boundary is unchanged. Because these codecs run in-sandbox next to hostile code
they are stdlib-only, **iterative** (no recursion → no stack-overflow DoS), and
**node-capped** (`_MAX_TREE_NODES` for trees, `_MAX_LIST_NODES` for lists), and a
returned object is encoded while the per-test `SIGALRM` is still armed, so a
cyclic/huge return can't hang the harness. Adding a rich type = one `_CODECS`
entry; pair any change here with the `executor-security-reviewer`.

## Execution flow

```
job {submissionId, languageId, code, testCases, limits}
  │
  ├─ write code + a per-language harness into a fresh sandbox scratch dir
  ├─ compile (if needed) with the same limits  → compile error ⇒ report, stop
  ├─ for each test case:
  │     run harness(input) under limits
  │     capture stdout/stderr/exit/time/memory
  │     compare output to `expected` (normalized)
  │     classify: pass | wrong-answer | TLE | MLE | runtime-error
  ├─ destroy sandbox
  └─ report per-test results
```

## Harness model

Each language has a thin **harness** that: reads a test `input` (JSON), calls the
user's function (name/params from the problem's `functionSpec`), serializes the
return value, and prints it in a canonical form for comparison. Keep harnesses
tiny and audited; they are part of the trusted boundary.

## Implementation options (pick one — record in an ADR)

| Option | Pros | Cons |
|--------|------|------|
| **Self-built**: Docker + gVisor or Firecracker microVMs + cgroups/seccomp | full control, strongest isolation | most work to build & operate |
| **Judge0** (self-hosted) | fast to adopt, many languages | another service to run; less control |
| **Piston** | simple, lightweight | fewer guarantees; vet isolation |
| **Hosted sandbox** (e2b, etc.) | no ops | cost; data leaves your infra |

**Recommendation for v1:** start with **Judge0 self-hosted** to ship, OR a minimal
Docker+gVisor executor if you want to own it. Either way, enforce the guarantees
above at the orchestration layer too (timeouts, output caps) — defense in depth.

## Testing the executor

- Maintain an adversarial test suite: infinite loop (→TLE), `while True: fork()`
  (→PID cap), huge allocation (→MLE), network call (→blocked), file read of
  `/etc/passwd` or env (→denied), giant stdout (→truncated).
- These tests must pass in CI before any executor change merges.
