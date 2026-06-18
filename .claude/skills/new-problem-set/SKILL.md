---
name: new-problem-set
description: Author a themed batch of new coding problems end-to-end — statement, tests, starter, and a verified canonical solution — following the project's authoring specs. Use when asked to create, generate, or add multiple coding problems, a problem set, or several exercises on a topic or theme.
argument-hint: "<theme | path-to-ideas-file> [count=3] [difficulty: easy|medium|hard|mixed]"
---

Author a **set** of new problems from this request: **$ARGUMENTS**

Interpret the request as a theme (or a path to an ideas file), with an optional
problem count (default 3) and an optional difficulty (default: a mix).

This is the batch version of `/add-problem`. Every problem must satisfy the same
two specs — read both first and treat them as binding:

- `specs/problem-authoring-guidelines.md` — the quality bar and house rules
  (**including the owner's Custom requirements** — do not skip them).
- `specs/problem-schema.md` — the on-disk format. Mirror `content/problems/two-sum/`.

## Procedure

1. **Plan the set.** Propose the problems (default 3 unless a count was given) as
   `slug — title (difficulty) — one-line idea`, varying topics and, for a mixed
   set, difficulty. If the request points to a file, read it for ideas. If the
   theme or count is ambiguous, ask before generating; otherwise proceed.

2. **Author each problem** under `content/problems/<slug>/` with all five pieces:
   `problem.md`, `meta.json`, `tests/cases.json`, `starters/python/solution.py`,
   and `solution/solution.py`. For non-trivial authoring, delegate to the
   `problem-author` subagent (it loads the same specs).
   - Pick the `compare` mode that matches what the statement promises about order.
   - Include hidden edge cases and at least one large input per the guidelines.
   - Tag from the canonical vocabulary only (use the `canonical-tags` skill);
     keep difficulty honest; standard library only.

3. **Verify the whole set** — do not report success until both are green:
   ```
   python scripts/seed.py     # every canonical solution passes all its tests
   python scripts/audit.py    # statement <-> compare <-> fairness consistent
   ```
   Fix anything the scripts flag (wrong expected, mismatched compare mode, "any
   order" prose with compare=exact, etc.) and re-run until clean.

4. **Report** a table of the new slugs with difficulty, tags, compare mode, and
   test counts (visible/hidden), plus the final seed/audit status.

If a guideline and a specific idea conflict, follow the guideline and say so.
