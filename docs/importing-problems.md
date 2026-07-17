# Importing generated problems in bulk

`scripts/import_generated_problems.py` validates and bulk-imports a **staging
folder** of fully-generated problems into the bank in one shot. It is the safe,
repeatable path for adding many problems at once: it runs every guardrail the
project already has and **imports only the problems that pass all of them**, so
you can run it unattended without risking a broken or unfair problem entering the
bank. Both problem kinds are supported — `kind="function"` (one top-level
function) and `kind="class"` (a stateful "design" problem).

```bash
python scripts/import_generated_problems.py <src> --dry-run   # validate + report, write nothing (do this first)
python scripts/import_generated_problems.py <src>             # validate, then prompt before importing
```

## Input layout

One **colocated** directory per problem, keyed by `<slug>`:

```
<src>/
├── <slug>/meta.json                   # the statement source: "title" + "body" (Markdown)
├── <slug>/generated_full_problem.json # the runnable "core" (see below)
└── <slug>/assets/…                    # OPTIONAL: figures (jpg/png/gif/svg) the body references
```

**Title and body come from `meta.json`; everything the judge needs comes from
`generated_full_problem.json`.** Where the two disagree on `tags`/`difficulty` by
design, the generated core wins — it is what was verified. `problem.md` is
assembled as `# <title>` + `body`.

`generated_full_problem.json` is exactly the LLM **core contract**
(`specs/problem-schema.md`, `docs/problem-generation.md`) — the same shape
`scripts/test_llm_output.py` validates and the Mode-A generator emits. A function
problem:

```jsonc
{
  "kind": "function",                  // optional; defaults to "function"
  "difficulty": "medium",              // easy | medium | hard
  "tags": ["array", "two-pointers"],
  "function_name": "fourSum",
  "params": [{ "name": "nums", "type": "int[]" }, { "name": "target", "type": "int" }],
  "return_type": "int[][]",
  "compare": "set_of_lists",           // exact | unordered | set_of_lists
  "starter_code": "def fourSum(nums, target):\n    ...",
  "canonical_solution": "def fourSum(nums, target):\n    ...",
  "tests": [{ "name": "...", "input": {...}, "expected": ..., "weight": 1, "hidden": false }],
  "hints": ["...", "..."]              // OPTIONAL, up to 3
}
```

A **class** (design) problem instead carries `"kind": "class"`, `class_name`, and
`class_methods` (constructor params in `params`), and its test inputs are
`{operations, args}` replayed against one instance (see `docs/design-problems.md`).

## What it checks (reuses existing gates — nothing re-implemented)

Per slug, cheapest → most expensive, stopping at the first failure so untrusted
code never runs for an already-broken problem:

1. **Presence & slug** — both JSON files exist and are valid, non-empty `title`
   and `body`, kebab-case slug.
2. **Structural** — `scripts/test_llm_output.py` (strict pydantic + AST):
   kind-aware required fields present and well-typed, valid identifiers, starter/
   canonical parse and define the declared signature, each test's `input` keys
   equal the params (or `{operations, args}` for a class), `expected` shape
   matches `compare`, hints cap, JSON-serializable values.
3. **Slug collision** — see *Duplicate detection* below.
4. **Behavioral** — the canonical solution must pass **all** its own tests in the
   real sandbox (`app.executor.run_submission`, via `scripts/audit.py`).
5. **Statement ↔ judge consistency** — `scripts/audit.py`: a statement promising
   "any order" must not use `compare=exact`, and for relaxed modes a deliberately
   re-ordered valid answer must still be accepted (fairness — skipped for class
   problems, which are always `compare=exact`).

Only slugs that clear **all** of these qualify. The script prints a report, asks
to confirm (unless `-y`), then imports each qualifying problem the durable way:
writes `<out>/<slug>/` (the human-editable mirror — default
`content/problems-extended/`), copies binary figures, reloads it from disk,
upserts the DB, and **re-verifies once more from the DB** (the same round-trip
`scripts/seed.py` uses).

## Target root

The default `--out` is `content/problems-extended/` — the gitignored **extended**
set (design/class batches go here). Pass `--out content/problems` for problems
destined for the committed default set. Either way the importer writes the on-disk
mirror **and** upserts the DB, so no separate `seed.py` run is needed to make the
imported problems live (though seeding again is harmless).

## Tags (advisory — never block an import)

Non-canonical tags do not disqualify a problem. On write, `app/tags.py`'s
`normalize_tags` folds known aliases (e.g. `bfs` → `breadth-first-search`) and
drops meta-tags. A tag that is **neither canonical nor a known alias** is *not*
folded — it persists on disk as-is, and the importer reports it as a warning:

```
. warn: non-canonical tag(s) ['interval'] not in vocabulary — will persist as-is (see specs/tags.md)
```

Fix these after import by editing the tag, or by folding it into the canonical
vocabulary in `app/tags.py` / `specs/tags.md` (don't invent tags inline — see the
`canonical-tags` skill).

## Hints (optional)

`generated_full_problem.json` may include a `hints` array (a first-class field of
the core contract). It is normalized (`content.normalize_hints`: trims blanks,
**caps at 3**) and written into `meta.json`. No `hints` key ⇒ the problem simply
has none. The `hints` column in the report shows how many were picked up.

## Figures

Bodies reference images with relative markdown `![alt](assets/<file>)`. On import
the files in `<slug>/assets/` are copied (binary-safe) into `<out>/<slug>/assets/`
and the refs are rewritten to the served URL `/problems/<slug>/assets/<file>` —
the convention existing problems use (`docs/problem-images.md`). A referenced file
that's missing is warned about (soft).

## Duplicate detection

Slugs are **unique bank-wide** (the DB keys on them and seeding loads every
content root), so an exact slug collision is the cheapest, most concrete signal of
a genuine duplicate. The importer distinguishes two cases:

- **Another content root or the DB** already has the slug → a hard **skip**;
  `--overwrite` cannot resolve it (removing the target dir wouldn't remove the
  other copy). Reconcile manually (rename, or decide which copy wins) first.

  ```
  -> slug already exists in problems (unique bank-wide) — reconcile manually; --overwrite cannot resolve a cross-root hit
  ```

- **The target root** already has the slug → skipped as a possible duplicate
  unless you pass `--overwrite` to replace it deliberately.

Broader **near-duplicate** detection (a rephrasing under a *different* slug) is
designed but not built (`docs/duplicate-detection-plan.md`, status: proposed).
When `app/dedup.py` lands, add it as a gate right after the slug-collision check.

## Flags & exit status

| flag | effect |
|------|--------|
| `--out <dir>` | content root to write into (default `content/problems-extended/`) |
| `--slug <slug>` | validate/import only this one slug |
| `--dry-run` | run every check and print the report, but write/import nothing |
| `-y`, `--yes` | skip the confirmation prompt (import everything that qualifies) |
| `--overwrite` | deliberately replace a problem whose slug already exists in the target root |
| `--strict` | treat structural **warnings** as disqualifying too |
| `-v`, `--verbose` | print per-test / per-error detail under each row |

Exit `0` only when the run is clean — everything qualified and (unless
`--dry-run`) imported. Exit `1` if any slug was skipped or an import failed to
re-verify (so a scripted/CI caller notices), and `2` on a usage/layout error.
Note: a run that successfully imports 75 of 95 still exits `1` because 20 were
skipped — read the printed summary, not just the code.

## Automation

The **`generated-problem-import` agent** drives the whole loop for a new batch:
dry-run → triage skips/failures → hand `XX N/M tests` canonical failures to the
**`design-problem-repair`** agent (for class problems) → re-run → import. See
`docs/design-problems.md` for the class-problem model.
