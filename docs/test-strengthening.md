# Test strengthening — design notes

> **Status: nothing is implemented.** The previous engine (`authoring/testgen/`,
> `scripts/oracle.py`, `scripts/strengthen_tests.py`, `scripts/strengthen_scheduler.py`,
> the `test-strengthener` agent) was **retired on 2026-07-29**. This file is the
> plan for what replaces it. Do not resurrect the old design; see "Why the old one
> went" before proposing anything clever.

## The problem

A hidden test suite is weak when a **wrong** solution scores 100 — the
"passes here, fails on LeetCode" gap. Strengthening means adding hidden cases
that separate correct solutions from wrong ones.

## The approach

Two things the repo already has, and nothing else:

1. **A verified canonical solution** — the only oracle. Every `expected` is
   whatever the canonical returns. Never hand-write an expected value.
2. **A per-problem `input_validator.py`** (`validate_input(...) -> bool`) — the
   fairness gate. Every candidate input must satisfy it, so no case can punish a
   solution for an input the statement forbids.

The process:

```
sample a random input  ->  validate_input()?  ->  run canonical  ->  store (input, output)
```

That is the whole idea. Suites are weak because they under-explore the
input/output space, and random sampling explores it. The 2026-07-29
`champagne-tower` session is the worked example: 11 hand-picked cases let a wrong
solution through; 36 sampled ones took it to 28/47.

## The one non-obvious part: stratify by *output*

Uniform random sampling of **inputs** is not enough, because the interesting
region is usually a thin slice of the input space.

On `champagne-tower`, 34 uniformly-sampled inputs produced **zero** partially-filled
glasses — every answer was exactly `0.0` or `1.0`, and the bug (which only shows on
a partial fill) survived all 34. The partial band is ~1% of the input space.

So: **bucket candidates by the shape of the canonical's output and fill a quota per
bucket.** Cheap to do — draw, classify, keep if that bucket isn't full:

```python
cls = classify(expected)          # e.g. "zero" / "one" / "fractional"
if got[cls] >= QUOTA[cls]:
    continue
```

Sensible generic buckets: empty vs non-empty result, zero / boundary / interior
value, "not found" sentinel vs found, min vs max of the output range, short vs long
returned list. Per-problem overrides where a generic bucket makes no sense.

Input-side spread still matters (small/large `n`, log-uniform magnitudes, edge
shapes), but it is in service of output spread, not a goal of its own.

## Two correctness traps to respect

- **Exact float comparison.** The judge compares with `==` after a JSON round-trip
  (`app/executor/__init__.py`, `_equal`). For float-returning problems, an input
  whose answer is not bit-stable across mathematically-equivalent implementations
  will fail *correct* solutions. Cheap guard: compute the answer a second way
  (different association/order) and skip the input if the two doubles differ.
  On `champagne-tower` this rejected ~0.3% of candidates.

- **Semantic preconditions.** `validate_input` checks the input's *ranges*; it
  never checks what the statement promises about the *answer* — "exactly one
  solution", "all distinct", "guaranteed reachable". On an input that breaks such a
  promise the canonical still returns something plausible, it gets baked as
  `expected`, `verify_bank` passes vacuously, and a *correct* solution is failed.
  This is the reason a bank-wide auto-apply is unsafe. Either add a per-problem
  `well_posed(...)` predicate alongside `validate_input`, or keep a human in the
  loop on `--apply`. See `docs/input-validators.md` § "Semantic preconditions".

## Sketch of the tool

One script, no engine, no agent:

```
scripts/random_cases.py <slug> -n 40 [--apply]
```

- Loads the problem from either content root, plus its validator and canonical.
- Samples inputs from the param types + parsed constraint bounds; rejects anything
  `validate_input` refuses.
- Runs the canonical through the normal `run_submission` path (sandboxed, same as
  grading) to get `expected`.
- Stratifies by output bucket; dedupes against stored cases.
- Dry-run prints the proposed cases and the output distribution; `--apply` appends
  them as hidden cases and re-runs `verify_bank` + `check_constraint_validators`.

Add cases; never delete or rewrite existing ones.

After applying anywhere, `scripts/recheck_solutions.py check <user>` shows which
previously-accepted user solutions now fail — that is the intended signal, but a
*correct* solution appearing there means one of the two traps above bit.

## Why the old one went

It was ~2,400 LOC (coverage tokens, AST mutants, an LLM candidate-solution
population, greedy set-cover, shrinking, an hourly cron sweep driving a subagent)
and it had **already swept `champagne-tower`** — the two `gen-*` cases in that
suite are its output. It still missed a one-line bug that 36 random samples caught
immediately, because it optimised for a coverage metric rather than for exploring
the output space.

Keep the replacement small enough that its failure modes are obvious.
