# Code execution (running untrusted code safely)

> This is the highest-risk subsystem. **Read before changing `services/executor`
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
   - **output size** (`EXECUTOR_MAX_OUTPUT_KB`, truncate beyond).
6. **Side-effect free toward us** — no access to host, API, DB, env secrets, or
   other submissions.

If a change can weaken any of the above, stop and write an ADR.

## Backends in this repository

Two backends implement one interface (`app/executor/`); pick via `EXECUTOR_BACKEND`:

- **`subprocess` (default).** Runs `harness.py` in a child process with POSIX
  rlimits (address space / CPU / file size / PID cap), a per-test `SIGALRM`
  timeout, an overall kill-timeout, a minimal env (no secrets), and a throwaway
  working dir. **It does NOT block network access** — intended for a personal /
  home instance where solvers are trusted (you and family on the LAN).
- **`docker` (opt-in).** Runs the same harness in a throwaway container with
  `--network none --cap-drop ALL --security-opt no-new-privileges --read-only`,
  capped memory/CPU/PIDs, and a non-root user — for untrusted, multi-user use.
  Build the image: `docker build -f infra/runner.Dockerfile -t lootcode-runner .`

Expected outputs never enter the sandbox (only inputs do); comparison and scoring
happen in the trusted parent (`app/executor/__init__.py`). The adversarial suite
lives in `tests/test_executor.py` — keep it green.

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
