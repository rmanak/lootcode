---
name: bulk-import
description: Import a batch of coding problems from a source file (a pasted/exported problem set) into the lootcode bank — triage, clean up plain-text damage, decide and generate figures, author, and verify. Use when asked to bulk-import, batch-add, or ingest problems from a text/markdown/source file.
argument-hint: <path-to-source-file> [difficulty: easy|medium|hard|mixed]
---

Import the problems in the source file named by **$ARGUMENTS** into the bank.

This is the **batch-ingest** path (cf. `/new-problem-set`, which authors from a
theme). The source is usually pasted/exported prose, so it arrives with formatting
damage and missing figures — this skill formalizes the cleanup and the
figure-generation that every such import needs. Every problem must still satisfy
both specs — read them first and treat them as binding:

- `specs/problem-authoring-guidelines.md` — quality bar + owner's house rules.
- `specs/problem-schema.md` — the on-disk format. Mirror `content/problems/two-sum/`.
- `docs/problem-images.md` — when a figure is warranted, how to generate it (SVG),
  and how to store/serve it. **The single source of truth for images.**

> First time on a fresh request, **write a short plan to a markdown file for review
> before executing** (e.g. `bulk-import.md`): the triage table, the cleanup list,
> the figure decisions, and any problems that don't fit the contract. Execute only
> after the owner approves.

## Procedure

1. **Triage every entry** into a table — `title → add | skip(reason)`:
   - **Duplicate?** Skip if the slug/title already exists in `content/problems/`
     or `scripts/build_bank.py`.
   - **Fits the solver contract?** The harness calls **one top-level function**
     once as `fn(**input)`. Skip or reframe anything that needs a class, multiple
     entry points, or stateful round-trips (e.g. serialize/deserialize, "design a
     data structure", interactive problems). Flag these for an owner decision
     rather than forcing a bad fit.
   - **Difficulty/tags** honest; tag from the canonical vocabulary only (use the
     `canonical-tags` skill — if a problem fits none, stop and discuss, don't invent).

2. **Clean up plain-text damage** before authoring (this is expected on every
   import — see [the memory on import cleanup]):
   - **Collapsed exponents/subscripts:** `105`→`10^5`, `104`→`10^4`, `109`→`10^9`,
     `231 - 1`→`2^31 - 1`, `5 * 104`→`5 * 10^4`. Match the bank's `10^k` / `2^31`
     style. Sanity-check the *value* (`10^5 = 100000`), don't just reformat blindly.
   - Smart quotes/unicode, broken tables, and merged words ("Example1:").
   - Contradictory or garbled wording — restate cleanly, preserving the intent and
     keeping every worked example valid.

3. **Decide figures, then generate them** — follow `docs/problem-images.md`:
   - Apply the **decision rubric**: generate a figure only when the data is
     structural/spatial (grid/matrix, tree, graph, geometry, number-line intervals,
     or a multi-step transformation) **and** a first-time reader grasps the mapping
     faster from a picture than from the prose examples. A figure in the *original*
     source is a strong signal one belongs (watch for a blank gap before `Input:`).
     Skip it for scalars/flat lists that the examples already make obvious.
   - Generate as **hand-written SVG** (no dependencies), one file per example,
     stored at `content/problems/<slug>/assets/<name>.svg`, referenced from
     `problem.md` as `![Example N …](/problems/<slug>/assets/<name>.svg)`. The
     `/problems/{slug}/assets/{filename}` route serves them safely.

4. **Pick representation conventions** for non-flat I/O (keep everything
   JSON-serializable; the canonical rebuilds structures internally):
   - Trees / linked lists → LeetCode level-order arrays with `null`/`None`.
   - Choose the **`compare` mode** that matches what the statement promises about
     order — "any order"/"any valid answer" must **not** be `exact`.

5. **Author** each kept problem in `scripts/build_bank.py` (the bank's discipline):
   a canonical solution, expected outputs **computed by running the canonical**
   (never hand-typed), cross-checked by a brute force and/or known answers, with a
   few visible + several hidden cases (smallest input, every constraint boundary,
   negatives/zero/dupes/ties, and ≥1 large input). Then `python scripts/build_bank.py`
   writes the `content/problems/<slug>/` dirs (and `assets/`).

6. **Verify — do not report success until all are green:**
   ```
   python scripts/seed.py     # every canonical passes ALL its tests
   python scripts/audit.py    # statement <-> compare <-> fairness consistent
   python -m pytest -q        # full suite, incl. executor + asset-route tests
   ```
   Fix anything flagged and re-run until clean. Spot-check one figure-bearing
   problem in the running app to confirm the image renders.

7. **Report** a table of added vs. skipped (with reasons), figures generated, and
   the final seed/audit/pytest status.

Any new image plumbing is a file-serving path → keep it path-traversal-safe and
restricted to `assets/` (never expose `solution/` or hidden `tests/`); review per
`docs/security.md`. If a guideline and a specific source entry conflict, follow the
guideline and say so.
