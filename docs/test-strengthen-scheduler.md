# Background test-strengthening scheduler

An unattended sweep that hardens the hidden test suites of every problem in the
**union of the `blind-73`, `top-interview-150`, and `top-google` collections**
(284 slugs), one problem per hour, by running the **`test-strengthener` agent**
headlessly. It is driven by **system cron**, so it keeps running across Claude
Code sessions and reboots, and it is fully **resumable** — a persistent queue is
the single source of truth for what's done and what's left.

- Driver: [`scripts/strengthen_scheduler.py`](../scripts/strengthen_scheduler.py)
- State (gitignored): `.strengthen/`
  - `queue.json` — ordered slug list + per-slug status (`pending` → `in_progress` → `done`/`failed`).
  - `cron.log` — one block per hourly fire (START / DONE / RETRY / FAIL lines).
  - `runs/<slug>.log` — the full headless-agent transcript for that slug.
  - `scheduler.lock` — flock; guarantees two hours never overlap.

## What one hourly fire does

1. Takes a **non-blocking flock**. If the previous hour's run is still going
   (agent took >1h), it logs "skipping this hour" and exits — no overlap, no
   double-spend.
2. Claims the next `pending` slug and marks it `in_progress`.
3. Runs `claude -p` in the repo (`--dangerously-skip-permissions`, model
   `claude-opus-4-8`, 55-min timeout). The prompt tells it to use the
   `test-strengthener` subagent to add coverage-widening hidden cases for **only
   that slug**, canonical-as-only-oracle, every input gated through the problem's
   `input_validator`, **no git commits**, no edits outside that slug's dir.
4. Marks the slug `done` on success; on failure/timeout it requeues (up to
   `MAX_ATTEMPTS=3`) then marks it `failed` and moves on, so one bad slug never
   stalls the sweep.

At 1 slug/hour, 284 slugs ≈ **12 days**. Changes are left **uncommitted** in the
working tree for you to review (`git status` / `git diff`) and commit in batches.

## Install the cron job

The job line uses **absolute paths** (cron runs from `$HOME` with a bare PATH, so
no `cd` and no relative paths):

```
0 * * * * /home/arman/claude_workspace/lootcode/.venv/bin/python /home/arman/claude_workspace/lootcode/scripts/strengthen_scheduler.py run >> /home/arman/claude_workspace/lootcode/.strengthen/cron.log 2>&1
```

Install it by writing a full crontab file (avoids the quoting/`!`/glob mangling
that bites the `echo … | crontab -` one-liner in an interactive shell):

```bash
R=/home/arman/claude_workspace/lootcode
crontab -l > "$R/.strengthen/new_crontab.txt"          # keep existing jobs verbatim
printf '0 * * * * %s/.venv/bin/python %s/scripts/strengthen_scheduler.py run >> %s/.strengthen/cron.log 2>&1\n' "$R" "$R" "$R" >> "$R/.strengthen/new_crontab.txt"
crontab "$R/.strengthen/new_crontab.txt"               # install
crontab -l | tail -1                                   # verify our line is there
```

Runs at minute 0 of every hour. (The crontab already pins `CRON_TZ` to Pacific;
this job doesn't care about wall-clock time.)

## Monitor

```bash
cd /home/arman/claude_workspace/lootcode
.venv/bin/python scripts/strengthen_scheduler.py status      # done/pending/failed + ETA + recent
.venv/bin/python scripts/strengthen_scheduler.py list pending
tail -f .strengthen/cron.log                                 # watch hourly fires
less .strengthen/runs/<slug>.log                             # one agent transcript
```

A Slack ping (via `~/.claude/slack-send.sh`) fires on any slug that **fails**
after all retries, and once when the **whole queue completes**.

## Kill / pause / resume

**Stop it (remove the cron line):**

```bash
crontab -l | grep -v 'strengthen_scheduler.py' | crontab -
```

That prevents any new hourly run. A run already in flight keeps going until it
finishes; to also stop that one:

```bash
pkill -f 'strengthen_scheduler.py run'   # kills the driver
pkill -f 'claude -p'                     # kills the in-flight agent, if any
# then un-stick the slug it was on:
.venv/bin/python scripts/strengthen_scheduler.py reset-stuck
```

**Pause** = remove the cron line; **resume** = re-add it (state is untouched, it
picks up at the next pending slug). To **re-do** a slug: `reset <slug>`. To start
the whole sweep over: `init --force`.

## Tuning

Env vars read by the driver (set them in the cron line if you want to override):

| Var | Default | Meaning |
|-----|---------|---------|
| `STRENGTHEN_MODEL` | `claude-opus-4-8` | Agent model. Set `claude-sonnet-5` to cut cost. |
| `STRENGTHEN_TIMEOUT` | `3300` | Per-slug hard timeout (seconds). |
| `STRENGTHEN_MAX_ATTEMPTS` | `3` | Retries before a slug is marked `failed`. |
| `STRENGTHEN_CLAUDE_BIN` | `/home/arman/.local/bin/claude` | Path to the `claude` CLI. |

## Notes / caveats

- **`--dangerously-skip-permissions`** is required because the run is unattended
  (no TTY to approve tool calls). It is scoped by a tight prompt (one slug, no
  git, no edits outside the slug dir) and by the `test-strengthener` agent's own
  rules; the project `guard-outside-project.py` hook still forces a block on any
  file access above the repo. Review the accumulated diff before committing.
- The driver activates the repo **`.venv`** (prepends it to `PATH`) so the
  agent's `python scripts/oracle.py` calls have the deps under cron's bare PATH.
- To run one slug by hand right now (bypassing cron):
  `.venv/bin/python scripts/strengthen_scheduler.py run`.
