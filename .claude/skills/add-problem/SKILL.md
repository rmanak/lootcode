---
name: add-problem
description: Scaffold one new coding problem (statement, tests, starter, and a verified canonical solution) per the project's authoring specs, then verify it. Use when asked to add, create, or generate a single coding problem or exercise.
argument-hint: <problem-slug> [difficulty]
arguments: [slug, difficulty]
---

Create a new problem at `content/problems/$slug/` (difficulty `$difficulty` —
default `easy` if none was given).

Follow **both** specs and mirror `content/problems/two-sum/`:

- `specs/problem-authoring-guidelines.md` — the quality bar and the owner's
  house rules (read the Custom requirements section too).
- `specs/problem-schema.md` — the on-disk format.

Generate:

- `problem.md` — statement, `## Constraints`, and 2–3 worked examples.
- `meta.json` — slug `$slug`, difficulty, tags (use the `canonical-tags` skill —
  canonical vocabulary only), function signature, time/memory limits, scoring,
  and a `compare` mode that matches what the statement promises about answer order.
- `tests/cases.json` — a few visible and several hidden cases, including edge and
  large inputs (per the guidelines).
- `starters/python/solution.py` — signature + docstring stub, no logic.
- `solution/solution.py` — a complete reference solution (standard library only)
  that passes every case within the limits.

Then verify — don't report success until both are green:

```
python scripts/seed.py     # canonical solution passes all its tests
python scripts/audit.py    # statement <-> compare <-> fairness consistent
```

If the problem idea behind `$slug` is unclear, ask before generating. For a whole
themed batch, use `/new-problem-set` instead.
