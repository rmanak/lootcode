# Hint generation & quality gate

Every problem can carry **up to 3 progressive hints** (`meta.json` `hints`, rendered
as collapsible "Hint N" panels — see `specs/problem-schema.md`). This doc covers how
hints are produced and, more importantly, how their **quality is gated** so they
guide without giving the answer away.

## The problem we're solving

Hints were originally generated one-shot by the local LLM with **no quality check**,
so a large fraction of final-tier hints leaked the whole solution — e.g. coin-change
hint 3 was *"For each amount, iterate through all coins and find the minimum previous
result plus one"*, which is the exact recurrence — while a minority were too vague to
help. The fix is a **generate → judge → regenerate** loop with the canonical solution
as the yardstick.

## What makes a good hint (the rubric)

Each tier has a **different job**, and the last tier must stop short of the answer:

| Tier | Job | Must NOT |
|------|-----|----------|
| Hint 1 | Light conceptual nudge / reframe / what to notice | name the technique |
| Hint 2 | Name the key technique, data structure, or subproblem | spell out the transition |
| Hint 3 | The crucial **insight** — what the state means, why it works, the base/edge case | state the recurrence, a formula, code, `dp[i][j]=…`, a step-by-step recipe, **narrate the named technique's operations** (push/pop, "advance the shorter pointer", "shrink the window while…"), or **name an algorithm together with all its bookkeeping** (e.g. "Kahn's + in-degrees + a queue") |

The last two "must NOT"s are the subtle ones: a hint can leak with no `dp[...]` and
no "first/then" wording, just by narrating how to *drive* a named structure or by
listing an algorithm's full bookkeeping. Naming a structure/algorithm is fine;
describing how to operate it is a reveal. Both have dedicated calibration examples in
`hint_judge_prompt.txt` and probes in the exemplar bench (`132-pattern`,
`course-schedule`).

"Reveal the idea; leave the derivation and the code to the solver." The full rubric,
with before/after examples, lives in the two prompt files below.

## Architecture

Three roles; the first two are the same local Qwen model in different modes, the
third is a one-time human/Claude calibration.

1. **Generator** (`generate_hints`, thinking off, fast) — writes hints from the
   **statement only**. The solution is deliberately withheld here: handing the model
   the answer is what causes transcription/leaks.
2. **Judge** (`judge_hints`, thinking **on**, **greedy** `temperature=0.0`) — a
   separate critic given the statement **+ the canonical solution + the candidate
   hints**. With the reference answer in hand it labels each hint `ok` / `reveals` /
   `vague` and lists the tiers to regenerate. This reference-grounded self-critique is
   the core of the gate. It decodes greedily on purpose: at 0.2 the same borderline
   leak was caught on one call and missed on the next — unacceptable for a gate — so
   the grader is deterministic run to run.
3. **Calibration** (`app/llm/hint_exemplars.json`) — 17 hand-curated gold hint sets
   spanning the pattern taxonomy (1D/2D/interval DP, stack, two-pointers, sliding
   window, grid DFS, topo-sort, tree DP, binary-search-on-answer, greedy, …). A few
   are baked into the prompts as few-shot; the whole set is the bench that
   `calibrate` grades the judge against.

`generate_hints_verified(statement, solution)` ties 1+2 into a loop: generate → a
cheap regex pre-filter (`leak_flags`, catches literal `dp[...]`/formulas for free) →
judge → regenerate the flagged tiers with the critique fed back, up to `tries` (3)
rounds. The first fully-clean set wins; otherwise the least-flagged set is returned.

### Files

| File | Role |
|------|------|
| `app/llm/hint_generator.py` | `generate_hints`, `leak_flags`, `judge_hints`, `generate_hints_verified` |
| `app/llm/hint_prompt.txt` | generator prompt — tier defs, anti-leak block, few-shot |
| `app/llm/hint_judge_prompt.txt` | critic prompt — the grading rubric |
| `app/llm/hint_exemplars.json` | gold hint sets: few-shot source + calibration bench |
| `scripts/improve_hints.py` | batch driver: `audit` / `fix` / `calibrate` |
| `scripts/generate_hints.py` | original one-shot bulk generator (no gate) — still used to seed hints on brand-new problems |

## The LLM server

All calls go to the local llama.cpp `llama-server` (**`http://localhost:8080`**, model
id **`qwen36`**) over the OpenAI-compatible API — no cloud calls. Start/relaunch it
with `/home/arman/claude_workspace/qwen/run.sh` (the `coding` profile suits it). The
code defaults to `:8080`; override with `--base-url` / `--model` or the
`LLM_SERVER_URL` / `LLM_MODEL` env vars. The judge runs with thinking **on**
(~20-40s/call), which is why it only runs during hardening, never in an interactive
path.

## Workflow

```bash
# 0. confirm the judge agrees with the gold exemplars before trusting it
python scripts/improve_hints.py calibrate

# 1. triage: grade every problem's existing hints, write .hints/audit.json
python scripts/improve_hints.py audit                 # all 741 (~hours, backgroundable)
python scripts/improve_hints.py audit --slug coin-change   # or a subset

# 2. preview fixes for the flagged problems (dry run is the DEFAULT). This now
#    writes a durable report, .hints/fix-dry.json, with old->new hints + the
#    judge's verdicts on the NEW set — resumable, so a killed run loses at most
#    --workers slugs and picks up where it stopped on re-run.
python scripts/improve_hints.py fix --from-report --dry-run

# 2b. browse the proposed replacements as a before->after page
python scripts/hint_compare_report.py --open

# 3. write them. TWO options:
#  (a) re-generate fresh and write only strictly-better results. NOTE: this
#      re-rolls at temperature>0, so the text differs from what you previewed.
python scripts/improve_hints.py fix --from-report --apply
#  (b) write the EXACT sets you reviewed from the dry-run report, verbatim, no
#      LLM calls (deterministic). --clean-only skips the still-flagged residuals.
python scripts/improve_hints.py apply-report --apply          # dry-run is the default

# 4. load the new hints into the DB
python scripts/seed.py
```

The audit report also renders to a browsable page for triage:
`python scripts/hint_audit_report.py --open` (filter by leak/vague, per-tier judge
reasons). Both HTML generators are self-contained static files — regenerate them
after each re-audit / re-fix.

- **Scope:** `audit` reads everything; `fix` only rewrites hint sets flagged by the
  judge/heuristic. Clean hints are left byte-for-byte alone (surgical `meta.json`
  write — only the `hints` block changes).
- **Safety:** `fix` overwrites a problem **only if the new set is strictly better**
  than the old (fewer flagged tiers, or fully clean), so a run can never make a
  problem's hints worse. `--no-baseline` skips the old-hint judging and always trusts
  the freshly-gated set.
- **Resumable:** each file is written the moment its hints are accepted; an
  interrupted run loses nothing — re-run to continue.
- **Speed:** `--workers` matches the server's slot count (default 4). `--no-judge`
  runs the heuristic pre-filter only (fast, catches literal pseudocode but misses
  prose recurrences). `--tries` bounds regeneration rounds per problem.

## Recalibrating

If the judge is mis-grading (too strict → churn and residual flags; too lax → leaks
slip through), tune `app/llm/hint_judge_prompt.txt` and re-run `calibrate` until the
gold sets grade `ok` and the seeded leaks are caught. Adjust the tier definitions and
few-shot in `app/llm/hint_prompt.txt` to change what the generator produces. Add new
patterns to `hint_exemplars.json` when a class of problem is under-served.
