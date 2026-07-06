# Test strengthening

A tool that **machine-generates hidden test cases to catch buggy _user_
solutions** — solutions that pass a problem's stored tests but are actually wrong.
It trusts the canonical solution as the oracle (runs it to compute expected
values) and selects the few inputs that best discriminate correct from buggy
solutions, using **two kinds of discriminator**:

- **Mutants** of the canonical — small plausible-wrong edits (catch *local* bugs).
- A **population** of independently-written LLM candidate solutions — some subtly
  wrong (catch *from-scratch* bugs that mutation structurally can't; see below).

An input that makes a discriminator **disagree with the canonical** is a candidate
hidden test. The model is never an oracle — it only supplies realistic wrong
solutions to select against; the canonical computes every expected value.

> Status (2026-07-05): **APPLIED.** 274 hidden cases were written across 219
> problems (`--apply --no-stress`, excluding 3 under-specified problems — see
> below). The blocker that paused apply on 2026-07-04 — the generator emitting
> *out-of-domain* inputs that would unfairly fail correct solutions (27 of the
> owner's 93 solved solutions flagged, **all** by illegal inputs) — was closed by
> gating every candidate through the problem's **stated-constraint validator**
> (`content/problems/<slug>/input_validator/input_validator.py`; see "Fairness"
> below, and `docs/input-validators.md`). Acceptance
> re-run after the gate: **27 → 0** of the owner's correct solutions flagged by an
> applied case. The stress case (T4) is **not** applied: it added zero
> discriminating power (+696 mutant / +152 population kills with or without it) and
> its oversized input/output poisons the app's single-batch grader
> (`run_submission(code, prob, prob.tests)` — no chunking), so it can only be
> served as a timing test, not baked as a correctness case. Every run is still
> `--dry-run` by default. Rationale/findings: `test-strengthening-plan.md` (§11).

## Why

Tests were largely LLM-generated: a handful of hand-picked inputs with
model-asserted expected values, verified only against the canonical itself. So a
user's wrong solution passes whenever the stored inputs don't happen to exercise
its bug. This tool replaces "ask the LLM for more tests" (same blind spots) with:
**enumerate many candidate inputs → compute expected by executing the trusted
canonical → keep the inputs that actually kill realistic bugs.**

## Run it

```bash
# Dry-run report for one problem (writes nothing):
python scripts/strengthen_tests.py median-from-data-stream -v

# A slug substring, in parallel:
python scripts/strengthen_tests.py --filter tree -j 8

# The whole bank (dry-run), then apply the selected cases:
python scripts/strengthen_tests.py -j 8
python scripts/strengthen_tests.py two-sum --apply     # append hidden cases to cases.json
```

Useful flags: `--apply` (write selected cases back as **hidden** tests),
`-j N` (**process** parallelism across problems), `--cap N` (max new cases per
problem, default 12), `--mut-cap N` (max mutants, default 60), `--fuzz N`
(random inputs), `--no-stress` (skip the T4 large case — **used for the applied
bank**, since a baked stress case poisons the app's single-batch grader),
`--validator`/`--no-validator` (the stated-constraint fairness gate, default on),
`--exclude SLUG` (skip a problem entirely — e.g. an under-specified statement the
validator can't fully gate), `--mutants`/`--population` (toggle each discriminator
source, both on by default). The exact command used for the 2026-07-05 apply:
`strengthen_tests.py -j 8 --fuzz 1500 --apply --no-stress --exclude house-robber
--exclude top-k-frequent-elements --exclude notification-dedup`. The report prints a
per-problem before→after **discriminator kill** score, how many **population bugs**
were caught, and the selected cases.

> **Fuzz budget:** subtle from-scratch bugs are *rare* in input space (the median
> `sol.py` bug appears only past ~500 random streams), so run the population path
> with a **large `--fuzz` (~1500)**. In-process grading makes this cheap
> per-problem. Mutants die at low fuzz, so the default 80 is fine when only mutating.

### Collecting the candidate population

The LLM population is collected separately (it is the slow, network-bound half) and
cached so selection can reuse it:

```bash
python scripts/collect_candidates.py -j 2          # whole bank (resumable), 2 = server slots
python scripts/collect_candidates.py two-sum -v    # one problem
python scripts/collect_candidates.py -j 2 --think  # slower reasoning-on top-up
```

Candidates land in `testgen_cache/candidates/<slug>.json` (git-ignored). The
collector is **resumable** — re-running fills only missing problems/configs.

After `--apply`, re-run `python scripts/verify_bank.py` (canonicals still pass) and
`python scripts/audit.py` (compare-mode fairness) before committing.

## Architecture

A standalone driver plus a small reusable library — mirrors `scripts/verify_bank.py`.
Nothing about the sandbox or judge is re-implemented: authoritative expected values
and canonical re-verification go through `app.executor.run_submission`, so
`compare` semantics and the `TreeNode` codec are honored automatically.

| Path | Role |
|------|------|
| `scripts/strengthen_tests.py` | Driver: load → generate → grade → select → report/apply. |
| `app/testgen/generators.py` | Candidate **inputs** by param type (`int[]`, grids, strings, `TreeNode`, …) **plus** a vocabulary-aware generator for design/"operations" problems. Covers edge shapes, seed perturbations, small fuzz, and one large stress input. Enforces parsed length bounds and **learned structural invariants** (see Fairness). |
| `app/testgen/constraints.py` | Best-effort parser for prose bounds in `problem.md` (`1 <= n <= 10^5`, comma-lists, `len(x)`/`x.length`). |
| `app/testgen/mutate.py` | AST **mutants** of the canonical: single-token edits (comparison/arithmetic/boolean swaps, off-by-one constants, `min`/`max`) **and statement-deletion (SDL)** — the missing-logic class. |
| `app/testgen/candidates.py` | LLM **candidate-solution population**: prompts the local qwen server (`:8090`) for several independent attempts per problem across temperatures / prompt styles. Screened + parsed into gradeable functions. |
| `scripts/collect_candidates.py` | Resumable, checkpointed collector for the population (2 workers = 2 server slots). |
| `app/testgen/select.py` | Greedy set-cover: minimal set of new cases that kills the discriminators (mutants + population) the existing suite misses; always keeps the stress case. |

### Pipeline (per problem)

1. Parse constraint bounds from `problem.md`.
2. Generate candidate inputs (edge ∪ seed-perturbation ∪ fuzz ∪ one stress).
3. Compute each candidate's expected by running the canonical; drop candidates it
   can't run cleanly or whose output serializes to >8 KB (a giant `expected` would
   also blow the user's own output cap).
4. Assemble **discriminators** = canonical mutants + the LLM candidate population
   (loaded from cache; screened for unsafe code, de-duped, canonical-identical
   dropped). Grade each against every input. An input that makes a discriminator
   diverge from the canonical **kills** it (an exception counts as divergence).
   **Stillborn** discriminators (killed by *every* input) are dropped — a broken
   candidate or a trivially-wrong mutant gives no signal about which inputs matter,
   and is by definition already caught by the existing seed tests.
5. Greedily select the minimal new cases that kill discriminators the existing
   suite misses, plus the force-kept stress case.
6. Recompute expected for kept cases through the **real sandbox** (authoritative,
   via `_grade` so an oversized stress case can't poison the batch) and verify the
   canonical passes each before writing.

### Performance & safety

Mutation *selection* runs **in-process** (compiling and executing mutants of the
trusted canonical, ~100× faster than a sandbox subprocess per grade — this is an
offline authoring script, like `scripts/seed.py`/`build_bank.py` which already
`exec` canonicals). Because SIGALRM cannot interrupt a runaway C-level call, the
in-process grading is wrapped in a **fork + hard-kill watchdog**. The authoritative
`expected` for every kept case is still computed through the real sandbox. Most
problems finish in ~0.1 s; a handful hit the ~15 s watchdog cap.

`TreeNode`-typed problems fall back to the (slow) sandbox grading path — an
in-process TreeNode codec is the obvious follow-up.

## Why two discriminator sources

Mutation-of-the-canonical selects tests that kill *local edits* — comparison flips,
off-by-one, dropped statements. Large and worthwhile, but **structurally unable** to
catch a *from-scratch* wrong solution whose bug is *distributed* across a different
implementation. The flagship case — `median-from-data-stream` with the wrong
`sol.py` — has a suite that already kills 100% of first-order mutants (zero
headroom), so mutation adds nothing, yet `sol.py` still passes.

The **population path** closes this: put independently-written candidate solutions
(from the local LLM) into the discriminator set. A wrong candidate is caught exactly
like a mutant — by an input where it diverges from the canonical. Validated:
injecting the real `sol.py` into median's population makes the selector pick a
discriminating stream, and `sol.py` flips **13/13 pass → 13/14 fail**. The model
stays out of the trust path (correct candidates just agree everywhere and contribute
nothing; the canonical is the only oracle).

## Fairness — respecting input preconditions

A generated input is only fair if it is **in-domain**: baking the canonical's answer
on an *invalid* input would unfairly fail a correct solution written to the contract.
The **primary, general guard** is the stated-constraint validator; the mechanical
guards below it are a cheap first pass that runs before it.

- **Stated-constraint validator** (`--validator`, default on): every candidate input
  is passed through the problem's own
  `content/problems/<slug>/input_validator/input_validator.py` `validate_input(...)`
  — a machine-generated, self-verified predicate for "does this
  input satisfy the ranges / lengths / shapes / char-sets / cross-param bounds the
  statement states?" — and dropped if it returns False. This is a *general* replacement
  for the piecemeal structural guards: it closed the whole out-of-domain leak class
  (0/1-domain grids, empty/ragged matrices, negative scalars, `k>len`, oversized
  stress, interval structure, char-sets) that had flagged 27 of the owner's 93 correct
  solutions, taking that to **0**. Safe-in-one-direction: a too-strict validator only
  loses coverage, never injects an illegal input. It cannot catch input↔answer
  *semantic* preconditions ("exactly one answer", "answer ≤ 2·10⁹", "events in time
  order"), which are deliberately not encoded — the 3 problems whose only residual leak
  is such a precondition (`house-robber`, `top-k-frequent-elements`, `notification-dedup`,
  the first two also missing an explicit Constraints section) were `--exclude`d from the
  apply pending statement tightening. The gate loads once per problem in
  `strengthen_tests._load_input_validator`, mirroring the audit's TreeNode dual-encoding.

The mechanical pre-pass guards (each also useful when a validator is absent):

- **Length bounds** parsed from the statement (`2 <= nums.length`) — no out-of-domain
  empty/short arrays.
- **Learned structural invariants** (`learn_array_invariants`): properties true across
  *every* stored example of a 1-D int-array param — `asc`/`desc` (sorted), `perm0`/
  `perm1` (a permutation of `0..n-1` / `1..n`), `rot` (sorted-or-rotated with distinct
  values). Generated inputs violating them are dropped. This is mechanical (no
  statement understanding) and **safe in one direction only**: over-inferring an
  invariant just makes generation more conservative; under-inferring is the residual
  risk. E.g. `binary-search` learns `{asc, rot}`, `array-nesting` learns `{perm0}`,
  `two-sum` learns nothing (arbitrary arrays stay free).
- **Graph node-label domains** (`learn_intmatrix_domain`, the "A+" guard): the integers
  inside an `int[][]` edge/adjacency param are node labels bounded by the contract
  (`0 <= node < n`, or `< len(adj)` for an adjacency list). Learned from the param's own
  examples: `nonneg` (no negative labels), `lt_len` (adjacency self-reference), and
  `lt_params` (endpoint labels below a scalar param such as `numCourses`; weight columns
  of `[u,v,w]` edges are exempt). Value grids (`grid`/`matrix`/`points`/`intervals`, and
  any non-graph-shaped matrix) are explicitly excluded, so nothing that is genuinely a
  2-D value array is affected. This closed a real leak: at whole-bank scale **13 of 27
  graph problems** had been selecting out-of-domain edges (`prerequisites=[[-34,-35]]`,
  `graph=[[3],[],[5,5],[5]]`); after the guard, **0**, with legitimate graph cases still
  selected and **no regression** on grid/matrix/interval problems.

Known residuals (see `resume.txt`): a size bound phrased as a bare variable (`1 <= N`)
rather than `len(A)` is missed; strict-invariant problems lose fuzz coverage (a
follow-up is invariant-*aware* generation — sort/permute/rotate rather than filter);
and input↔answer preconditions ("exactly one solution exists") aren't structural and
no input filter catches them.
