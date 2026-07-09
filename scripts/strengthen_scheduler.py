#!/usr/bin/env python3
"""
Background scheduler that hardens the hidden test suites of every problem in the
union of the blind-73 / top-interview-150 / top-google collections, one problem
per invocation, by running the `test-strengthener` agent headlessly.

It is meant to be driven by cron once an hour (see docs/test-strengthen-scheduler.md):

    0 * * * * cd /home/arman/claude_workspace/lootcode && \
      .venv/bin/python scripts/strengthen_scheduler.py run >> .strengthen/cron.log 2>&1

Each `run`:
  1. Takes a non-blocking flock so two hours never overlap (a long run keeps the
     next hour's fire from starting a second agent).
  2. Claims the next `pending` slug from .strengthen/queue.json (persistent state).
  3. Launches `claude -p` in the repo, which uses the test-strengthener subagent to
     add coverage-widening hidden cases for that one slug (canonical is the only
     oracle; every input gated through the problem's input_validator).
  4. Marks the slug done (or requeues/fails it) and logs.

State lives under .strengthen/ (gitignored). The queue is the single source of
truth for what's left, so the sweep is fully resumable across reboots/sessions.

Subcommands:
    run [--slug SLUG] [--slugs-file FILE] [--no-lock] [--force]
            Run the agent on specific slug(s). --slug can be repeated; --slugs-file
            reads one slug per line (blank lines and # comments ignored). Slugs
            already marked `done` are skipped so a killed run resumes by re-passing
            the same list; --force redoes them anyway. --no-lock skips the flock for
            parallel manual runs. With no flags, claims the next pending slug from
            the queue (the cron action).
    status          Print progress counts and a short tail of recent activity.
    list [STATUS]   List slugs (optionally filtered: pending|in_progress|done|failed).
    init [--force]  (Re)build the queue from the collections. --force discards state.
    reset SLUG      Put one slug back to pending.
    reset-stuck     Reset any in_progress slug back to pending (use after a crash).

Config is via constants below, overridable by env vars (STRENGTHEN_*).
"""
from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
STATE_DIR = REPO / ".strengthen"
QUEUE_FILE = STATE_DIR / "queue.json"
LOCK_FILE = STATE_DIR / "scheduler.lock"
RUNS_DIR = STATE_DIR / "runs"

COLLECTIONS = ["blind-73", "top-interview-150", "top-google"]
CONTENT_ROOTS = [REPO / "content" / "problems", REPO / "content" / "problems-extended"]

# The agent runs headlessly. cron has a bare PATH, so use absolute paths and
# prepend the repo venv so the agent's `python scripts/oracle.py` has the deps.
CLAUDE_BIN = os.environ.get("STRENGTHEN_CLAUDE_BIN", "/home/arman/.local/bin/claude")
MODEL = os.environ.get("STRENGTHEN_MODEL", "claude-opus-4-8")  # switch to claude-sonnet-5 to cut cost
VENV_BIN = REPO / ".venv" / "bin"
TIMEOUT_SEC = int(os.environ.get("STRENGTHEN_TIMEOUT", "3300"))  # 55 min; leaves headroom before the next hour
MAX_ATTEMPTS = int(os.environ.get("STRENGTHEN_MAX_ATTEMPTS", "3"))
SLACK = Path(os.environ.get("STRENGTHEN_SLACK", "/home/arman/.claude/slack-send.sh"))


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def log(msg: str) -> None:
    print(f"[{now_iso()}] {msg}", flush=True)


def slack(msg: str) -> None:
    """Best-effort Slack ping; never fails the run."""
    try:
        if SLACK.exists():
            subprocess.run([str(SLACK), msg], timeout=30,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Queue
# ---------------------------------------------------------------------------
def build_union_slugs() -> list[str]:
    seen: set[str] = set()
    order: list[str] = []
    for name in COLLECTIONS:
        path = REPO / "content" / "collections" / f"{name}.json"
        if not path.exists():
            log(f"WARNING: collection {name}.json not found, skipping")
            continue
        data = json.loads(path.read_text())
        for slug in data.get("problems", []):
            if slug in seen:
                continue
            seen.add(slug)
            if any((root / slug).is_dir() for root in CONTENT_ROOTS):
                order.append(slug)
            else:
                log(f"WARNING: slug '{slug}' not found on disk, skipping")
    return order


def build_queue() -> dict:
    slugs = build_union_slugs()
    return {
        "created": now_iso(),
        "source_collections": COLLECTIONS,
        "model": MODEL,
        "slugs": [
            {"slug": s, "status": "pending", "attempts": 0,
             "started": None, "finished": None, "note": None}
            for s in slugs
        ],
    }


def load_queue() -> dict:
    return json.loads(QUEUE_FILE.read_text())


def save_queue(q: dict) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    tmp = QUEUE_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(q, indent=2))
    os.replace(tmp, QUEUE_FILE)  # atomic


def ensure_queue() -> dict:
    if not QUEUE_FILE.exists():
        STATE_DIR.mkdir(exist_ok=True)
        q = build_queue()
        save_queue(q)
        log(f"initialized queue with {len(q['slugs'])} slugs")
    return load_queue()


def counts(q: dict) -> dict[str, int]:
    c = {"pending": 0, "in_progress": 0, "done": 0, "failed": 0}
    for e in q["slugs"]:
        c[e["status"]] = c.get(e["status"], 0) + 1
    return c


# ---------------------------------------------------------------------------
# The per-slug agent run
# ---------------------------------------------------------------------------
def build_prompt(slug: str) -> str:
    return f"""You are running UNATTENDED as a scheduled background job inside the lootcode repo.
Harden the hidden test suite of exactly ONE problem, slug: "{slug}".

Use the test-strengthener subagent (the Task tool) to do this. Its coverage-first
workflow: run `python scripts/oracle.py cover {slug}` (dry run), review the proposed
in-domain cases, then apply the good ones with `python scripts/oracle.py cover {slug} --apply`.
If a concrete wrong solution is worth trying, `oracle.py fuzz {slug} --solution <f> --shrink`
is add-only. The canonical solution is the ONLY oracle — never hand-write an `expected`.
Every input must satisfy the problem's input_validator; if the validator wrongly rejects a
genuine edge case or wrongly accepts an illegal input, fix or flag it per the agent's rules —
never bake an unfair case on illegal input.

Hard constraints for this unattended run:
- Work ONLY on slug "{slug}". Do not touch any other problem.
- Do NOT run `git commit`, `git push`, or any git write. Leave changes in the working tree.
- This slug's directory is either content/problems/{slug}/ OR content/problems-extended/{slug}/ —
  some slugs live in the extended set; use whichever one actually exists on disk. Do NOT edit any
  file outside that one directory (a validator fix for THIS slug is the only exception).
- Do not start servers or long-running processes; finish within your time budget.

End your final message with exactly one line of this form (used for automated logging).
You MUST replace the placeholders with actual concrete values — do NOT output the placeholder
text literally. Examples of correct output:

  RESULT: two-sum added=6 validator_changed=no notes=added 6 single-answer cases
  RESULT: basic-calculator added=3 validator_changed=yes notes=fixed validator to reject empty input
  RESULT: valid-parentheses added=0 validator_changed=no notes=suite already comprehensive

Your RESULT line for {slug}:
"""


def run_agent(slug: str) -> tuple[bool, str]:
    """Run the test-strengthener agent on one slug. Returns (ok, result_line)."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_log = RUNS_DIR / f"{slug}.log"

    env = os.environ.copy()
    env["PATH"] = f"{VENV_BIN}:{os.path.dirname(CLAUDE_BIN)}:" + env.get("PATH", "")
    env["VIRTUAL_ENV"] = str(REPO / ".venv")
    env.pop("PYTHONHOME", None)

    cmd = [CLAUDE_BIN, "-p", build_prompt(slug),
           "--dangerously-skip-permissions", "--model", MODEL]

    started = time.time()
    with run_log.open("w") as fh:
        fh.write(f"# strengthen run for '{slug}' @ {now_iso()}\n# cmd: {' '.join(cmd[:1]+cmd[2:])}\n\n")
        fh.flush()
        try:
            proc = subprocess.run(cmd, cwd=str(REPO), env=env, timeout=TIMEOUT_SEC,
                                  stdout=fh, stderr=subprocess.STDOUT)
        except subprocess.TimeoutExpired:
            fh.write(f"\n# TIMEOUT after {TIMEOUT_SEC}s\n")
            return False, f"timeout after {TIMEOUT_SEC}s"

    dur = int(time.time() - started)
    ok = proc.returncode == 0
    result_line = f"exit={proc.returncode} dur={dur}s"
    # Best-effort: pull the agent's RESULT: line out of the transcript.
    try:
        for line in reversed(run_log.read_text().splitlines()):
            if line.strip().startswith("RESULT:"):
                result_line = line.strip()
                break
    except Exception:
        pass
    return ok, result_line


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def run_one(slug: str) -> int:
    """Run the agent on a single slug, updating the queue. Returns exit code."""
    q = ensure_queue()
    entry = next((e for e in q["slugs"] if e["slug"] == slug), None)
    if entry is None:
        log(f"WARNING: slug '{slug}' not in queue, adding as pending")
        entry = {"slug": slug, "status": "pending", "attempts": 0,
                 "started": None, "finished": None, "note": None}
        q["slugs"].append(entry)
        save_queue(q)

    entry["status"] = "in_progress"
    entry["attempts"] += 1
    entry["started"] = now_iso()
    save_queue(q)
    c = counts(q)
    log(f"START {slug} (attempt {entry['attempts']}/{MAX_ATTEMPTS}) "
        f"[done {c['done']} / pending {c['pending']} / failed {c['failed']}]")

    ok, result_line = run_agent(slug)

    q = load_queue()
    entry = next(e for e in q["slugs"] if e["slug"] == slug)
    entry["finished"] = now_iso()
    entry["note"] = result_line
    if ok:
        entry["status"] = "done"
        log(f"DONE  {slug} :: {result_line}")
    elif entry["attempts"] >= MAX_ATTEMPTS:
        entry["status"] = "failed"
        log(f"FAIL  {slug} (gave up after {entry['attempts']}) :: {result_line}")
        slack(f":warning: strengthen scheduler: `{slug}` FAILED after "
              f"{entry['attempts']} attempts — {result_line}")
    else:
        entry["status"] = "pending"
        log(f"RETRY {slug} (attempt {entry['attempts']}) :: {result_line}")
    save_queue(q)
    return 0


def cmd_run(slugs: list[str] | None = None,
            slugs_file: str | None = None,
            no_lock: bool = False,
            force: bool = False) -> int:
    # Resolve the slug list
    if slugs_file:
        with open(slugs_file) as f:
            file_slugs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        file_slugs = []

    target_slugs = (slugs or []) + file_slugs

    STATE_DIR.mkdir(exist_ok=True)

    # Acquire lock (unless --no-lock for parallel manual runs)
    lock_fd = None
    if not no_lock:
        lock_fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_RDWR)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            log("another run holds the lock; skipping")
            return 0

    try:
        if target_slugs:
            # Run specific slugs. Skip ones already done (resumable) unless --force.
            q = ensure_queue()
            done = {e["slug"] for e in q["slugs"] if e["status"] == "done"}
            for slug in target_slugs:
                if slug in done and not force:
                    log(f"SKIP  {slug} (already done; use --force to redo)")
                    continue
                run_one(slug)
        else:
            # Default: claim next pending from queue
            q = ensure_queue()
            entry = next((e for e in q["slugs"] if e["status"] == "pending"), None)
            if entry is None:
                c = counts(q)
                if c["in_progress"]:
                    log(f"no pending slugs; {c['in_progress']} stuck in_progress (run reset-stuck)")
                else:
                    log(f"queue complete — done={c['done']} failed={c['failed']}")
                return 0
            run_one(entry["slug"])

        # Final status
        q = ensure_queue()
        c = counts(q)
        if c["pending"] == 0 and c["in_progress"] == 0:
            slack(f":white_check_mark: strengthen scheduler finished the whole queue — "
                  f"done={c['done']} failed={c['failed']} ({len(q['slugs'])} slugs).")
            log(f"QUEUE COMPLETE — done={c['done']} failed={c['failed']}")
        return 0
    finally:
        if lock_fd is not None:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)


def cmd_status() -> int:
    q = ensure_queue()
    c = counts(q)
    total = len(q["slugs"])
    pct = 100 * c["done"] // total if total else 0
    print(f"queue: {total} slugs  |  done {c['done']} ({pct}%)  "
          f"pending {c['pending']}  in_progress {c['in_progress']}  failed {c['failed']}")
    hrs = c["pending"] + c["in_progress"]
    if hrs:
        print(f"~{hrs} hours of work left at 1 slug/hour")
    recent = [e for e in q["slugs"] if e["finished"]]
    recent.sort(key=lambda e: e["finished"], reverse=True)
    if recent:
        print("\nmost recent:")
        for e in recent[:8]:
            print(f"  {e['finished']}  {e['status']:11} {e['slug']:40} {e.get('note') or ''}")
    if c["failed"]:
        print("\nfailed:")
        for e in q["slugs"]:
            if e["status"] == "failed":
                print(f"  {e['slug']:40} {e.get('note') or ''}")
    return 0


def cmd_list(status: str | None) -> int:
    q = ensure_queue()
    for e in q["slugs"]:
        if status is None or e["status"] == status:
            print(f"{e['status']:11} {e['slug']}")
    return 0


def cmd_init(force: bool) -> int:
    if QUEUE_FILE.exists() and not force:
        print(f"queue already exists at {QUEUE_FILE} (use --force to rebuild)")
        return 1
    q = build_queue()
    save_queue(q)
    print(f"built queue with {len(q['slugs'])} slugs -> {QUEUE_FILE}")
    return 0


def cmd_reset(slug: str) -> int:
    q = ensure_queue()
    e = next((e for e in q["slugs"] if e["slug"] == slug), None)
    if not e:
        print(f"slug not in queue: {slug}")
        return 1
    e.update(status="pending", attempts=0, started=None, finished=None, note=None)
    save_queue(q)
    print(f"reset {slug} -> pending")
    return 0


def cmd_reset_stuck() -> int:
    q = ensure_queue()
    n = 0
    for e in q["slugs"]:
        if e["status"] == "in_progress":
            e["status"] = "pending"
            n += 1
    save_queue(q)
    print(f"reset {n} in_progress -> pending")
    return 0


def parse_run_args(args: list[str]):
    """Parse --slug, --slugs-file, --no-lock, --force from run args."""
    slugs = []
    slugs_file = None
    no_lock = False
    force = False
    i = 0
    while i < len(args):
        if args[i] == "--slug" and i + 1 < len(args):
            slugs.append(args[i + 1])
            i += 2
        elif args[i] == "--slugs-file" and i + 1 < len(args):
            slugs_file = args[i + 1]
            i += 2
        elif args[i] == "--no-lock":
            no_lock = True
            i += 1
        elif args[i] == "--force":
            force = True
            i += 1
        else:
            i += 1
    return slugs, slugs_file, no_lock, force


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "status"
    if cmd == "run":
        slugs, slugs_file, no_lock, force = parse_run_args(argv[2:])
        return cmd_run(slugs=slugs or None, slugs_file=slugs_file,
                       no_lock=no_lock, force=force)
    if cmd == "status":
        return cmd_status()
    if cmd == "list":
        return cmd_list(argv[2] if len(argv) > 2 else None)
    if cmd == "init":
        return cmd_init("--force" in argv)
    if cmd == "reset":
        if len(argv) < 3:
            print("usage: reset <slug>")
            return 1
        return cmd_reset(argv[2])
    if cmd == "reset-stuck":
        return cmd_reset_stuck()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
